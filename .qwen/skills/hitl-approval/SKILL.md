---
name: hitl-approval
description: |
  Human-in-the-Loop (HITL) approval workflow for sensitive actions.
  File-based approval system where Claude creates approval requests,
  human reviews and moves files to Approved/Rejected folders,
  and orchestrator executes approved actions.
---

# Human-in-the-Loop Approval Workflow

File-based approval system for sensitive AI actions.

## Overview

The HITL approval workflow ensures human oversight for sensitive operations:
- Sending emails to new contacts
- Making payments
- Posting to social media
- Accessing banking systems
- Any irreversible actions

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  AI Detection   │────▶│  Approval File   │────▶│  Human Review   │
│  (Claude Code)  │     │  Pending_Approval│     │  (User)         │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                    ┌─────────────────────────────────────┘
                    │
        ┌───────────▼───────────┐
        │   Move File To:       │
        │   /Approved/  or      │
        │   /Rejected/          │
        └───────────┬───────────┘
                    │
        ┌───────────▼───────────┐
        │   Orchestrator        │
        │   Executes/Logs       │
        └───────────────────────┘
```

## Approval File Format

```markdown
---
type: approval_request
action: email_send
to: client@example.com
subject: Invoice #1234
amount: 1500.00
created: 2026-02-28T10:00:00Z
expires: 2026-03-01T10:00:00Z
status: pending
priority: normal
---

# Approval Request: Email Send

## Action Details
- **Type:** Send Email
- **To:** client@example.com
- **Subject:** Invoice #1234
- **Attachments:** invoice.pdf

## Content
Dear Client,

Please find attached your invoice for January 2026.

Best regards

## Why Approval Required
- New recipient (first time emailing)
- Contains financial document attachment

## To Approve
1. Review the content above
2. Move this file to `/Approved/` folder
3. AI will execute the action

## To Reject
1. Move this file to `/Rejected/` folder
2. Add reason for rejection in notes below

## Notes
<!-- Add any notes or context here -->

---
*Created by AI Employee - Approval Required*
```

## Action Types & Thresholds

| Action Type | Auto-Approve | Require Approval |
|-------------|--------------|------------------|
| Email to known contact | Yes (no attachment) | New contact or attachment |
| Email bulk send | Never | >5 recipients |
| Payment | Never | Any amount |
| Social media post | Never | All posts |
| Bank access | Never | Always |
| File delete (vault) | Never | Always |
| File create/read | Yes | Never |

## Creating Approval Requests

### From Python

```python
from pathlib import Path
from datetime import datetime

def create_approval_request(action_type: str, details: dict, vault_path: str) -> Path:
    """Create approval request file."""
    vault = Path(vault_path)
    pending = vault / 'Pending_Approval'
    pending.mkdir(parents=True, exist_ok=True)
    
    filename = f"APPROVAL_{action_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = pending / filename
    
    content = f"""---
type: approval_request
action: {action_type}
created: {datetime.now().isoformat()}
expires: {(datetime.now().replace(hour=23, minute=59)).isoformat()}
status: pending
---

# Approval Request: {action_type.replace('_', ' ').title()}

## Details
{chr(10).join(f'- **{k.replace("_", " ").title()}:** {v}' for k, v in details.items())}

## To Approve
Move this file to `/Approved/` folder.

## To Reject
Move this file to `/Rejected/` folder.

---
*Created by AI Employee - Approval Required*
"""
    
    filepath.write_text(content, encoding='utf-8')
    return filepath
```

### From Claude Code

```
# Claude creates approval file directly

write_file(
  path: "Pending_Approval/APPROVAL_email_send_20260228_100000.md",
  content: """---
type: approval_request
action: email_send
to: client@example.com
subject: Invoice #1234
---

# Approval Request

...
"""
)
```

## Orchestrator Integration

```python
class Orchestrator:
    def check_approvals(self):
        """Check Approved folder for files ready to execute."""
        approved_folder = self.vault_path / 'Approved'
        
        if not approved_folder.exists():
            return
        
        for filepath in approved_folder.glob('APPROVAL_*.md'):
            self.execute_approved_action(filepath)
    
    def execute_approved_action(self, filepath: Path):
        """Execute an approved action."""
        content = filepath.read_text()
        
        # Parse action type
        action_type = self._extract_action_type(content)
        details = self._extract_details(content)
        
        # Execute based on type
        if action_type == 'email_send':
            self._send_email(details)
        elif action_type == 'linkedin_post':
            self._post_linkedin(details)
        elif action_type == 'payment':
            self._process_payment(details)
        
        # Move to Done and log
        self._archive_action(filepath)
```

## Approval Workflow Example

### Scenario: Client Invoice Request

**Step 1: WhatsApp Message Received**
```
+1234567890: Hey, can you send me the invoice for January?
```

**Step 2: WhatsApp Watcher Creates Action File**
```
Needs_Action/WHATSAPP_client_20260228_100000.md
```

**Step 3: Claude Code Processes**
- Reads action file
- Generates invoice PDF
- Determines approval needed (new client)
- Creates approval request

**Step 4: Approval File Created**
```
Pending_Approval/APPROVAL_email_send_20260228_100500.md
```

**Step 5: Human Review**
- User opens Pending_Approval folder
- Reviews email content
- Moves file to Approved folder

**Step 6: Orchestrator Executes**
- Detects approved file
- Sends email via Email MCP
- Logs action
- Moves to Done

## Monitoring Approvals

### Check Pending Approvals

```bash
# List pending approvals
python scripts/approval_manager.py list --pending

# Check expired approvals
python scripts/approval_manager.py list --expired
```

### Auto-Expire Approvals

```python
def check_expired_approvals(vault_path: str):
    """Move expired approvals to Rejected."""
    pending = Path(vault_path) / 'Pending_Approval'
    rejected = Path(vault_path) / 'Rejected'
    
    for f in pending.glob('APPROVAL_*.md'):
        content = f.read_text()
        expires = extract_expiry(content)
        
        if expires and datetime.now() > expires:
            # Move to rejected with note
            f.rename(rejected / f.name)
            logger.info(f'Expired approval moved to rejected: {f.name}')
```

## Security Considerations

### Approval File Integrity

- Never auto-approve payments to new recipients
- Always require approval for banking access
- Log all approval decisions
- Set reasonable expiry times (24-48 hours)

### Audit Trail

```json
{
  "timestamp": "2026-02-28T10:05:00Z",
  "action_type": "email_send",
  "actor": "claude_code",
  "target": "client@example.com",
  "approval_status": "approved",
  "approved_by": "human",
  "approval_file": "APPROVAL_email_send_20260228_100500.md",
  "result": "success"
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Approval not detected | Check file naming: APPROVAL_*.md |
| Action not executing | Check orchestrator logs |
| File stuck in Approved | Verify action completed, check logs |
| Expired too quickly | Adjust expiry time in template |

## Best Practices

1. **Clear Descriptions**: Explain why approval is needed
2. **Complete Information**: Include all relevant details
3. **Expiry Times**: Set reasonable deadlines
4. **Audit Logging**: Log all decisions
5. **Graceful Rejection**: Allow notes on rejection reasons

---
*HITL Approval Workflow v0.1 - Silver Tier Skill*
