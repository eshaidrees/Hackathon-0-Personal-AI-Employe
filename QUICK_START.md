
# 🚀 AI Employee - Quick Start Guide

## ✅ Silver Tier Status: COMPLETE

All Silver Tier requirements are implemented and working:
- ✅ Gmail Watcher (API + IMAP)
- ✅ LinkedIn Watcher (Playwright)
- ✅ File System Watcher (Watchdog)
- ✅ Orchestrator with Plan.md creation
- ✅ Email MCP Server
- ✅ HITL Approval Workflow
- ✅ Task Scheduler Setup

---

## ⚡ Quick Start (15 Minutes)

### Step 1: Activate Virtual Environment

```bash
cd C:\Users\PC\Desktop\Hackathon-0-AI-Employe\Personal-AI-Employe
venv\Scripts\activate
```

### Step 2: Configure Gmail (IMAP Method - NO OAuth!)

**This is the FIX for your authentication error!**

Instead of complex OAuth verification, use Gmail IMAP with App Password:

1. **Enable IMAP in Gmail:**
   - Gmail Settings → See all settings → Forwarding and POP/IMAP
   - Enable IMAP → Save Changes

2. **Enable 2-Factor Authentication:**
   - https://myaccount.google.com/security
   - Enable 2-Step Verification

3. **Create App Password:**
   - https://myaccount.google.com/apppasswords
   - App: Mail | Device: Other (AI Employee)
   - Copy 16-character password

4. **Add to .env file:**
   ```
   GMAIL_EMAIL=esha35319@gmail.com
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

### Step 3: Test Demo Mode

```bash
# Run the Silver Tier test
test_silver_tier.bat
```

Expected output:
```
✓ Demo files created in Needs_Action/
✓ Plan files created in Plans/
✓ Dashboard updated
SILVER TIER STATUS: COMPLETE
```

### Step 4: Run Real Gmail Watcher

```bash
# Test Gmail IMAP (reads your actual emails)
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --interval 120
```

### Step 5: Run LinkedIn Watcher (Demo)

```bash
# Demo mode first
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --demo

# Real mode (requires LinkedIn login)
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --interval 300
```

### Step 6: Run Orchestrator

```bash
# Single cycle (dry-run)
python scripts/orchestrator.py --vault ../AI_Employee_Vault --once --dry-run

# Continuous mode
python scripts/orchestrator.py --vault ../AI_Employee_Vault --interval 60
```

---

## 📁 Project Structure

```
Personal-AI-Employe/
├── scripts/                    # All automation scripts
│   ├── gmail_imap_watcher.py   # Gmail via IMAP (RECOMMENDED)
│   ├── gmail_watcher.py        # Gmail via OAuth API
│   ├── gmail_auth.py           # OAuth authentication (not needed for IMAP)
│   ├── linkedin_watcher.py     # LinkedIn monitoring
│   ├── linkedin_poster.py      # LinkedIn auto-posting
│   ├── filesystem_watcher.py   # File drop monitoring
│   ├── orchestrator.py         # Master coordinator
│   ├── email_mcp_server.py     # Email sending
│   ├── approval_manager.py     # Approval workflow
│   └── scheduler_setup.py      # Cron/Task Scheduler setup
├── AI_Employee_Vault/          # Obsidian vault
│   ├── Dashboard.md            # Real-time status
│   ├── Company_Handbook.md     # Rules of engagement
│   ├── Business_Goals.md       # Q1 2026 objectives
│   ├── Inbox/                  # Raw incoming items
│   ├── Needs_Action/           # Items to process
│   ├── Plans/                  # AI-generated plans
│   ├── Pending_Approval/       # Awaiting human decision
│   ├── Approved/               # Ready to execute
│   ├── Done/                   # Completed archive
│   └── Logs/                   # Audit logs
├── .env                        # Environment variables (DO NOT COMMIT)
├── credentials.json            # Gmail OAuth (only if using API method)
└── README.md                   # This file
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Gmail IMAP (Recommended - No OAuth!)
GMAIL_EMAIL=esha35319@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password

# Claude Code
CLAUDE_COMMAND=claude
MAX_CLAUDE_ITERATIONS=10

# Safe mode (set to false for production)
DRY_RUN=true
```

### LinkedIn Setup (Optional)

For LinkedIn auto-posting:

```bash
# Add to .env
LINKEDIN_EMAIL=your@email.com
LINKEDIN_PASSWORD=your-password
```

First run will require manual login, then session is saved.

---

## 🎯 Common Commands

### Gmail

```bash
# IMAP method (recommended)
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --interval 120

# Show IMAP setup instructions
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --setup

# Clear processed emails (re-check all)
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --clean

# OAuth method (not recommended - requires verification)
python scripts/gmail_auth.py
python scripts/gmail_watcher.py --vault ../AI_Employee_Vault --interval 120
```

### LinkedIn

```bash
# Demo mode
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --demo

# Real monitoring
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --interval 300

# Create demo post
python scripts/linkedin_poster.py --vault ../AI_Employee_Vault --demo
```

### File System

```bash
# Monitor Inbox folder for file drops
python scripts/filesystem_watcher.py --vault ../AI_Employee_Vault --interval 30
```

### Orchestrator

```bash
# Single cycle
python scripts/orchestrator.py --vault ../AI_Employee_Vault --once --dry-run

# Continuous mode (every 60 seconds)
python scripts/orchestrator.py --vault ../AI_Employee_Vault --interval 60
```

### Scheduler

```bash
# Setup scheduled tasks
python scripts/scheduler_setup.py setup

# List scheduled tasks
python scripts/scheduler_setup.py list

# Remove scheduled tasks
python scripts/scheduler_setup.py remove
```

---

## 🔄 Workflow Example

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
6. Triggers Claude Code reasoning
   ↓
7. If approval needed: Pending_Approval/APPROVAL_*.md
   ↓
8. Human moves to Approved/
   ↓
9. Email MCP sends reply
   ↓
10. Move to Done/
```

---

## 🛠️ Troubleshooting

### Gmail IMAP Not Working

| Error | Solution |
|-------|----------|
| "IMAP disabled" | Enable in Gmail Settings → Forwarding and POP/IMAP |
| "Invalid credentials" | Check app password (16 chars, no typos) |
| "2FA required" | Enable 2-Step Verification first |

### LinkedIn Not Working

| Error | Solution |
|-------|----------|
| "Login failed" | Manual login first time, session saved after |
| "Element not found" | LinkedIn UI changed, update selectors |

### Orchestrator Issues

| Error | Solution |
|-------|----------|
| "Claude not found" | Install: `npm install -g @anthropic/claude-code` |
| "Vault not found" | Check path: use `../AI_Employee_Vault` |

### General

```bash
# Check all scripts exist
dir scripts\*.py

# Check vault folders
dir AI_Employee_Vault\

# View logs
type AI_Employee_Vault\Logs\*.json
```

---

## 📊 Silver Tier Checklist

| Requirement | Script | Status |
|-------------|--------|--------|
| Gmail Watcher | `gmail_imap_watcher.py` | ✅ |
| LinkedIn Watcher | `linkedin_watcher.py` | ✅ |
| File System Watcher | `filesystem_watcher.py` | ✅ |
| Reasoning Loop | `orchestrator.py` | ✅ |
| MCP Server | `email_mcp_server.py` | ✅ |
| Approval Workflow | `approval_manager.py` | ✅ |
| Task Scheduling | `scheduler_setup.py` | ✅ |

---

## 🎓 Next Steps

### For Production Use:

1. **Set DRY_RUN=false** in .env (when ready for real actions)
2. **Configure LinkedIn** credentials for auto-posting
3. **Setup Scheduler** for automated runs:
   ```bash
   python scripts/scheduler_setup.py setup
   ```
4. **Review Company_Handbook.md** and customize rules
5. **Update Business_Goals.md** with your objectives

### For Gold Tier:

- [ ] Odoo Community integration (Accounting)
- [ ] Facebook/Instagram integration
- [ ] Twitter (X) integration
- [ ] Weekly Business Audit with CEO Briefing
- [ ] Ralph Wiggum loop for autonomous completion

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | This quick start guide |
| `QWEN.md` | Project configuration reference |
| `SILVER_TIER_COMPLETE.md` | Silver Tier verification |
| `GMAIL_QUICK_FIX.md` | Gmail IMAP setup (detailed) |
| `Company_Handbook.md` | Rules of engagement |
| `Business_Goals.md` | Q1 2026 objectives |

---

## 🎉 You're Ready!

**Silver Tier is COMPLETE and WORKING!**

To start using your AI Employee:

```bash
# 1. Add Gmail App Password to .env
# 2. Run watchers
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --interval 120 &
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --interval 300 &
python scripts/filesystem_watcher.py --vault ../AI_Employee_Vault --interval 30 &

# 3. Run orchestrator
python scripts/orchestrator.py --vault ../AI_Employee_Vault --interval 60
```

---

*AI Employee v0.2 - Silver Tier Complete*
*Hackathon 0 - Building Autonomous FTEs in 2026*
