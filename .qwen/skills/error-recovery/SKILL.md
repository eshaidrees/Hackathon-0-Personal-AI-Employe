# Error Recovery Skill

## Purpose
Error recovery and graceful degradation system for AI Employee. Provides retry logic, circuit breaker pattern, error quarantine, and system health monitoring.

## Capabilities
- Retry logic with exponential backoff
- Circuit breaker pattern for fault tolerance
- Graceful degradation with fallbacks
- Error quarantine for later review
- Recovery plan generation
- System health monitoring
- Automatic error cleanup

## Files
- `scripts/error_recovery.py` - Main error recovery implementation

## Usage

### Check System Health
```bash
# View system health status
python scripts/error_recovery.py --vault ../AI_Employee_Vault health
```

### Cleanup Old Errors
```bash
# Remove errors older than 30 days
python scripts/error_recovery.py --vault ../AI_Employee_Vault cleanup --days 30
```

### Demo Mode
```bash
# Test error recovery features
python scripts/error_recovery.py --vault ../AI_Employee_Vault demo
```

### Quarantine Error
```bash
# Quarantine an error for review
python scripts/error_recovery.py --vault ../AI_Employee_Vault quarantine
```

## Python API

### Retry with Exponential Backoff

```python
from error_recovery import ErrorRecovery, RetryConfig, TransientError

recovery = ErrorRecovery(vault_path='../AI_Employee_Vault')

# Configure retry
config = RetryConfig(
    max_attempts=3,
    base_delay=1.0,      # Start with 1 second
    max_delay=60.0,      # Max 60 seconds between attempts
    exponential_base=2.0, # Double delay each attempt
    jitter=True          # Add randomness to prevent thundering herd
)

# Execute with retry
def send_email():
    # Your code that might fail
    pass

try:
    result = recovery.with_retry(
        func=send_email,
        retry_config=config,
        retryable_exceptions=(TransientError,),
        on_retry=lambda attempt, error, delay: print(f'Retry {attempt}: {error}'),
        operation_name='send_email'
    )
except Exception as e:
    print(f'All retries exhausted: {e}')
```

### Circuit Breaker Pattern

```python
from error_recovery import ErrorRecovery, CriticalError

recovery = ErrorRecovery(vault_path='../AI_Employee_Vault')

def call_external_api():
    # Code that might fail repeatedly
    pass

try:
    result = recovery.with_circuit_breaker(
        func=call_external_api,
        operation_name='external_api_call',
        failure_threshold=5,      # Open after 5 failures
        recovery_timeout=60       # Try again after 60 seconds
    )
except CriticalError as e:
    print(f'Circuit breaker open: {e}')
```

### Graceful Degradation

```python
from error_recovery import ErrorRecovery

recovery = ErrorRecovery(vault_path='../AI_Employee_Vault')

def primary_operation():
    # Primary implementation
    pass

def fallback_operation():
    # Fallback implementation
    pass

result = recovery.graceful_degradation(
    primary_func=primary_operation,
    fallback_func=fallback_operation,
    operation_name='data_fetch'
)

# If primary fails and no fallback, returns None
result = recovery.graceful_degradation(
    primary_func=primary_operation,
    operation_name='optional_feature'
)
```

### Error Quarantine

```python
from error_recovery import ErrorRecovery
from pathlib import Path

recovery = ErrorRecovery(vault_path='../AI_Employee_Vault')

# Quarantine an error
error_file = recovery.quarantine_error(
    error_type='authentication_failure',
    error_context={
        'service': 'gmail',
        'user': 'user@example.com',
        'error_code': 'AUTH_FAILED'
    },
    original_file=Path('Needs_Action/EMAIL_123.md')
)
print(f'Error quarantined to: {error_file}')
```

### Recovery Plan Generation

```python
from error_recovery import ErrorRecovery

recovery = ErrorRecovery(vault_path='../AI_Employee_Vault')

# Create recovery plan
plan_file = recovery.create_recovery_plan(
    error_type='network_timeout',
    error_context={
        'service': 'odoo',
        'url': 'http://localhost:8069',
        'timeout': 30
    }
)
print(f'Recovery plan created: {plan_file}')
```

### System Health Check

```python
from error_recovery import ErrorRecovery

recovery = ErrorRecovery(vault_path='../AI_Employee_Vault')

health = recovery.get_system_health()
print(f"Status: {health['status']}")
print(f"Circuit Breakers: {health['circuit_breakers']}")
print(f"Recent Errors: {len(health['recent_errors'])}")
```

## Configuration

### Environment Variables
```bash
# Enable circuit breaker
CIRCUIT_BREAKER_ENABLED=true

# Failure threshold before opening circuit
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5

# Recovery timeout in seconds
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60

# Dry run mode
DRY_RUN=true
```

## Error Types

### TransientError
Temporary errors that should be retried:
- Network timeouts
- Rate limiting
- Temporary service unavailability

### CriticalError
Serious errors requiring intervention:
- Authentication failures
- Circuit breaker open
- Data corruption

## Circuit Breaker States

| State | Description | Behavior |
|-------|-------------|----------|
| CLOSED | Normal operation | All requests allowed |
| OPEN | Too many failures | All requests blocked |
| HALF-OPEN | Testing recovery | Limited requests allowed |

## Recovery Steps by Error Type

### Authentication Errors
1. Check credential validity
2. Refresh tokens if expired
3. Verify API keys are correct
4. Check service status
5. Re-authenticate if necessary

### Network Errors
1. Check network connectivity
2. Verify service is reachable
3. Check firewall rules
4. Retry operation
5. Escalate if persistent

### Timeout Errors
1. Check service response time
2. Increase timeout if appropriate
3. Retry with exponential backoff
4. Check for service degradation

### Permission Errors
1. Verify user permissions
2. Check resource access rights
3. Request elevated permissions
4. Contact administrator

## Error Quarantine Format

```markdown
---
type: error_quarantine
error_type: authentication_failure
timestamp: 2026-03-14T10:30:00
status: pending_review
---

# Error Quarantine: authentication_failure

## Error Details
```json
{
  "service": "gmail",
  "user": "user@example.com",
  "error_code": "AUTH_FAILED"
}
```

## Original File
EMAIL_123.md

## Investigation Notes
<!-- Add investigation notes here -->

## Resolution
<!-- Add resolution steps here -->
```

## Recovery Plan Format

```markdown
---
type: recovery_plan
error_type: network_timeout
created: 2026-03-14T10:30:00
status: pending
priority: medium
---

# Recovery Plan: network_timeout

## Error Context
```json
{
  "service": "odoo",
  "url": "http://localhost:8069",
  "timeout": 30
}
```

## Recovery Steps
1. Check network connectivity
2. Verify service is reachable
3. Check firewall rules
4. Retry operation
5. Escalate if persistent

## Verification
- [ ] Error no longer occurs
- [ ] System functioning normally
- [ ] Logs reviewed and cleared

## Notes
<!-- Add additional notes here -->
```

## Health Check Output

```
System Health Status: HEALTHY
Timestamp: 2026-03-14T10:30:00

Circuit Breakers:
  send_email: closed (errors: 0)
  odoo_call: half-open (errors: 3)
  post_linkedin: open (errors: 5)

Recent Errors: 3
  - email_send: Connection timeout
  - odoo_create: Authentication failed
  - post_twitter: Rate limited
```

## Troubleshooting

### Circuit Breaker Open
- Check error counts for the operation
- Review recent errors in logs
- Fix underlying issue before reset
- Wait for recovery timeout

### Too Many Retries
- Increase max_attempts if appropriate
- Check if error is truly transient
- Consider increasing delays
- Review error type classification

### Error Quarantine Full
- Review and resolve quarantined errors
- Run cleanup to remove old errors
- Address root causes

---

*Skill Version: 1.0*
*AI Employee v0.3 - Gold Tier*
