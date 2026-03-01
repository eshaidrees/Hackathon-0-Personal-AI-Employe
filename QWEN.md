# QWEN.md - AI Employee Project Configuration

## Project Overview

**Project Name:** Personal AI Employee
**Hackathon:** Hackathon 0 - Building Autonomous FTEs in 2026
**Version:** 0.2.0 (Silver Tier)
**Status:** Silver Tier Complete
**Brain:** Qwen Code (or Claude Code)

---

## Architecture Summary

### Core Components

1. **Perception Layer (Watchers)**
   - `scripts/gmail_watcher.py` - Monitors Gmail API for new messages
   - `scripts/linkedin_watcher.py` - Monitors LinkedIn via Playwright
   - `scripts/filesystem_watcher.py` - Monitors Inbox folder for file drops

2. **Memory Layer (Obsidian Vault)**
   - `AI_Employee_Vault/` - Local Markdown knowledge base
   - Dashboard.md - Real-time status dashboard
   - Company_Handbook.md - Rules of engagement
   - Business_Goals.md - Objectives and metrics

3. **Reasoning Layer (Qwen Code)**
   - Processes action items from Needs_Action folder
   - Creates plans in Plans folder
   - Requests approval for sensitive actions (HITL)

4. **Action Layer (MCP Servers + Orchestrator)**
   - `scripts/orchestrator.py` - Master coordination process
   - `scripts/email_mcp_server.py` - Email sending via Gmail API
   - `scripts/linkedin_poster.py` - LinkedIn content posting
   - Updates Dashboard.md and manages file flow

5. **Scheduling Layer**
   - `scripts/scheduler_setup.py` - Configure cron/Task Scheduler
   - Daily briefings, weekly reviews, health checks

---

## Folder Structure

```
Personal-AI-Employe/
├── AI_Employee_Vault/          # Obsidian vault (DO NOT COMMIT sensitive files)
│   ├── Dashboard.md            # Main status dashboard
│   ├── Company_Handbook.md     # Rules of engagement
│   ├── Business_Goals.md       # Q1 2026 objectives
│   ├── Inbox/                  # Raw incoming items
│   ├── Needs_Action/           # Items requiring processing
│   ├── Plans/                  # Action plans by Qwen Code
│   ├── Pending_Approval/       # Awaiting human decision (HITL)
│   ├── Approved/               # Ready to execute
│   ├── Rejected/               # Declined actions
│   ├── Done/                   # Completed archive
│   ├── Logs/                   # Audit logs (JSON)
│   └── Briefings/              # CEO briefings
├── scripts/
│   ├── base_watcher.py         # Base class for all watchers
│   ├── gmail_watcher.py        # Gmail API monitoring
│   ├── gmail_auth.py           # Gmail OAuth2 authentication
│   ├── linkedin_watcher.py     # LinkedIn monitoring (Playwright)
│   ├── linkedin_poster.py      # LinkedIn posting automation
│   ├── filesystem_watcher.py   # File drop monitoring script
│   ├── orchestrator.py         # Master coordination process
│   ├── email_mcp_server.py     # Email MCP server (Gmail API)
│   ├── approval_manager.py     # HITL approval management
│   └── scheduler_setup.py      # Scheduled tasks setup
├── credentials.json            # Gmail OAuth credentials (DO NOT COMMIT)
├── token.json                  # Gmail OAuth token (DO NOT COMMIT)
├── .qwen/skills/               # Agent skills documentation
│   ├── browsing-with-playwright/
│   ├── whatsapp-watcher/
│   ├── linkedin-poster/
│   ├── email-mcp-server/
│   ├── hitl-approval/
│   ├── claude-reasoning/
│   └── task-scheduler/
├── .env.template               # Environment variables template
├── .gitignore                  # Git ignore rules
├── README.md                   # Setup and usage instructions
├── SILVER_TIER_SETUP.md        # Detailed Silver Tier setup
└── QWEN.md                     # This file - Project configuration
```

---

## Quick Commands

### Setup
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
playwright install

# Copy environment template
copy .env.template .env  # Windows
```

### Gmail Authentication
```bash
# Place credentials.json in project root first
# Then authenticate
python scripts/gmail_auth.py

# Test Gmail API connection
python scripts/gmail_watcher.py --vault ../AI_Employee_Vault --test
```

### Run Watchers
```bash
# Gmail Watcher (every 2 minutes)
python scripts/gmail_watcher.py --vault ../AI_Employee_Vault --interval 120

# LinkedIn Watcher (every 5 minutes)
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --interval 300

# File System Watcher (every 30 seconds)
python scripts/filesystem_watcher.py --vault ../AI_Employee_Vault --interval 30

# Demo mode (create sample files)
python scripts/gmail_watcher.py --vault ../AI_Employee_Vault --demo
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --demo
```

### Run Actions
```bash
# LinkedIn Poster (create demo post)
python scripts/linkedin_poster.py --vault ../AI_Employee_Vault --demo

# Email MCP (demo mode)
python scripts/email_mcp_server.py demo

# Approval Manager (list pending)
python scripts/approval_manager.py --vault ../AI_Employee_Vault list --type pending
```

### Run Orchestrator
```bash
# Single cycle (dry-run)
python scripts/orchestrator.py --vault ../AI_Employee_Vault --once --dry-run

# Continuous mode
python scripts/orchestrator.py --vault ../AI_Employee_Vault --interval 60
```

### Setup Scheduling
```bash
# Setup cron/Task Scheduler
python scripts/scheduler_setup.py setup

# List scheduled tasks
python scripts/scheduler_setup.py list

# Remove all scheduled tasks
python scripts/scheduler_setup.py remove
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CLAUDE_COMMAND` | Qwen/Claude Code command | `claude` |
| `MAX_CLAUDE_ITERATIONS` | Max task iterations | `10` |
| `DRY_RUN` | Safe mode (no real actions) | `true` |
| `GMAIL_CREDENTIALS_PATH` | Gmail OAuth credentials file | `credentials.json` |
| `GMAIL_TOKEN_PATH` | Gmail OAuth token file | `token.json` |
| `LINKEDIN_EMAIL` | LinkedIn email | (empty) |
| `LINKEDIN_PASSWORD` | LinkedIn password | (empty) |
| `LINKEDIN_SESSION_PATH` | LinkedIn browser session | `./linkedin_session` |
| `LINKEDIN_KEYWORDS` | LinkedIn notification keywords | `message,connection,job,post` |
| `WHATSAPP_SESSION_PATH` | WhatsApp session | `./whatsapp_session` |
| `WHATSAPP_KEYWORDS` | Priority keywords | `urgent,asap,invoice,payment,help` |
| `POST_APPROVAL_REQUIRED` | LinkedIn approval required | `true` |
| `VAULT_PATH` | Absolute vault path | (auto) |

---

## Silver Tier Checklist

### Core Requirements
- [x] All Bronze requirements completed
- [x] Two or more Watcher scripts (Gmail + LinkedIn + File System)
- [x] LinkedIn auto-posting capability
- [x] Qwen Code reasoning loop with Plan.md creation
- [x] Email MCP server for external actions
- [x] Human-in-the-loop approval workflow
- [x] Task scheduling via cron/Task Scheduler

### Skills Created
- [x] `gmail-watcher` - Gmail API monitoring with OAuth2
- [x] `linkedin-watcher` - LinkedIn monitoring via Playwright
- [x] `linkedin-poster` - LinkedIn content posting
- [x] `email-mcp-server` - Gmail API integration
- [x] `hitl-approval` - Approval workflow
- [x] `claude-reasoning` - Structured reasoning loop
- [x] `task-scheduler` - Scheduled operations

---

## Gold Tier TODO

To advance to Gold Tier, add:
- [ ] Full cross-domain integration (Personal + Business)
- [ ] Odoo Community integration via MCP
- [ ] Facebook/Instagram integration
- [ ] Twitter (X) integration
- [ ] Weekly Business and Accounting Audit
- [ ] Error recovery and graceful degradation
- [ ] Comprehensive audit logging
- [ ] Ralph Wiggum loop for autonomous completion

---

## Workflow Examples

### Example 1: Gmail Invoice Request

```
1. Email received: "Please send me the invoice"
2. Gmail Watcher detects unread email via Gmail API
3. Creates: Needs_Action/EMAIL_msg_id_*.md
4. Orchestrator triggers Qwen Code reasoning
5. Qwen Code creates: Plans/PLAN_invoice_*.md
6. Qwen Code generates invoice PDF
7. Qwen Code creates approval: Pending_Approval/APPROVAL_email_*.md
8. Human moves file to Approved/
9. Email MCP sends invoice via Gmail API
10. Task moved to Done/
```

### Example 2: LinkedIn Connection Request

```
1. LinkedIn notification: "John Doe wants to connect"
2. LinkedIn Watcher detects via Playwright
3. Creates: Needs_Action/LINKEDIN_MSG_john_doe_*.md
4. Orchestrator triggers Qwen Code reasoning
5. Qwen Code analyzes sender profile
6. Qwen Code drafts response message
7. Human reviews and approves
8. LinkedIn Poster sends acceptance
9. Task moved to Done/
```

### Example 3: LinkedIn Business Post

```
1. AI generates post content based on Business_Goals
2. LinkedIn Poster creates: Pending_Approval/POST_*.md
3. Human reviews and moves to Approved/
4. LinkedIn Poster publishes via Playwright
5. Screenshot saved to Done/
```

### Example 4: Daily CEO Briefing (Scheduled)

```
1. Cron/Task Scheduler triggers at 8 AM
2. Orchestrator runs daily-briefing action
3. Reviews yesterday's completed tasks
4. Summarizes revenue/expenses
5. Generates: Briefings/YYYY-MM-DD_Daily_Briefing.md
6. Updates Dashboard.md
```

---

## Key Design Decisions

1. **Local-First:** All data stored locally in Obsidian vault for privacy
2. **File-Based Communication:** Components communicate via markdown files
3. **Dry-Run Default:** Safe mode enabled by default during development
4. **Human-in-the-Loop:** Sensitive actions require approval before execution
5. **Audit Logging:** All actions logged to JSON files for review
6. **Modular Skills:** Each capability is a separate, reusable skill
7. **Qwen Code as Brain:** Uses Qwen Code (or Claude Code) for reasoning

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `credentials.json not found` | Place credentials.json in project root |
| Gmail API error | Run `python scripts/gmail_auth.py` to re-authenticate |
| LinkedIn login fails | Manual login may be required first time |
| Session not saved | Check session path permissions |
| Approval not detected | Check file naming: APPROVAL_*.md |
| Scheduled task not running | Check scheduler logs, verify paths |
| Import errors | Activate venv: `venv\Scripts\activate` |
| Playwright error | Run `playwright install` |

---

## Security Notes

- NEVER commit `.env` file
- NEVER commit `credentials.json` or `token.json`
- NEVER store credentials in vault markdown files
- Keep `DRY_RUN=true` during development
- Review logs regularly in `AI_Employee_Vault/Logs/`
- Session files stored securely, never committed
- Be aware of LinkedIn/WhatsApp terms of service

---

## Agent Skills Reference

| Skill | Purpose | Script |
|-------|---------|--------|
| `browsing-with-playwright` | Browser automation | Playwright MCP |
| `gmail-watcher` | Gmail API monitoring | gmail_watcher.py |
| `linkedin-watcher` | LinkedIn monitoring | linkedin_watcher.py |
| `linkedin-poster` | LinkedIn posting | linkedin_poster.py |
| `email-mcp-server` | Email operations | email_mcp_server.py |
| `hitl-approval` | Approval workflow | approval_manager.py |
| `claude-reasoning` | Reasoning loop | orchestrator.py |
| `task-scheduler` | Scheduling | scheduler_setup.py |

---

## Contact & Resources

- **Hackathon Info:** Personal AI Employee Hackathon 0
- **Zoom Meetings:** Wednesdays 10:00 PM
- **Documentation:** 
  - `README.md` - Setup and usage
  - `SILVER_TIER_SETUP.md` - Detailed setup guide
  - `.qwen/skills/*/SKILL.md` - Skill documentation
- **Gmail API:** https://console.cloud.google.com/

---

*Last Updated: 2026-02-28*
*AI Employee v0.2 - Silver Tier Complete*
*Brain: Qwen Code (or Claude Code)*
