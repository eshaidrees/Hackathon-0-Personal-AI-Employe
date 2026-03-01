# Silver Tier Setup Guide

## Quick Start (5 minutes)

### 1. Install Dependencies

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 2. Setup Gmail API (with your credentials.json)

```bash
# Place your credentials.json in the project directory
# Then run authentication:
python scripts/gmail_auth.py

# Follow the browser prompts to authenticate
# Token will be saved to token.json for reuse
```

### 3. Test Gmail Watcher

```bash
# Test Gmail API connection
python scripts/gmail_watcher.py --vault ../AI_Employee_Vault --test

# Run Gmail Watcher (creates demo file)
python scripts/gmail_watcher.py --vault ../AI_Employee_Vault --demo
```

### 4. Test LinkedIn Watcher

```bash
# Run LinkedIn Watcher demo
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --demo
```

### 5. Run Orchestrator

```bash
# Single cycle (dry-run)
python scripts/orchestrator.py --vault ../AI_Employee_Vault --once --dry-run

# Continuous mode
python scripts/orchestrator.py --vault ../AI_Employee_Vault --interval 60
```

---

## Gmail API Setup (Detailed)

### Step 1: Get credentials.json

You mentioned you already have this file. Place it in the project root:

```
Personal-AI-Employe/
├── credentials.json    ← Place here
├── scripts/
└── AI_Employee_Vault/
```

### Step 2: Authenticate

```bash
python scripts/gmail_auth.py
```

This will:
1. Open your browser
2. Ask you to select your Google account
3. Request Gmail API permissions
4. Save token to `token.json`

### Step 3: Verify

```bash
python scripts/gmail_watcher.py --vault ../AI_Employee_Vault --test
```

Expected output:
```
✓ Gmail API connected
Unread messages: 5
```

---

## LinkedIn Setup (Detailed)

### Step 1: Configure Credentials (Optional)

Add to `.env`:

```
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password
LINKEDIN_SESSION_PATH=./linkedin_session
```

**Note:** Auto-login may not work due to LinkedIn security. Manual login on first run is expected.

### Step 2: First Run (Manual Login)

```bash
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --interval 300
```

When prompted:
1. Browser will open
2. Log in to LinkedIn manually
3. Complete any verification steps
4. Session is saved for future runs

### Step 3: Subsequent Runs

Session is reused. Just run:

```bash
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault
```

---

## Running All Watchers

### Option 1: Multiple Terminals

```bash
# Terminal 1: Gmail Watcher
python scripts/gmail_watcher.py --vault ../AI_Employee_Vault --interval 120

# Terminal 2: LinkedIn Watcher
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --interval 300

# Terminal 3: File System Watcher
python scripts/filesystem_watcher.py --vault ../AI_Employee_Vault --interval 30

# Terminal 4: Orchestrator
python scripts/orchestrator.py --vault ../AI_Employee_Vault --interval 60
```

### Option 2: Background Processes (Windows)

```powershell
# Start Gmail Watcher
Start-Process python -ArgumentList "scripts/gmail_watcher.py --vault ../AI_Employee_Vault" -WindowStyle Hidden

# Start LinkedIn Watcher
Start-Process python -ArgumentList "scripts/linkedin_watcher.py --vault ../AI_Employee_Vault" -WindowStyle Hidden

# Start Orchestrator
Start-Process python -ArgumentList "scripts/orchestrator.py --vault ../AI_Employee_Vault" -WindowStyle Hidden
```

### Option 3: Using PM2 (Cross-platform)

```bash
# Install PM2
npm install -g pm2

# Start watchers
pm2 start scripts/gmail_watcher.py --name gmail --interpreter python -- --vault ../AI_Employee_Vault
pm2 start scripts/linkedin_watcher.py --name linkedin --interpreter python -- --vault ../AI_Employee_Vault
pm2 start scripts/orchestrator.py --name orchestrator --interpreter python -- --vault ../AI_Employee_Vault

# Save PM2 configuration
pm2 save

# Start on boot
pm2 startup
```

---

## Verify Silver Tier Completion

### Checklist

Run these commands to verify:

```bash
# 1. Check all scripts exist
ls scripts/*.py

# Expected: base_watcher.py, gmail_watcher.py, linkedin_watcher.py, 
#           filesystem_watcher.py, orchestrator.py, gmail_auth.py,
#           approval_manager.py, scheduler_setup.py

# 2. Test Gmail API
python scripts/gmail_watcher.py --vault ../AI_Employee_Vault --test

# Expected: ✓ Gmail API connected

# 3. Create demo files
python scripts/gmail_watcher.py --vault ../AI_Employee_Vault --demo
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --demo

# Expected: Demo files created in Needs_Action/

# 4. Run orchestrator
python scripts/orchestrator.py --vault ../AI_Employee_Vault --once --dry-run

# Expected: Processes files, creates Plans
```

### Silver Tier Requirements

- [x] Two or more Watcher scripts (Gmail + LinkedIn + File System)
- [x] LinkedIn auto-posting capability (linkedin_poster.py)
- [x] Claude/Qwen Code reasoning loop with Plan.md creation
- [x] One working MCP server for external action (email_mcp_server.py)
- [x] Human-in-the-loop approval workflow (approval_manager.py)
- [x] Basic scheduling via cron/Task Scheduler (scheduler_setup.py)

---

## Troubleshooting

### Gmail API Issues

**Problem:** `ModuleNotFoundError: No module named 'google'`

**Solution:**
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

**Problem:** `credentials.json not found`

**Solution:** Place your credentials.json in the project root directory.

**Problem:** `Token expired`

**Solution:**
```bash
python scripts/gmail_auth.py  # Re-authenticate
```

### LinkedIn Watcher Issues

**Problem:** `Browser crashes on startup`

**Solution:** Increase check interval:
```bash
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --interval 600
```

**Problem:** `Login fails repeatedly`

**Solution:** LinkedIn may have additional security. Try:
1. Use a dedicated browser profile
2. Complete CAPTCHA if shown
3. Wait 24 hours between attempts

**Problem:** `No notifications detected`

**Solution:** LinkedIn selectors may have changed. Check browser logs for selector updates.

### General Issues

**Problem:** `ImportError: No module named 'playwright'`

**Solution:**
```bash
pip install playwright
playwright install
```

**Problem:** `Vault not found`

**Solution:** Check path is correct:
```bash
python scripts/gmail_watcher.py --vault ../AI_Employee_Vault
# Adjust path relative to script location
```

---

## Next Steps (Gold Tier)

To advance to Gold Tier:

1. **Odoo Integration**: Set up Odoo Community Edition with MCP server
2. **Facebook/Instagram**: Add social media watchers
3. **Twitter/X**: Add Twitter API integration
4. **Weekly Audit**: Implement CEO Briefing generation
5. **Error Recovery**: Add retry logic and graceful degradation
6. **Ralph Wiggum Loop**: Implement autonomous task completion

---

*Silver Tier Setup Guide - AI Employee v0.2*
