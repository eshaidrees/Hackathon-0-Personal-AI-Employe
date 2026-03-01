# 🤖 Personal AI Employee - Silver Tier Complete!

**Hackathon 0: Building Autonomous FTEs in 2026**

A local-first, agent-driven personal AI employee that manages your personal and business affairs 24/7 using Qwen Code and Obsidian.

**Status:** ✅ **Silver Tier Complete & Production Ready**

---

## 🚀 Quick Start (10 Minutes)

### Step 1: Setup Environment

```bash
cd Personal-AI-Employe

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
playwright install
```

### Step 2: Configure Gmail (NO OAuth Required!)

**Use Gmail IMAP - Works Instantly!**

1. **Enable IMAP in Gmail:**
   - Gmail Settings → See all settings → Forwarding and POP/IMAP → Enable IMAP

2. **Enable 2-Factor Authentication:**
   - https://myaccount.google.com/security

3. **Create App Password:**
   - https://myaccount.google.com/apppasswords
   - App: Mail | Device: Other (AI Employee)
   - Copy 16-character password

4. **Add to `.env` file:**
   ```
   GMAIL_EMAIL=your.email@gmail.com
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

### Step 3: Test It Works

```bash
# Run Gmail Watcher (reads your real emails!)
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --interval 120

# Process emails
python scripts/orchestrator.py --vault ../AI_Employee_Vault --once

# Check results
dir AI_Employee_Vault\Needs_Action
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 PERSONAL AI EMPLOYEE                    │
│                    SILVER TIER                          │
├─────────────────────────────────────────────────────────┤
│  Perception Layer (Watchers)                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ Gmail        │ │ LinkedIn     │ │ File System  │    │
│  │ Watcher      │ │ Watcher      │ │ Watcher      │    │
│  │ (IMAP+API)   │ │ (Playwright) │ │ (Watchdog)   │    │
│  └──────────────┘ └──────────────┘ └──────────────┘    │
├─────────────────────────────────────────────────────────┤
│  Memory Layer (Obsidian Vault)                          │
│  Dashboard | Handbook | Goals | Needs_Action | Plans   │
├─────────────────────────────────────────────────────────┤
│  Reasoning Layer (Qwen Code)                            │
│  Reads → Thinks → Plans → Executes → Reviews           │
├─────────────────────────────────────────────────────────┤
│  Action Layer (MCP + Orchestrator)                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ Email MCP    │ │ LinkedIn     │ │ Approval     │    │
│  │ Server       │ │ Poster       │ │ Manager      │    │
│  └──────────────┘ └──────────────┘ └──────────────┘    │
├─────────────────────────────────────────────────────────┤
│  Scheduling Layer                                       │
│  Daily Briefings | Weekly Reviews | Health Checks       │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Vault Structure

```
AI_Employee_Vault/
├── Dashboard.md           # Real-time status dashboard
├── Company_Handbook.md    # Rules of engagement
├── Business_Goals.md      # Q1 2026 objectives
├── Inbox/                 # Raw incoming items
├── Needs_Action/          # Items requiring processing
├── Plans/                 # Action plans by Qwen Code
├── Pending_Approval/      # Awaiting human decision (HITL)
├── Approved/              # Ready to execute
├── Rejected/              # Declined actions
├── Done/                  # Completed archive
├── Logs/                  # Audit logs (JSON)
└── Briefings/             # CEO briefings
```

---

## 🚀 Usage - Full Automation

### Option 1: Run All Watchers (Recommended)

Open 4 terminals:

```bash
# Terminal 1: Gmail Watcher (every 2 min)
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --interval 120

# Terminal 2: LinkedIn Watcher (every 5 min)
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --interval 300

# Terminal 3: File System Watcher (every 30 sec)
python scripts/filesystem_watcher.py --vault ../AI_Employee_Vault --interval 30

# Terminal 4: Orchestrator (every 60 sec)
python scripts/orchestrator.py --vault ../AI_Employee_Vault --interval 60
```

### Option 2: Quick Test (Demo Mode)

```bash
# Create demo files
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --demo
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --demo

# Run orchestrator
python scripts/orchestrator.py --vault ../AI_Employee_Vault --once --dry-run

# Check results
type AI_Employee_Vault\Dashboard.md
```

### Option 3: Process Real Emails

```bash
# 1. Run Gmail Watcher (creates action files from emails)
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --interval 120

# 2. Generate reply drafts
python scripts/email_auto_responder.py --vault ../AI_Employee_Vault

# 3. Review drafts in Pending_Approval/
dir AI_Employee_Vault\Pending_Approval\

# 4. Approve (move to Approved/)
move AI_Employee_Vault\Pending_Approval\REPLY_*.md AI_Employee_Vault\Approved\

# 5. Send approved emails
python scripts/email_auto_responder.py --vault ../AI_Employee_Vault --send-approved
```

---

## ✅ Silver Tier Deliverables - ALL COMPLETE

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | **Bronze Tier Foundation** | ✅ | Dashboard, Handbook, Goals, folders |
| 2 | **Two or more Watcher scripts** | ✅ | Gmail (API + IMAP) + LinkedIn + File System |
| 3 | **LinkedIn auto-posting** | ✅ | `linkedin_poster.py` |
| 4 | **Qwen Code reasoning loop** | ✅ | `orchestrator.py` creates Plan.md |
| 5 | **One working MCP server** | ✅ | `email_mcp_server.py` |
| 6 | **Human-in-the-loop approval** | ✅ | `approval_manager.py` + folders |
| 7 | **Task scheduling** | ✅ | `scheduler_setup.py` |

---

## 📜 Available Scripts

### Watchers (Perception Layer)

| Script | Purpose | Command |
|--------|---------|---------|
| `gmail_imap_watcher.py` | Gmail via IMAP (NO OAuth!) | `--interval 120` |
| `gmail_watcher.py` | Gmail via OAuth API | `--interval 120` |
| `linkedin_watcher.py` | LinkedIn monitoring | `--interval 300` |
| `filesystem_watcher.py` | File drop monitoring | `--interval 30` |

### Actions (Action Layer)

| Script | Purpose | Command |
|--------|---------|---------|
| `email_auto_responder.py` | Auto-reply to emails | `--send-approved` |
| `email_mcp_server.py` | Email MCP server | `demo` |
| `linkedin_poster.py` | LinkedIn auto-posting | `--demo` |

### Coordination

| Script | Purpose | Command |
|--------|---------|---------|
| `orchestrator.py` | Master coordinator | `--interval 60` |
| `approval_manager.py` | HITL workflow | `list --type pending` |
| `scheduler_setup.py` | Task Scheduler setup | `setup` |

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Gmail IMAP (Recommended - No OAuth!)
GMAIL_EMAIL=your.email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

# Gmail API (Alternative - requires OAuth)
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json

# LinkedIn (optional - for auto-login)
LINKEDIN_EMAIL=your@email.com
LINKEDIN_PASSWORD=your-password
LINKEDIN_SESSION_PATH=./linkedin_session
LINKEDIN_KEYWORDS=message,connection,job,post

# Qwen Code
CLAUDE_COMMAND=claude
MAX_CLAUDE_ITERATIONS=10

# Safe mode (set to false for production)
DRY_RUN=true
LOG_LEVEL=INFO
```

---

## 🧪 Testing

### Quick Verification

```bash
# Test 1: Verify all scripts exist
python -c "from pathlib import Path; scripts=['gmail_imap_watcher.py','linkedin_watcher.py','orchestrator.py','email_auto_responder.py']; print('OK' if all((Path('scripts')/s).exists() for s in scripts) else 'Missing')"

# Test 2: Verify vault structure
python -c "from pathlib import Path; vault=Path('AI_Employee_Vault'); folders=['Inbox','Needs_Action','Done','Plans']; print('OK' if all((vault/f).exists() for f in folders) else 'Missing')"

# Test 3: Verify core files
python -c "from pathlib import Path; vault=Path('AI_Employee_Vault'); files=['Dashboard.md','Company_Handbook.md','Business_Goals.md']; print('OK' if all((vault/f).exists() for f in files) else 'Missing')"

# Test 4: Run full demo
test_silver_tier.bat
```

### Gmail IMAP Test

```bash
# Show setup instructions
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --setup

# Test connection (reads real emails)
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --interval 60

# Clear processed IDs (re-check all emails)
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --clean
```

---

## 📚 Skills Created

| Skill | Purpose | Status |
|-------|---------|--------|
| `gmail-watcher` | Gmail API/IMAP monitoring | ✅ |
| `linkedin-watcher` | LinkedIn monitoring | ✅ |
| `linkedin-poster` | LinkedIn auto-posting | ✅ |
| `email-mcp-server` | Email sending | ✅ |
| `hitl-approval` | Approval workflow | ✅ |
| `claude-reasoning` | Reasoning loop | ✅ |
| `task-scheduler` | Scheduling | ✅ |
| `whatsapp-watcher` | WhatsApp monitoring | ✅ |

Documentation: `.qwen/skills/*/SKILL.md`

---

## 🐛 Troubleshooting

### Gmail IMAP (Recommended Method)

| Issue | Solution |
|-------|----------|
| "IMAP disabled" | Enable in Gmail Settings → Forwarding and POP/IMAP |
| "Invalid credentials" | Check app password (16 chars, no typos) |
| "2FA required" | Enable 2-Step Verification first |

### Gmail OAuth (Alternative)

| Issue | Solution |
|-------|----------|
| "Access denied 403" | Add test user in Google Cloud Console |
| "credentials.json not found" | Download from Google Cloud Console |
| Token expired | Run `python scripts/gmail_auth.py` again |

### General

| Issue | Solution |
|-------|----------|
| "claude: command not found" | `npm install -g @anthropic/claude-code` |
| LinkedIn login fails | Manual login first time, session saved after |
| Python import errors | Activate venv: `venv\Scripts\activate` |
| Playwright error | `playwright install` |

---

## 🔐 Security Notes

- ✅ **NEVER** commit `.env` file
- ✅ **NEVER** store credentials in vault markdown files
- ✅ Use environment variables for all API keys
- ✅ Keep `DRY_RUN=true` during development
- ✅ Review logs regularly in `AI_Employee_Vault/Logs/`
- ✅ Session files stored securely, never committed
- ⚠️ Be aware of LinkedIn/WhatsApp terms of service

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | This file - complete setup guide |
| `QUICK_START.md` | Quick reference for commands |
| `GMAIL_QUICK_FIX.md` | Gmail IMAP setup (detailed) |
| `QWEN.md` | Project configuration |
| `SILVER_TIER_COMPLETE.md` | Silver Tier verification |
| `Company_Handbook.md` | Rules of engagement |
| `Business_Goals.md` | Q1 2026 objectives |

---

## 🎯 Workflow Example

### Email Processing Flow

```
1. Email arrives in Gmail
   ↓
2. Gmail IMAP Watcher detects unread email
   ↓
3. Creates: Needs_Action/EMAIL_*.md
   ↓
4. Orchestrator detects new file
   ↓
5. Creates: Plans/PLAN_*.md
   ↓
6. Email Auto-Responder generates reply
   ↓
7. Saves draft: Pending_Approval/REPLY_*.md
   ↓
8. Human reviews and moves to Approved/
   ↓
9. Send approved: --send-approved flag
   ↓
10. Email sent via Gmail SMTP ✓
    ↓
11. Move to Done/ (archived)
```

---

## 🏆 What's Working Now

✅ **Gmail IMAP Watcher** - Reads real emails (no OAuth!)  
✅ **Email Auto-Responder** - Generates and sends replies  
✅ **LinkedIn Watcher** - Monitors notifications  
✅ **File System Watcher** - Watches for file drops  
✅ **Orchestrator** - Coordinates all components  
✅ **Plan Creation** - Creates Plan.md for each item  
✅ **Approval Workflow** - Pending → Approved → Execute  
✅ **Dashboard Updates** - Real-time status  
✅ **Audit Logging** - All actions logged  

---

## 🚀 Next Steps

### For Production Use:

1. **Set DRY_RUN=false** in `.env` (when ready for real actions)
2. **Configure LinkedIn** credentials for auto-posting
3. **Setup Scheduler** for automated runs:
   ```bash
   python scripts/scheduler_setup.py setup
   ```
4. **Customize** Company_Handbook.md rules
5. **Update** Business_Goals.md with your objectives

### For Gold Tier (Optional):

- [ ] Odoo Community integration (Accounting)
- [ ] Facebook/Instagram integration
- [ ] Twitter (X) integration
- [ ] Weekly Business Audit with CEO Briefing
- [ ] Ralph Wiggum loop for autonomous completion

---

*Built with ❤️ for Hackathon 0 - AI Employee v0.2 (Silver Tier Complete)*

**Last Updated:** 2026-03-02  
**Status:** Production Ready ✅
