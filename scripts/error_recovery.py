"""
Error Recovery and Graceful Degradation System
Handles retries, fallbacks, and system recovery for AI Employee
"""
import os
import sys
import json
import time
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Callable, Any, Optional, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RetryConfig:
    """Configuration for retry behavior."""
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0,
                 max_delay: float = 60.0, exponential_base: float = 2.0,
                 jitter: bool = True):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


class TransientError(Exception):
    """Transient error that should be retried."""
    pass


class CriticalError(Exception):
    """Critical error that requires human intervention."""
    pass


class ErrorRecovery:
    """
    Error recovery and graceful degradation system.
    Provides retry logic, fallbacks, and system health monitoring.
    """

    def __init__(self, vault_path: str):
        """
        Initialize Error Recovery system.

        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path).resolve()
        self.logs_dir = self.vault_path / 'Logs'
        self.errors_dir = self.logs_dir / 'errors'
        self.recovery_dir = self.logs_dir / 'recovery'

        # Ensure directories exist
        for dir_path in [self.logs_dir, self.errors_dir, self.recovery_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.default_retry_config = RetryConfig()
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'

        # Error tracking
        self.error_counts: Dict[str, int] = {}
        self.last_error_time: Dict[str, datetime] = {}
        self.circuit_breaker_state: Dict[str, str] = {}  # closed/open/half-open

        import logging
        self.logger = logging.getLogger('ErrorRecovery')

    def with_retry(self, func: Callable, retry_config: Optional[RetryConfig] = None,
                   retryable_exceptions: tuple = (TransientError,),
                   on_retry: Optional[Callable] = None,
                   operation_name: str = None) -> Any:
        """
        Execute a function with retry logic.

        Args:
            func: Function to execute
            retry_config: Retry configuration
            retryable_exceptions: Tuple of exceptions that should be retried
            on_retry: Callback function called on each retry
            operation_name: Name of operation for logging

        Returns:
            Function result

        Raises:
            Last exception if all retries fail
        """
        config = retry_config or self.default_retry_config
        operation_name = operation_name or func.__name__
        last_exception = None

        for attempt in range(1, config.max_attempts + 1):
            try:
                return func()
            except retryable_exceptions as e:
                last_exception = e
                
                if attempt < config.max_attempts:
                    # Calculate delay with exponential backoff
                    delay = min(
                        config.base_delay * (config.exponential_base ** (attempt - 1)),
                        config.max_delay
                    )
                    
                    # Add jitter if configured
                    if config.jitter:
                        delay = delay * (0.5 + random.random())

                    self.logger.warning(
                        f'{operation_name} attempt {attempt} failed: {e}. '
                        f'Retrying in {delay:.1f}s...'
                    )

                    # Call retry callback if provided
                    if on_retry:
                        on_retry(attempt, e, delay)

                    time.sleep(delay)
                else:
                    self.logger.error(f'{operation_name} failed after {config.max_attempts} attempts')
            
            except Exception as e:
                # Non-retryable error
                self.logger.error(f'{operation_name} failed with non-retryable error: {e}')
                raise

        # All retries exhausted
        if last_exception:
            raise last_exception

    def with_circuit_breaker(self, func: Callable, operation_name: str = None,
                            failure_threshold: int = 5, 
                            recovery_timeout: int = 60) -> Any:
        """
        Execute a function with circuit breaker pattern.

        Args:
            func: Function to execute
            operation_name: Name of operation
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying again

        Returns:
            Function result

        Raises:
            CriticalError if circuit is open
        """
        operation_name = operation_name or func.__name__
        now = datetime.now()

        # Get current circuit state
        state = self.circuit_breaker_state.get(operation_name, 'closed')

        if state == 'open':
            # Check if recovery timeout has passed
            last_error = self.last_error_time.get(operation_name)
            if last_error and (now - last_error).total_seconds() > recovery_timeout:
                self.logger.info(f'Circuit breaker for {operation_name} entering half-open state')
                self.circuit_breaker_state[operation_name] = 'half-open'
            else:
                raise CriticalError(f'Circuit breaker open for {operation_name}')

        try:
            result = func()
            
            # Success - reset circuit
            if self.circuit_breaker_state.get(operation_name) == 'half-open':
                self.logger.info(f'Circuit breaker for {operation_name} closed after successful operation')
            self.circuit_breaker_state[operation_name] = 'closed'
            self.error_counts[operation_name] = 0
            
            return result

        except Exception as e:
            # Record failure
            self.error_counts[operation_name] = self.error_counts.get(operation_name, 0) + 1
            self.last_error_time[operation_name] = now

            # Check if threshold exceeded
            if self.error_counts[operation_name] >= failure_threshold:
                self.logger.error(f'Circuit breaker for {operation_name} opened after {failure_threshold} failures')
                self.circuit_breaker_state[operation_name] = 'open'

            raise

    def graceful_degradation(self, primary_func: Callable, 
                             fallback_func: Optional[Callable] = None,
                             operation_name: str = None) -> Any:
        """
        Execute primary function with fallback on failure.

        Args:
            primary_func: Primary function to try
            fallback_func: Fallback function if primary fails
            operation_name: Name of operation

        Returns:
            Result from primary or fallback function
        """
        operation_name = operation_name or primary_func.__name__

        try:
            return primary_func()
        except Exception as e:
            self.logger.warning(f'{operation_name} failed: {e}')

            if fallback_func:
                self.logger.info(f'Executing fallback for {operation_name}')
                try:
                    return fallback_func()
                except Exception as fallback_error:
                    self.logger.error(f'Fallback also failed for {operation_name}: {fallback_error}')
                    raise
            else:
                # No fallback - return default based on expected return type
                self.logger.info(f'No fallback configured for {operation_name}, returning default')
                return None

    def quarantine_error(self, error_type: str, error_context: dict,
                         original_file: Optional[Path] = None) -> Path:
        """
        Quarantine an error for later review.

        Args:
            error_type: Type of error
            error_context: Error context/details
            original_file: Original file that caused error (if applicable)

        Returns:
            Path to quarantined error file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ERROR_{error_type}_{timestamp}.md"
        error_file = self.errors_dir / filename

        content = f'''---
type: error_quarantine
error_type: {error_type}
timestamp: {datetime.now().isoformat()}
status: pending_review
---

# Error Quarantine: {error_type}

## Error Details
```json
{json.dumps(error_context, indent=2)}
```

## Original File
{original_file.name if original_file else 'N/A'}

## Investigation Notes
<!-- Add investigation notes here -->

## Resolution
<!-- Add resolution steps here -->

---
*Created by Error Recovery System - AI Employee v0.3*
'''

        error_file.write_text(content, encoding='utf-8')

        # Move original file if provided
        if original_file and original_file.exists():
            quarantine_path = self.errors_dir / f'ORIGINAL_{original_file.name}'
            try:
                original_file.rename(quarantine_path)
            except Exception as e:
                self.logger.warning(f'Could not quarantine original file: {e}')

        self.logger.info(f'Error quarantined: {filename}')
        return error_file

    def create_recovery_plan(self, error_type: str, error_context: dict) -> Path:
        """
        Create a recovery plan for addressing an error.

        Args:
            error_type: Type of error
            error_context: Error context

        Returns:
            Path to recovery plan file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"RECOVERY_{error_type}_{timestamp}.md"
        recovery_file = self.recovery_dir / filename

        # Generate recovery steps based on error type
        recovery_steps = self._generate_recovery_steps(error_type, error_context)

        content = f'''---
type: recovery_plan
error_type: {error_type}
created: {datetime.now().isoformat()}
status: pending
priority: {self._get_priority(error_type)}
---

# Recovery Plan: {error_type}

## Error Context
```json
{json.dumps(error_context, indent=2)}
```

## Recovery Steps
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(recovery_steps))}

## Verification
- [ ] Error no longer occurs
- [ ] System functioning normally
- [ ] Logs reviewed and cleared

## Notes
<!-- Add additional notes here -->

---
*Created by Error Recovery System - AI Employee v0.3*
'''

        recovery_file.write_text(content, encoding='utf-8')
        self.logger.info(f'Recovery plan created: {filename}')
        return recovery_file

    def _generate_recovery_steps(self, error_type: str, context: dict) -> list:
        """Generate recovery steps based on error type."""
        steps = []

        if 'authentication' in error_type.lower() or 'auth' in error_type.lower():
            steps = [
                'Check credential validity',
                'Refresh tokens if expired',
                'Verify API keys are correct',
                'Check service status',
                'Re-authenticate if necessary'
            ]
        elif 'network' in error_type.lower() or 'connection' in error_type.lower():
            steps = [
                'Check network connectivity',
                'Verify service is reachable',
                'Check firewall rules',
                'Retry operation',
                'Escalate if persistent'
            ]
        elif 'timeout' in error_type.lower():
            steps = [
                'Check service response time',
                'Increase timeout if appropriate',
                'Retry with exponential backoff',
                'Check for service degradation'
            ]
        elif 'permission' in error_type.lower() or 'access' in error_type.lower():
            steps = [
                'Verify user permissions',
                'Check resource access rights',
                'Request elevated permissions if needed',
                'Contact administrator'
            ]
        else:
            steps = [
                'Review error logs',
                'Identify root cause',
                'Implement fix',
                'Test resolution',
                'Monitor for recurrence'
            ]

        return steps

    def _get_priority(self, error_type: str) -> str:
        """Get priority level for error type."""
        high_priority = ['authentication', 'payment', 'data_loss', 'security']
        medium_priority = ['network', 'timeout', 'rate_limit']
        
        error_type_lower = error_type.lower()
        
        if any(p in error_type_lower for p in high_priority):
            return 'high'
        elif any(p in error_type_lower for p in medium_priority):
            return 'medium'
        else:
            return 'low'

    def get_system_health(self) -> dict:
        """
        Get overall system health status.

        Returns:
            Health status dict
        """
        health = {
            'status': 'healthy',
            'circuit_breakers': {},
            'recent_errors': [],
            'timestamp': datetime.now().isoformat()
        }

        # Check circuit breakers
        for operation, state in self.circuit_breaker_state.items():
            health['circuit_breakers'][operation] = {
                'state': state,
                'error_count': self.error_counts.get(operation, 0)
            }
            if state == 'open':
                health['status'] = 'degraded'
            elif state == 'half-open':
                if health['status'] == 'healthy':
                    health['status'] = 'recovering'

        # Check for recent errors
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_dir / f'{today}.json'
        
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text(encoding='utf-8'))
                error_logs = [l for l in logs if l.get('result') == 'failure']
                health['recent_errors'] = error_logs[-10:]  # Last 10 errors
                
                if len(error_logs) > 20:
                    health['status'] = 'degraded'
            except:
                pass

        # Count quarantined errors
        error_count = len(list(self.errors_dir.glob('ERROR_*.md')))
        if error_count > 10:
            health['status'] = 'degraded'
            health['quarantined_errors'] = error_count

        return health

    def cleanup_old_errors(self, days: int = 30) -> int:
        """
        Clean up old error files.

        Args:
            days: Remove errors older than this

        Returns:
            Number of files removed
        """
        cutoff = datetime.now() - timedelta(days=days)
        removed = 0

        for error_file in self.errors_dir.glob('*.md'):
            try:
                content = error_file.read_text(encoding='utf-8')
                if 'timestamp:' in content:
                    for line in content.split('\n'):
                        if 'timestamp:' in line:
                            timestamp_str = line.split(':')[1].strip()
                            try:
                                timestamp = datetime.fromisoformat(timestamp_str)
                                if timestamp < cutoff:
                                    error_file.unlink()
                                    removed += 1
                            except:
                                pass
            except Exception as e:
                self.logger.debug(f'Error processing {error_file}: {e}')

        self.logger.info(f'Cleaned up {removed} old error files')
        return removed


# Decorator for easy retry usage
def retry(max_attempts: int = 3, base_delay: float = 1.0,
          retryable_exceptions: tuple = (TransientError,)):
    """Decorator for adding retry logic to functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            recovery = ErrorRecovery('../AI_Employee_Vault')
            config = RetryConfig(max_attempts=max_attempts, base_delay=base_delay)
            return recovery.with_retry(
                lambda: func(*args, **kwargs),
                retry_config=config,
                retryable_exceptions=retryable_exceptions,
                operation_name=func.__name__
            )
        return wrapper
    return decorator


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Error Recovery System')
    parser.add_argument(
        '--vault',
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        'action',
        choices=['health', 'cleanup', 'demo', 'quarantine'],
        help='Action to perform'
    )
    parser.add_argument('--days', type=int, default=30, help='Days for cleanup')

    args = parser.parse_args()

    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()

    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        sys.exit(1)

    recovery = ErrorRecovery(str(vault_path))

    if args.action == 'health':
        health = recovery.get_system_health()
        print(f"System Health Status: {health['status'].upper()}")
        print(f"Timestamp: {health['timestamp']}")
        print(f"\nCircuit Breakers:")
        for op, info in health['circuit_breakers'].items():
            print(f"  {op}: {info['state']} (errors: {info['error_count']})")
        print(f"\nRecent Errors: {len(health['recent_errors'])}")
        for error in health['recent_errors'][-5:]:
            print(f"  - {error.get('action_type', 'unknown')}: {error.get('error', 'unknown')}")

    elif args.action == 'cleanup':
        removed = recovery.cleanup_old_errors(args.days)
        print(f'Removed {removed} old error files')

    elif args.action == 'demo':
        print('Error Recovery Demo Mode')
        
        # Demo retry with transient error
        def failing_function():
            raise TransientError('Simulated transient error')
        
        try:
            recovery.with_retry(
                failing_function,
                retry_config=RetryConfig(max_attempts=3, base_delay=0.5),
                operation_name='demo_retry'
            )
        except Exception as e:
            print(f'Final error after retries: {e}')

        # Demo circuit breaker
        print('\nCircuit Breaker State:', recovery.circuit_breaker_state)

        # Demo health check
        health = recovery.get_system_health()
        print(f'System Health: {health["status"]}')

    elif args.action == 'quarantine':
        # Create demo quarantine
        error_file = recovery.quarantine_error(
            'demo_error',
            {'message': 'This is a demo error', 'code': 500},
            None
        )
        print(f'Error quarantined to: {error_file}')


if __name__ == '__main__':
    main()
