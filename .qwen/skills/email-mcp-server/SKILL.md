---
name: email-mcp-server
description: |
  Email MCP server for sending, drafting, and managing emails via Gmail API.
  Supports OAuth2 authentication, attachments, and human-in-the-loop approval
  for sensitive emails. Integrates with Claude Code for automated responses.
---

# Email MCP Server

Model Context Protocol (MCP) server for email operations using Gmail API.

## Prerequisites

```bash
# Install Gmail API dependencies
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Install MCP server framework
npm install -g @modelcontextprotocol/server
```

## Setup

### 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json`

### 2. OAuth Authentication

```bash
# First-time authentication
python scripts/email_auth.py --credentials credentials.json

# This will:
# 1. Open browser for OAuth consent
# 2. Save token to token.json
# 3. Token is reused for subsequent requests
```

### 3. MCP Configuration

Add to `~/.config/claude-code/mcp.json`:

```json
{
  "servers": [
    {
      "name": "email",
      "command": "python",
      "args": ["/path/to/scripts/email_mcp_server.py"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json",
        "GMAIL_TOKEN": "/path/to/token.json"
      }
    }
  ]
}
```

## Quick Reference

### Send Email

```bash
# Basic email
python scripts/email_mcp_server.py send \
  --to recipient@example.com \
  --subject "Invoice #1234" \
  --body "Please find attached your invoice..."

# With attachment
python scripts/email_mcp_server.py send \
  --to recipient@example.com \
  --subject "Invoice #1234" \
  --body "Please find attached..." \
  --attachment ./invoice.pdf

# Draft only (no send)
python scripts/email_mcp_server.py draft \
  --to recipient@example.com \
  --subject "Invoice #1234" \
  --body "..."
```

### Read Emails

```bash
# List recent emails
python scripts/email_mcp_server.py list --max 10

# Search emails
python scripts/email_mcp_server.py search --query "from:client@example.com"

# Get specific email
python scripts/email_mcp_server.py get --id MESSAGE_ID
```

### Manage Labels

```bash
# Mark as read
python scripts/email_mcp_server.py label --id MESSAGE_ID --action read

# Archive
python scripts/email_mcp_server.py label --id MESSAGE_ID --action archive

# Add star
python scripts/email_mcp_server.py label --id MESSAGE_ID --action star
```

## Tools (MCP Protocol)

### `email_send`

Send an email immediately.

**Parameters:**
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject
- `body` (string, required): Email body (plain text or HTML)
- `cc` (string, optional): CC recipients
- `bcc` (string, optional): BCC recipients
- `attachments` (array, optional): File paths to attach

**Example:**
```json
{
  "tool": "email_send",
  "arguments": {
    "to": "client@example.com",
    "subject": "Invoice #1234",
    "body": "Dear Client,\n\nPlease find attached your invoice...\n\nBest regards",
    "attachments": ["/path/to/invoice.pdf"]
  }
}
```

### `email_draft`

Create a draft email without sending.

**Parameters:** Same as `email_send`

**Returns:** Draft ID for later retrieval/modification

### `email_list`

List emails matching criteria.

**Parameters:**
- `query` (string, optional): Gmail search query
- `max_results` (number, optional): Max results (default: 10)
- `label_ids` (array, optional): Filter by labels

**Example:**
```json
{
  "tool": "email_list",
  "arguments": {
    "query": "is:unread is:important",
    "max_results": 5
  }
}
```

### `email_get`

Get full email content.

**Parameters:**
- `message_id` (string, required): Gmail message ID

### `email_reply`

Reply to an email.

**Parameters:**
- `message_id` (string, required): Original message ID
- `body` (string, required): Reply content
- `include_original` (boolean, optional): Include original in reply

### `email_label`

Modify email labels.

**Parameters:**
- `message_id` (string, required): Gmail message ID
- `action` (string, required): read/unread/archive/star/trash

## Human-in-the-Loop Pattern

For sensitive emails, use approval workflow:

### 1. Create Approval Request

```python
# In orchestrator or Claude workflow
def send_email_with_approval(to, subject, body):
    # Check if approval needed
    if requires_approval(to, subject, body):
        # Create approval file
        filepath = create_approval_request({
            'type': 'email_send',
            'to': to,
            'subject': subject,
            'body': body
        })
        return f"Approval request created: {filepath}"
    else:
        # Send directly
        return send_email(to, subject, body)
```

### 2. Approval File Format

```markdown
---
type: approval_request
action: email_send
to: client@example.com
subject: Invoice #1234
created: 2026-02-28T10:00:00Z
expires: 2026-03-01T10:00:00Z
status: pending
---

# Email Approval Request

## Details
- **To:** client@example.com
- **Subject:** Invoice #1234
- **Attachments:** invoice.pdf

## Content
Dear Client,

Please find attached your invoice for January 2026.

Best regards

## To Approve
Move this file to /Approved/ folder.

## To Reject
Move this file to /Rejected/ folder.

---
*Created by Email MCP - AI Employee v0.1*
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Claude Code    │────▶│  Email MCP       │────▶│  Gmail API      │
│  (Reasoning)    │     │  (Server)        │     │  (External)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Approval Files  │
                       │  (HITL)          │
                       └──────────────────┘
```

## Security

### Credential Management

```bash
# NEVER commit credentials
echo "credentials.json" >> .gitignore
echo "token.json" >> .gitignore

# Use environment variables
export GMAIL_CREDENTIALS=/secure/path/credentials.json
export GMAIL_TOKEN=/secure/path/token.json
```

### Approval Thresholds

| Condition | Action |
|-----------|--------|
| New recipient (first time) | Require approval |
| Bulk email (>5 recipients) | Require approval |
| Contains attachment | Require approval |
| Known contact, no attachment | Auto-send OK |

## Demo Mode

Test without sending real emails:

```bash
# Set dry-run mode
export DRY_RUN=true

# Run email commands
python scripts/email_mcp_server.py send \
  --to test@example.com \
  --subject "Test" \
  --body "This won't actually send"

# Output: [DRY RUN] Would send email to test@example.com
```

## Templates

### Invoice Email Template

```markdown
Subject: Invoice #{{invoice_number}} - {{company_name}}

Dear {{client_name}},

Please find attached invoice #{{invoice_number}} for {{amount}}.

Payment Details:
- Amount: ${{amount}}
- Due Date: {{due_date}}
- Payment Method: {{payment_method}}

If you have any questions, please don't hesitate to reach out.

Best regards,
{{your_name}}
```

### Response Template

```markdown
Subject: Re: {{original_subject}}

Dear {{sender_name}},

Thank you for your email. 

[AI-generated response based on context]

Best regards,
{{your_name}}

---
*Drafted by AI Employee - Review before sending*
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| OAuth error | Re-run authentication, check credentials |
| API quota exceeded | Wait 24 hours or request quota increase |
| Attachment too large | Gmail limit is 25MB total |
| Authentication expired | Re-run email_auth.py to refresh token |

## Example: Automated Invoice Response

```python
# Workflow: Client asks for invoice via WhatsApp
# 1. WhatsApp Watcher creates action file
# 2. Claude Code processes and generates invoice
# 3. Email MCP sends with approval

from email_mcp_server import EmailMCP

mcp = EmailMCP()

# Check if approval needed (new client)
if client not in known_clients:
    mcp.create_approval_request(
        to=client_email,
        subject=f"Invoice #{invoice_number}",
        body=invoice_email_template,
        attachments=[invoice_pdf]
    )
else:
    # Send directly for known clients
    mcp.send(
        to=client_email,
        subject=f"Invoice #{invoice_number}",
        body=invoice_email_template,
        attachments=[invoice_pdf]
    )
```

## Next Steps

After email is sent:
1. Log action to audit log
2. Update Dashboard.md
3. Move task to Done folder
4. Track response/reply

---
*Email MCP Server v0.1 - Silver Tier Skill*
