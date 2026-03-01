---
name: whatsapp-watcher
description: |
  WhatsApp Web monitoring using Playwright. Monitors WhatsApp Web for unread messages
  containing priority keywords (urgent, asap, invoice, payment, help) and creates
  action files in Needs_Action folder. Requires browser automation setup.
---

# WhatsApp Watcher

Monitor WhatsApp Web for important messages using Playwright browser automation.

## Prerequisites

```bash
# Install Playwright
pip install playwright
playwright install

# Install python-dotenv for configuration
pip install python-dotenv
```

## Server Lifecycle

### Start Playwright Server (for MCP integration)

```bash
# Start Playwright MCP server
npx @playwright/mcp@latest --port 8808 --shared-browser-context &
```

### WhatsApp Session Management

WhatsApp Web requires an authenticated session. The first run will need manual QR code scan:

```bash
# Session will be stored in configured path
python scripts/whatsapp_watcher.py --vault ../AI_Employee_Vault --session-path ./whatsapp_session
```

## Quick Reference

### Basic Usage

```bash
# Run WhatsApp Watcher (continuous mode)
python scripts/whatsapp_watcher.py --vault ../AI_Employee_Vault

# Run with custom check interval (30 seconds)
python scripts/whatsapp_watcher.py --vault ../AI_Employee_Vault --interval 30

# Create demo WhatsApp message file
python scripts/whatsapp_watcher.py --vault ../AI_Employee_Vault --demo
```

### Configuration

```bash
# Set session path in .env
echo "WHATSAPP_SESSION_PATH=./whatsapp_session" >> .env

# Set priority keywords (comma-separated)
echo "WHATSAPP_KEYWORDS=urgent,asap,invoice,payment,help" >> .env
```

## Workflow

1. **Start Watcher**: Script launches headless browser to WhatsApp Web
2. **Session Load**: Loads existing session or waits for QR scan
3. **Monitor Unread**: Checks for unread messages every N seconds
4. **Keyword Filter**: Filters messages containing priority keywords
5. **Create Action File**: Creates markdown file in Needs_Action folder
6. **Mark Processed**: Tracks processed message IDs to avoid duplicates

## Action File Format

```markdown
---
type: whatsapp
from: +1234567890
chat: John Doe
received: 2026-02-28T10:30:00Z
keywords: urgent, invoice
priority: high
status: pending
---

# WhatsApp Message: John Doe

## Message Content
Hey, can you send me the invoice for January? This is urgent.

## Detected Keywords
- urgent
- invoice

## Suggested Actions
- [ ] Read message
- [ ] Generate invoice
- [ ] Send via email (requires approval)
- [ ] Mark as done

---
*Created by WhatsApp Watcher - AI Employee v0.1*
```

## Keyword Detection

Default priority keywords:
- `urgent` - High priority immediate attention
- `asap` - As soon as possible request
- `invoice` - Billing/invoice related
- `payment` - Payment inquiry or issue
- `help` - Assistance request

Customize in `.env`:
```
WHATSAPP_KEYWORDS=urgent,asap,invoice,payment,help,pricing,quote
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  WhatsApp Web   │────▶│ WhatsApp Watcher │────▶│ Needs_Action/   │
│  (Browser)      │     │  (Playwright)    │     │ WHATSAPP_*.md   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Session Storage │
                        │  (Persistent)    │
                        └──────────────────┘
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code appears every time | Session not saving - check session path permissions |
| No messages detected | Ensure WhatsApp Web is loaded and chats are visible |
| Browser crashes | Increase check interval, reduce frequency |
| Keyword false positives | Refine keyword list, add negative keywords |

## Security Notes

- **Session Storage**: Keep session files secure, never commit to version control
- **Privacy**: Be aware of WhatsApp's terms of service for automation
- **Rate Limiting**: Use reasonable check intervals (30s+) to avoid detection
- **Logout**: Implement proper logout for shared machines

## Demo Mode

Test without connecting to WhatsApp:

```bash
python scripts/whatsapp_watcher.py --vault ../AI_Employee_Vault --demo
```

Creates sample action file:
```
AI_Employee_Vault/Needs_Action/WHATSAPP_DEMO_20260228_103000.md
```

## Integration with Orchestrator

WhatsApp Watcher integrates with the main orchestrator:

```bash
# Terminal 1: Start WhatsApp Watcher
python scripts/whatsapp_watcher.py --vault ../AI_Employee_Vault

# Terminal 2: Start Orchestrator
python scripts/orchestrator.py --vault ../AI_Employee_Vault
```

Orchestrator will:
1. Detect new WhatsApp action files
2. Create Plan files for each message
3. Trigger Claude Code for processing
4. Move completed items to Done folder

## Example: Client Invoice Request

**Incoming WhatsApp:**
```
+1234567890 (John Doe): Hey, can you send me the invoice for January? This is urgent.
```

**Action File Created:**
```
AI_Employee_Vault/Needs_Action/WHATSAPP_john_doe_20260228_103000.md
```

**Claude Processing:**
1. Reads action file
2. Checks Company_Handbook.md for invoice rules
3. Creates Plan file with invoice generation steps
4. Generates invoice PDF
5. Creates approval request for email send
6. Waits for human approval

## Code Example: Custom Keyword Handler

```python
# Add to whatsapp_watcher.py
CUSTOM_KEYWORD_HANDLERS = {
    'invoice': lambda msg: create_invoice_action(msg),
    'payment': lambda msg: flag_for_finance_review(msg),
    'urgent': lambda msg: escalate_to_sms(msg),
}
```

## Next Steps

After WhatsApp Watcher creates action files:
1. Orchestrator processes Needs_Action folder
2. Claude Code analyzes and creates plans
3. Human approves sensitive actions
4. MCP servers execute approved actions

---
*WhatsApp Watcher v0.1 - Silver Tier Skill*
