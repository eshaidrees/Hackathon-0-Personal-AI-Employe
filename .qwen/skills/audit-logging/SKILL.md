# Audit Logging Skill

## Purpose
Comprehensive audit logging system for all AI Employee actions with retention management, query capabilities, and export functionality.

## Capabilities
- Log all actions with full context
- Append-only audit trail (JSONL format)
- Daily log files with automatic rotation
- Query logs by date, type, actor, result
- Export to JSON or CSV
- Automatic log retention (90-day default)
- Statistics and reporting
- Error tracking and correlation

## Files
- `scripts/audit_logger.py` - Main audit logging implementation

## Usage

### View Statistics
```bash
# View last 7 days statistics
python scripts/audit_logger.py --vault ../AI_Employee_Vault stats --days 7

# View last 30 days
python scripts/audit_logger.py --vault ../AI_Employee_Vault stats --days 30
```

### Query Logs
```bash
# Query by action type
python scripts/audit_logger.py --vault ../AI_Employee_Vault query --type email_send

# Query by actor
python scripts/audit_logger.py --vault ../AI_Employee_Vault query --actor gmail_watcher

# Query by result
python scripts/audit_logger.py --vault ../AI_Employee_Vault query --result failure

# Combined filters
python scripts/audit_logger.py --vault ../AI_Employee_Vault query --type email_send --result success
```

### Export Audit Trail
```bash
# Export to JSON
python scripts/audit_logger.py --vault ../AI_Employee_Vault export --output audit_export.json

# Export to CSV
python scripts/audit_logger.py --vault ../AI_Employee_Vault export --output audit_export.csv
```

### Cleanup Old Logs
```bash
# Remove logs older than 90 days
python scripts/audit_logger.py --vault ../AI_Employee_Vault cleanup
```

### Demo Mode
```bash
# Create demo log entries
python scripts/audit_logger.py --vault ../AI_Employee_Vault demo
```

## Log Entry Format

```json
{
  "entry_id": "a1b2c3d4e5f6",
  "timestamp": "2026-03-14T10:30:00",
  "date": "2026-03-14",
  "action_type": "email_send",
  "actor": "email_mcp",
  "parameters": {
    "to": "client@example.com",
    "subject": "Invoice #123"
  },
  "result": "success",
  "error": null,
  "approval_status": "approved",
  "approved_by": "human",
  "context": {},
  "correlation_id": "a1b2c3d4e5f6",
  "system": {
    "dry_run": true,
    "log_level": "INFO",
    "python_version": "3.13.0",
    "platform": "win32"
  }
}
```

## Python API

```python
from audit_logger import AuditLogger

# Initialize
logger = AuditLogger(vault_path='../AI_Employee_Vault')

# Log action start
correlation_id = logger.log_action_start(
    action_type='invoice_create',
    actor='odoo_mcp',
    parameters={'partner_id': 1, 'amount': 1500}
)

# Log action complete
logger.log_action_complete(
    action_type='invoice_create',
    actor='odoo_mcp',
    parameters={'partner_id': 1, 'amount': 1500},
    correlation_id=correlation_id
)

# Log action failure
logger.log_action_failure(
    action_type='invoice_create',
    actor='odoo_mcp',
    parameters={'partner_id': 1, 'amount': 1500},
    error='Connection timeout',
    correlation_id=correlation_id
)

# Log error
logger.log_error(
    error_type='authentication',
    error_message='Invalid credentials',
    context={'service': 'odoo'},
    actor='odoo_mcp'
)

# Query logs
entries = logger.query(
    start_date='2026-03-01',
    end_date='2026-03-14',
    action_type='email_send',
    result='success'
)

# Get statistics
stats = logger.get_statistics(days=7)
print(f"Total actions: {stats['total_actions']}")
print(f"Errors: {stats['errors']}")
```

## Configuration

### Environment Variables
```bash
# Log level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Log retention days
LOG_RETENTION_DAYS=90

# Vault path
VAULT_PATH=/path/to/AI_Employee_Vault
```

## Log File Structure

```
AI_Employee_Vault/
└── Logs/
    ├── 2026-03-14.json          # Daily log
    ├── 2026-03-13.json          # Daily log
    ├── ...
    └── audit/
        └── audit_trail.jsonl    # Append-only trail
```

## Query Examples

### Find All Errors
```bash
python scripts/audit_logger.py --vault ../AI_Employee_Vault query --result failure
```

### Find All Email Actions
```bash
python scripts/audit_logger.py --vault ../AI_Employee_Vault query --type email_send
```

### Find Actions by Actor
```bash
python scripts/audit_logger.py --vault ../AI_Employee_Vault query --actor orchestrator
```

### Find Pending Approvals
```python
entries = logger.query(action_type='approval_request', result='pending')
```

## Statistics Output

```
Audit Log Statistics (Last 7 Days)
==================================================
Total Actions: 156
Errors: 3
Approvals Required: 12

By Result:
  success: 145
  failure: 3
  pending: 8

By Action Type:
  email_send: 45
  notification_detected: 67
  post_created: 23
  approval_request: 12
  error_auth: 3
  invoice_create: 6

By Actor:
  gmail_watcher: 45
  orchestrator: 67
  linkedin_poster: 23
  approval_manager: 12
  odoo_mcp: 6
  error_recovery: 3
```

## Retention Policy

- Daily logs retained for 90 days (configurable)
- Audit trail is append-only (never deleted)
- Automatic cleanup via scheduled task
- Manual cleanup available via CLI

## Export Formats

### JSON Export
```json
[
  {
    "entry_id": "...",
    "timestamp": "...",
    "action_type": "...",
    ...
  }
]
```

### CSV Export
```csv
entry_id,timestamp,action_type,actor,result,error,approval_status
a1b2c3,2026-03-14T10:30:00,email_send,email_mcp,success,,approved
```

## Compliance & Security

- Append-only audit trail prevents tampering
- Unique entry IDs for integrity verification
- Correlation IDs link related actions
- Full context captured for each action
- System state recorded (dry_run, version, etc.)

## Troubleshooting

### No Logs Found
- Check vault path is correct
- Verify log files exist in `Logs/` folder
- Check date range for query

### Export Failed
- Ensure output path is writable
- Check file permissions
- Verify JSON/CSV format support

### High Log Volume
- Reduce log level to WARNING or ERROR
- Decrease retention period
- Filter queries by specific criteria

---

*Skill Version: 1.0*
*AI Employee v0.3 - Gold Tier*
