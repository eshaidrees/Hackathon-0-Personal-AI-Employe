"""
Comprehensive Audit Logger
Centralized logging system for all AI Employee actions with retention and query capabilities
"""
import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AuditLogger:
    """
    Comprehensive audit logging for AI Employee.
    Logs all actions with full context for compliance and debugging.
    """

    def __init__(self, vault_path: str, retention_days: int = 90):
        """
        Initialize Audit Logger.

        Args:
            vault_path: Path to the Obsidian vault root
            retention_days: Number of days to retain logs (default: 90)
        """
        self.vault_path = Path(vault_path).resolve()
        self.logs_dir = self.vault_path / 'Logs'
        self.audit_dir = self.logs_dir / 'audit'
        self.retention_days = retention_days

        # Ensure directories exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.audit_dir.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')

        # Daily log file
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.daily_log = self.logs_dir / f'{self.today}.json'

        # Audit trail (append-only)
        self.audit_log = self.audit_dir / 'audit_trail.jsonl'

        import logging
        self.logger = logging.getLogger('AuditLogger')

    def log(self, action_type: str, actor: str, parameters: dict,
            result: str = 'success', error: str = None,
            approval_status: str = 'auto', approved_by: str = None,
            context: dict = None, correlation_id: str = None) -> str:
        """
        Log an action with full audit trail.

        Args:
            action_type: Type of action (email_send, task_complete, etc.)
            actor: Who/what performed the action (orchestrator, gmail_watcher, etc.)
            parameters: Action parameters/details
            result: success/failure/pending
            error: Error message if failed
            approval_status: auto/approved/rejected/pending
            approved_by: Human who approved (if applicable)
            context: Additional context data
            correlation_id: ID to correlate related actions

        Returns:
            Log entry ID
        """
        timestamp = datetime.now()
        
        # Create unique entry ID
        entry_data = f"{timestamp.isoformat()}{action_type}{actor}{json.dumps(parameters, sort_keys=True)}"
        entry_id = hashlib.sha256(entry_data.encode()).hexdigest()[:16]

        # Create log entry
        entry = {
            'entry_id': entry_id,
            'timestamp': timestamp.isoformat(),
            'date': self.today,
            'action_type': action_type,
            'actor': actor,
            'parameters': parameters,
            'result': result,
            'error': error,
            'approval_status': approval_status,
            'approved_by': approved_by,
            'context': context or {},
            'correlation_id': correlation_id or entry_id,
            'system': {
                'dry_run': self.dry_run,
                'log_level': self.log_level,
                'python_version': sys.version,
                'platform': sys.platform
            }
        }

        # Write to daily log
        self._write_daily_log(entry)

        # Write to audit trail (append-only)
        self._write_audit_trail(entry)

        # Log to standard logging
        log_message = f"[{action_type}] {actor} -> {result}"
        if error:
            self.logger.error(f"{log_message} - {error}")
        else:
            self.logger.info(log_message)

        return entry_id

    def _write_daily_log(self, entry: dict):
        """Write entry to daily log file."""
        # Load existing logs
        if self.daily_log.exists():
            try:
                logs = json.loads(self.daily_log.read_text(encoding='utf-8'))
            except:
                logs = []
        else:
            logs = []

        # Append new entry
        logs.append(entry)

        # Save
        self.daily_log.write_text(json.dumps(logs, indent=2), encoding='utf-8')

    def _write_audit_trail(self, entry: dict):
        """Append entry to audit trail (JSONL format)."""
        with open(self.audit_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')

    def query(self, start_date: str = None, end_date: str = None,
              action_type: str = None, actor: str = None,
              result: str = None, correlation_id: str = None) -> List[dict]:
        """
        Query audit logs.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            action_type: Filter by action type
            actor: Filter by actor
            result: Filter by result
            correlation_id: Filter by correlation ID

        Returns:
            List of matching log entries
        """
        results = []

        # Determine which files to search
        if start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            current = start
            files_to_search = []
            while current <= end:
                files_to_search.append(self.logs_dir / f'{current.strftime("%Y-%m-%d")}.json')
                current += timedelta(days=1)
        else:
            # Search last 7 days by default
            files_to_search = []
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                files_to_search.append(self.logs_dir / f'{date}.json')

        # Search files
        for log_file in files_to_search:
            if not log_file.exists():
                continue

            try:
                logs = json.loads(log_file.read_text(encoding='utf-8'))
                for entry in logs:
                    if self._matches_filter(entry, action_type, actor, result, correlation_id):
                        results.append(entry)
            except Exception as e:
                self.logger.debug(f'Error reading {log_file}: {e}')

        # Also search audit trail for older entries
        if self.audit_log.exists():
            try:
                with open(self.audit_log, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            if self._matches_filter(entry, action_type, actor, result, correlation_id):
                                # Check date range if specified
                                if start_date and end_date:
                                    entry_date = entry.get('date', '')
                                    if start_date <= entry_date <= end_date:
                                        results.append(entry)
                                else:
                                    results.append(entry)
                        except:
                            continue
            except Exception as e:
                self.logger.debug(f'Error reading audit trail: {e}')

        return results

    def _matches_filter(self, entry: dict, action_type: str, actor: str,
                        result: str, correlation_id: str) -> bool:
        """Check if entry matches filter criteria."""
        if action_type and entry.get('action_type') != action_type:
            return False
        if actor and entry.get('actor') != actor:
            return False
        if result and entry.get('result') != result:
            return False
        if correlation_id and entry.get('correlation_id') != correlation_id:
            return False
        return True

    def get_statistics(self, days: int = 7) -> dict:
        """
        Get audit log statistics.

        Args:
            days: Number of days to analyze

        Returns:
            Statistics dict
        """
        stats = {
            'total_actions': 0,
            'by_result': {},
            'by_action_type': {},
            'by_actor': {},
            'errors': 0,
            'approvals_required': 0,
            'period': f'{days} days'
        }

        # Query logs
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        entries = self.query(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

        for entry in entries:
            stats['total_actions'] += 1

            # By result
            result = entry.get('result', 'unknown')
            stats['by_result'][result] = stats['by_result'].get(result, 0) + 1

            # By action type
            action_type = entry.get('action_type', 'unknown')
            stats['by_action_type'][action_type] = stats['by_action_type'].get(action_type, 0) + 1

            # By actor
            actor = entry.get('actor', 'unknown')
            stats['by_actor'][actor] = stats['by_actor'].get(actor, 0) + 1

            # Count errors
            if entry.get('error'):
                stats['errors'] += 1

            # Count approvals
            if entry.get('approval_status') in ['approved', 'pending']:
                stats['approvals_required'] += 1

        return stats

    def cleanup_old_logs(self):
        """Remove logs older than retention period."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        removed = 0

        # Clean daily logs
        for log_file in self.logs_dir.glob('*.json'):
            try:
                # Parse date from filename
                date_str = log_file.stem  # YYYY-MM-DD
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                if file_date < cutoff:
                    log_file.unlink()
                    removed += 1
                    self.logger.info(f'Removed old log: {log_file.name}')
            except Exception as e:
                self.logger.debug(f'Error processing {log_file}: {e}')

        self.logger.info(f'Cleanup complete: removed {removed} old log files')
        return removed

    def export_audit_trail(self, output_path: str, format: str = 'json') -> Path:
        """
        Export full audit trail.

        Args:
            output_path: Output file path
            format: Export format (json, csv)

        Returns:
            Path to exported file
        """
        output = Path(output_path)
        entries = []

        # Read audit trail
        if self.audit_log.exists():
            with open(self.audit_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entries.append(json.loads(line))
                    except:
                        continue

        if format == 'json':
            output.write_text(json.dumps(entries, indent=2), encoding='utf-8')
        elif format == 'csv':
            import csv
            if entries:
                keys = entries[0].keys()
                with open(output, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(entries)

        self.logger.info(f'Exported {len(entries)} entries to {output}')
        return output

    def log_error(self, error_type: str, error_message: str, 
                  context: dict = None, actor: str = 'system') -> str:
        """Log an error with full context."""
        return self.log(
            action_type=f'error_{error_type}',
            actor=actor,
            parameters={'error_message': error_message, 'context': context or {}},
            result='failure',
            error=error_message
        )

    def log_action_start(self, action_type: str, actor: str, 
                         parameters: dict) -> str:
        """Log action start."""
        return self.log(
            action_type=action_type,
            actor=actor,
            parameters=parameters,
            result='pending'
        )

    def log_action_complete(self, action_type: str, actor: str,
                           parameters: dict, correlation_id: str) -> str:
        """Log action completion."""
        return self.log(
            action_type=action_type,
            actor=actor,
            parameters=parameters,
            result='success',
            correlation_id=correlation_id
        )

    def log_action_failure(self, action_type: str, actor: str,
                          parameters: dict, error: str, 
                          correlation_id: str) -> str:
        """Log action failure."""
        return self.log(
            action_type=action_type,
            actor=actor,
            parameters=parameters,
            result='failure',
            error=error,
            correlation_id=correlation_id
        )


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger(vault_path: str = None) -> AuditLogger:
    """Get or create global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        if vault_path is None:
            vault_path = os.getenv('VAULT_PATH', '../AI_Employee_Vault')
        _audit_logger = AuditLogger(vault_path)
    return _audit_logger


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Audit Logger')
    parser.add_argument(
        '--vault',
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        'action',
        choices=['stats', 'query', 'cleanup', 'export', 'demo'],
        help='Action to perform'
    )
    parser.add_argument('--days', type=int, default=7, help='Days to query')
    parser.add_argument('--output', help='Output path for export')
    parser.add_argument('--type', help='Action type filter')
    parser.add_argument('--actor', help='Actor filter')
    parser.add_argument('--result', help='Result filter')

    args = parser.parse_args()

    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()

    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        sys.exit(1)

    logger = AuditLogger(str(vault_path))

    if args.action == 'stats':
        stats = logger.get_statistics(args.days)
        print(f"Audit Log Statistics (Last {args.days} Days)")
        print("=" * 50)
        print(f"Total Actions: {stats['total_actions']}")
        print(f"Errors: {stats['errors']}")
        print(f"Approvals Required: {stats['approvals_required']}")
        print("\nBy Result:")
        for result, count in stats['by_result'].items():
            print(f"  {result}: {count}")
        print("\nBy Action Type:")
        for action_type, count in stats['by_action_type'].items():
            print(f"  {action_type}: {count}")
        print("\nBy Actor:")
        for actor, count in stats['by_actor'].items():
            print(f"  {actor}: {count}")

    elif args.action == 'query':
        results = logger.query(
            action_type=args.type,
            actor=args.actor,
            result=args.result
        )
        print(f"Found {len(results)} matching entries")
        for entry in results[:10]:  # Show first 10
            print(f"{entry['timestamp']} | {entry['action_type']} | {entry['actor']} | {entry['result']}")

    elif args.action == 'cleanup':
        removed = logger.cleanup_old_logs()
        print(f'Removed {removed} old log files')

    elif args.action == 'export':
        if not args.output:
            print('Error: --output required for export')
            sys.exit(1)
        path = logger.export_audit_trail(args.output)
        print(f'Exported to {path}')

    elif args.action == 'demo':
        print('Audit Logger Demo Mode')
        print(f'Vault: {vault_path}')
        print(f'Retention: {logger.retention_days} days')

        # Log some demo entries
        logger.log(
            action_type='demo_action',
            actor='audit_logger',
            parameters={'demo': True},
            result='success'
        )
        print('Demo action logged')

        # Show stats
        stats = logger.get_statistics(1)
        print(f"\nToday's stats: {stats['total_actions']} actions")


if __name__ == '__main__':
    main()
