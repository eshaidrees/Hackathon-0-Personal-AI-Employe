# 🤖 Personal AI Employee - All Tiers Complete

**Hackathon 0: Building Autonomous FTEs (Full-Time Equivalent) in 2026**

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

A fully autonomous Personal AI Employee that manages your personal and business affairs 24/7 using **Claude Code** (or Qwen Code) and **Obsidian**. This is a production-ready implementation of a "Digital FTE" (Full-Time Equivalent).

**Status:** ✅ **All Tiers Complete (Bronze + Silver + Gold)**

**Version:** 0.3.0

> **The 'Aha!' Moment:** A Digital FTE works nearly 9,000 hours a year vs a human's 2,000. The cost per task reduction (from ~$5.00 to ~$0.50) is an **85–90% cost saving**.

---

## 🏆 Hackathon Tier Declaration

**Tier:** 🥇 **Gold Tier (All Tiers Complete)**

| Tier | Status | Description |
|------|--------|-------------|
| 🥉 Bronze | ✅ Complete | Foundation: Vault, Dashboard, 1+ Watcher |
| 🥈 Silver | ✅ Complete | Functional: 2+ Watchers, MCP, HITL, Scheduling |
| 🥇 Gold | ✅ Complete | Autonomous: Cross-domain, Odoo, Social Media, Weekly Audit, Error Recovery, Ralph Loop |

---

## 🚀 Quick Start

### Step 1: Setup Environment

```bash
cd Personal-AI-Employe

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
playwright install
```

### Step 2: Configure Gmail

**Option A: Gmail IMAP (Recommended - No OAuth)**

1. Enable IMAP in Gmail Settings
2. Enable 2-Factor Authentication
3. Create App Password at https://myaccount.google.com/apppasswords
4. Add to `.env`:
   ```
   GMAIL_EMAIL=your.email@gmail.com
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

**Option B: Gmail OAuth API**

1. Download credentials.json from Google Cloud Console
2. Run authentication:
   ```bash
   python scripts/gmail_auth.py
   ```

### Step 3: Test

```bash
# Run Gmail Watcher
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --interval 120

# Process emails
python scripts/orchestrator.py --vault ../AI_Employee_Vault --once

# Check results
dir AI_Employee_Vault\Needs_Action
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERSONAL AI EMPLOYEE                         │
│                      ALL TIERS (v0.3)                           │
├─────────────────────────────────────────────────────────────────┤
│  PERCEPTION LAYER (Watchers)                                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│
│  │ Gmail    │ │ LinkedIn │ │ WhatsApp │ │ FB/IG    │ │Twitter ││
│  │ Watcher  │ │ Watcher  │ │ Watcher  │ │ Watcher  │ │Watcher ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘│
│  ┌──────────┐                                                  │
│  │ File     │ ← Monitor local file drops                       │
│  │ Watcher  │                                                  │
│  └──────────┘                                                  │
├─────────────────────────────────────────────────────────────────┤
│  MEMORY LAYER (Obsidian Vault)                                  │
│  Dashboard | Handbook | Goals | Needs_Action | Plans | Logs    │
│  /Briefings/ | /Accounting/ | /Logs/audit/                     │
├─────────────────────────────────────────────────────────────────┤
│  REASONING LAYER (Claude Code / Qwen Code)                      │
│  Reads → Thinks → Plans → Executes → Reviews                   │
│  Ralph Wiggum Loop: Autonomous multi-step completion           │
├─────────────────────────────────────────────────────────────────┤
│  ACTION LAYER (MCP Servers + Orchestrator)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│
│  │ Email    │ │ LinkedIn │ │ FB/IG    │ │ Twitter  │ │ Odoo   ││
│  │ MCP      │ │ Poster   │ │ Poster   │ │ Poster   │ │ MCP    ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘│
│  HITL Approval: Pending → Approved → Execute                   │
├─────────────────────────────────────────────────────────────────┤
│  SUPPORT LAYER (Gold Tier)                                      │
│  Audit Logger | Error Recovery | Weekly Audit | Ralph Loop     │
├─────────────────────────────────────────────────────────────────┤
│  SCHEDULING LAYER                                               │
│  Daily Briefings | Weekly Reviews | Health Checks              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Vault Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time status dashboard
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Q1 2026 objectives
├── Inbox/                    # Raw incoming items
├── Needs_Action/             # Items requiring processing
├── Plans/                    # Action plans by Claude/Qwen
├── Pending_Approval/         # Awaiting human decision (HITL)
├── Approved/                 # Ready to execute
├── Rejected/                 # Declined actions
├── Done/                     # Completed archive
├── Logs/                     # Audit logs
│   ├── audit/                # Audit trail (JSONL)
│   ├── errors/               # Error quarantine
│   └── recovery/             # Recovery plans
├── Briefings/                # CEO briefings
│   └── WEEKLY_BRIEFING_*.md  # Weekly reports
├── Accounting/               # Financial records
└── Invoices/                 # Generated invoices
```

---

## ✅ All Tier Requirements - What I Built

### 🥉 Bronze Tier: Foundation (8-12 hours)

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | Obsidian vault with Dashboard.md and Company_Handbook.md | ✅ | AI_Employee_Vault/Dashboard.md, Company_Handbook.md |
| 2 | One working Watcher script | ✅ | gmail_imap_watcher.py, filesystem_watcher.py |
| 3 | Claude Code reading/writing to vault | ✅ | orchestrator.py with Claude/Qwen integration |
| 4 | Basic folder structure: /Inbox, /Needs_Action, /Done | ✅ | All folders created |
| 5 | All AI functionality as Agent Skills | ✅ | .qwen/skills/*/SKILL.md |

**Bronze Files:**
- `AI_Employee_Vault/Dashboard.md`
- `AI_Employee_Vault/Company_Handbook.md`
- `AI_Employee_Vault/Business_Goals.md`
- `scripts/gmail_imap_watcher.py`
- `scripts/filesystem_watcher.py`
- `scripts/orchestrator.py`

---

### 🥈 Silver Tier: Functional Assistant (20-30 hours)

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | All Bronze requirements | ✅ | Complete |
| 2 | Two or more Watcher scripts | ✅ | Gmail + LinkedIn + WhatsApp + File System |
| 3 | LinkedIn auto-posting | ✅ | linkedin_poster.py |
| 4 | Claude reasoning loop with Plan.md | ✅ | orchestrator.py creates Plans/PLAN_*.md |
| 5 | One working MCP server | ✅ | email_mcp_server.py |
| 6 | Human-in-the-loop approval workflow | ✅ | approval_manager.py + Pending_Approval/ folder |
| 7 | Basic scheduling via cron/Task Scheduler | ✅ | scheduler_setup.py |
| 8 | All AI functionality as Agent Skills | ✅ | 8 Silver tier skills documented |

**Silver Files (NEW):**
- `scripts/linkedin_watcher.py`
- `scripts/whatsapp_watcher.py`
- `scripts/linkedin_poster.py`
- `scripts/email_mcp_server.py`
- `scripts/approval_manager.py`
- `scripts/scheduler_setup.py`

---

### 🥇 Gold Tier: Autonomous Employee (40+ hours)

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | All Silver requirements | ✅ | Complete |
| 2 | Full cross-domain integration (Personal + Business) | ✅ | Email + Social Media + ERP integration |
| 3 | Odoo Community integration via MCP | ✅ | odoo_mcp_server.py (JSON-RPC API) |
| 4 | Facebook/Instagram integration | ✅ | facebook_instagram_watcher.py + facebook_instagram_poster.py |
| 5 | Twitter (X) integration | ✅ | twitter_watcher.py + twitter_poster.py |
| 6 | Multiple MCP servers | ✅ | Email MCP + Odoo MCP + Social Media MCP |
| 7 | Weekly Business and Accounting Audit | ✅ | weekly_audit.py → CEO Briefing |
| 8 | Error recovery and graceful degradation | ✅ | error_recovery.py |
| 9 | Comprehensive audit logging | ✅ | audit_logger.py (JSONL, 90-day retention) |
| 10 | Ralph Wiggum loop for autonomous completion | ✅ | ralph_wiggum_loop.py |
| 11 | Documentation of architecture | ✅ | README.md, QWEN.md, .qwen/skills/*/SKILL.md |
| 12 | All AI functionality as Agent Skills | ✅ | 15 total skills documented |

**Gold Files (NEW):**
- `scripts/odoo_mcp_server.py`
- `scripts/facebook_instagram_watcher.py`
- `scripts/facebook_instagram_poster.py`
- `scripts/twitter_watcher.py`
- `scripts/twitter_poster.py`
- `scripts/weekly_audit.py`
- `scripts/audit_logger.py`
- `scripts/error_recovery.py`
- `scripts/ralph_wiggum_loop.py`

---

## 📜 All Scripts Created

### Watchers (Perception Layer)

| Script | Tier | Purpose |
|--------|------|---------|
| `gmail_imap_watcher.py` | Bronze | Gmail via IMAP (no OAuth required) |
| `gmail_watcher.py` | Silver | Gmail via OAuth API |
| `linkedin_watcher.py` | Silver | LinkedIn monitoring via Playwright |
| `whatsapp_watcher.py` | Silver | WhatsApp Web monitoring via Playwright |
| `facebook_instagram_watcher.py` | Gold | Facebook/Instagram monitoring via Graph API |
| `twitter_watcher.py` | Gold | Twitter/X monitoring via API |
| `filesystem_watcher.py` | Bronze | File drop monitoring via Watchdog |

### Actions (Action Layer)

| Script | Tier | Purpose |
|--------|------|---------|
| `email_auto_responder.py` | Silver | Auto-reply to emails |
| `email_mcp_server.py` | Silver | Email MCP server |
| `linkedin_poster.py` | Silver | LinkedIn auto-posting |
| `facebook_instagram_poster.py` | Gold | Facebook/Instagram posting |
| `twitter_poster.py` | Gold | Twitter/X posting |
| `odoo_mcp_server.py` | Gold | Odoo ERP integration (invoices, customers, payments) |

### Coordination & Support

| Script | Tier | Purpose |
|--------|------|---------|
| `orchestrator.py` | Bronze | Master coordinator |
| `approval_manager.py` | Silver | HITL workflow management |
| `scheduler_setup.py` | Silver | Task Scheduler setup |
| `weekly_audit.py` | Gold | Weekly CEO briefing generator |
| `audit_logger.py` | Gold | Comprehensive audit logging |
| `error_recovery.py` | Gold | Error handling & graceful degradation |
| `ralph_wiggum_loop.py` | Gold | Autonomous multi-step task completion |

---

## 🚀 Usage

### Run All Watchers

```bash
# Terminal 1: Gmail Watcher
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --interval 120

# Terminal 2: LinkedIn Watcher
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --interval 300

# Terminal 3: WhatsApp Watcher
python scripts/whatsapp_watcher.py --vault ../AI_Employee_Vault --interval 30

# Terminal 4: Facebook/Instagram Watcher
python scripts/facebook_instagram_watcher.py --platform facebook --vault ../AI_Employee_Vault --interval 300

# Terminal 5: Twitter Watcher
python scripts/twitter_watcher.py --vault ../AI_Employee_Vault --interval 300

# Terminal 6: File System Watcher
python scripts/filesystem_watcher.py --vault ../AI_Employee_Vault --interval 30

# Terminal 7: Orchestrator
python scripts/orchestrator.py --vault ../AI_Employee_Vault --interval 60
```

### Demo Mode (Test Without Real Data)

```bash
# Create demo files
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --demo
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --demo
python scripts/facebook_instagram_watcher.py --platform facebook --vault ../AI_Employee_Vault --demo
python scripts/twitter_watcher.py --vault ../AI_Employee_Vault --demo

# Run orchestrator (dry-run)
python scripts/orchestrator.py --vault ../AI_Employee_Vault --once --dry-run
```

### Weekly CEO Briefing

```bash
# Generate weekly audit
python scripts/weekly_audit.py --vault ../AI_Employee_Vault

# View briefing
type AI_Employee_Vault\Briefings\WEEKLY_BRIEFING_*.md
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Gmail
GMAIL_EMAIL=your.email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

# LinkedIn
LINKEDIN_EMAIL=your@email.com
LINKEDIN_PASSWORD=your-password

# Odoo
ODOO_URL=http://localhost:8069
ODOO_DATABASE=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=your-password

# Facebook/Instagram
FACEBOOK_EMAIL=your@email.com
FACEBOOK_PASSWORD=your-password

# Twitter
TWITTER_EMAIL=your@email.com
TWITTER_USERNAME=your-username
TWITTER_PASSWORD=your-password

# System
CLAUDE_COMMAND=claude
MAX_CLAUDE_ITERATIONS=10
DRY_RUN=true
LOG_LEVEL=INFO
```

---

## 📊 Workflow Example

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
9. Send approved
   ↓
10. Email sent ✓
    ↓
11. Move to Done/ + Audit log created
```

---

## 📚 Agent Skills Created

All AI functionality is implemented as Agent Skills:

### Bronze/Silver Tier Skills

| Skill | Purpose |
|-------|---------|
| `gmail-watcher` | Gmail API/IMAP monitoring |
| `linkedin-watcher` | LinkedIn monitoring |
| `linkedin-poster` | LinkedIn auto-posting |
| `email-mcp-server` | Email sending |
| `hitl-approval` | Approval workflow |
| `claude-reasoning` | Structured reasoning loop |
| `task-scheduler` | Scheduled operations |
| `whatsapp-watcher` | WhatsApp monitoring |

### Gold Tier Skills

| Skill | Purpose |
|-------|---------|
| `odoo-integration` | Odoo ERP operations |
| `facebook-instagram-automation` | FB/IG monitoring & posting |
| `twitter-automation` | Twitter/X monitoring & posting |
| `weekly-audit` | Business accounting audit |
| `audit-logging` | Comprehensive audit trail |
| `error-recovery` | Error handling & degradation |
| `ralph-wiggum-loop` | Autonomous task completion |

Documentation: `.qwen/skills/*/SKILL.md`

---

## 🧪 Testing

### Verify All Tiers

```bash
# Verify all scripts exist
python -c "from pathlib import Path; scripts=['gmail_imap_watcher.py','linkedin_watcher.py','whatsapp_watcher.py','orchestrator.py','email_mcp_server.py','odoo_mcp_server.py','weekly_audit.py','ralph_wiggum_loop.py']; print('OK' if all((Path('scripts')/s).exists() for s in scripts) else 'Missing')"

# Verify vault structure
python -c "from pathlib import Path; vault=Path('AI_Employee_Vault'); folders=['Inbox','Needs_Action','Done','Plans','Briefings','Logs']; print('OK' if all((vault/f).exists() for f in folders) else 'Missing')"

# Verify core files
python -c "from pathlib import Path; vault=Path('AI_Employee_Vault'); files=['Dashboard.md','Company_Handbook.md','Business_Goals.md']; print('OK' if all((vault/f).exists() for f in files) else 'Missing')"
```

### Test Commands by Tier

```bash
# Bronze: Test Gmail Watcher
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --interval 120

# Silver: Test LinkedIn Poster
python scripts/linkedin_poster.py --vault ../AI_Employee_Vault --demo

# Gold: Test Weekly Audit
python scripts/weekly_audit.py --vault ../AI_Employee_Vault

# Gold: Test Audit Logger
python scripts/audit_logger.py --vault ../AI_Employee_Vault stats --days 7

# Gold: Test Error Recovery
python scripts/error_recovery.py --vault ../AI_Employee_Vault health

# Gold: Test Ralph Wiggum Loop
python scripts/ralph_wiggum_loop.py --vault ../AI_Employee_Vault --task-id test_001 --prompt "Process all pending items" --max-iterations 5
```

---

## 🔐 Security

- ✅ NEVER commit `.env` file
- ✅ NEVER commit `credentials.json` or `token.json`
- ✅ NEVER store credentials in vault markdown files
- ✅ Use environment variables for all API keys
- ✅ Keep `DRY_RUN=true` during development
- ✅ Review logs regularly in `AI_Employee_Vault/Logs/`
- ✅ Session files stored securely, never committed

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | This file - setup and usage guide |
| `QWEN.md` | Project configuration |
| `ODOO_SETUP.md` | Odoo ERP setup |
| `ALL_TEST_COMMANDS.md` | Test command reference |
| `COMMANDS_GUIDE.md` | Command usage guide |
| `.qwen/skills/*/SKILL.md` | Skill documentation |

---

## 📝 Hackathon Submission

**Submission Requirements:**

- [x] GitHub repository with complete codebase
- [x] README.md with setup instructions and architecture overview
- [ ] Demo video (5-10 minutes)
- [x] Security disclosure (credentials via .env, never committed)
- [x] Tier declaration: **Gold Tier (All Tiers Complete)**
- [ ] Submit Form: https://forms.gle/JR9T1SJq5rmQyGkGA

**Judging Criteria Alignment:**

| Criterion | Weight | My Implementation |
|-----------|--------|-------------------|
| Functionality | 30% | ✅ All tiers working (Bronze + Silver + Gold) |
| Innovation | 25% | ✅ Cross-domain integration (Personal + Business + Social) |
| Practicality | 20% | ✅ Production-ready, daily usable |
| Security | 15% | ✅ HITL, audit logging, credential management |
| Documentation | 10% | ✅ README, skill docs, architecture diagrams |

---

## 🎓 Learning Resources

- [Claude Code Fundamentals](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows)
- [Obsidian Download](https://obsidian.md/download)
- [MCP Introduction](https://modelcontextprotocol.io/introduction)
- [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Odoo Documentation](https://www.odoo.com/documentation)
- [Ralph Wiggum Pattern](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)

---

*Built for Hackathon 0 - AI Employee v0.3 (All Tiers Complete)*

**Last Updated:** 2026-03-31  
**Status:** Bronze ✅ Silver ✅ Gold ✅  
**Brain:** Claude Code (or Qwen Code)
