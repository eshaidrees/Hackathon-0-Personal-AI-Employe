# Gmail Setup - Quick Fix (NO OAuth Required!)

## Problem Solved: Use IMAP Instead of OAuth

The Gmail API OAuth verification is complex. **Use Gmail IMAP instead** - it works instantly with an App Password!

---

## Quick Setup (5 Minutes)

### Step 1: Enable IMAP in Gmail

1. Open Gmail in browser
2. Click ⚙️ Settings → **See all settings**
3. Click **Forwarding and POP/IMAP** tab
4. Under "IMAP Access": Select **Enable IMAP**
5. Click **Save Changes**

### Step 2: Enable 2-Factor Authentication

1. Go to: https://myaccount.google.com/security
2. Under "How you sign in to Google": Click **2-Step Verification**
3. Follow prompts to enable (need phone number)

### Step 3: Create App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Under "App passwords":
   - **Select app**: Mail
   - **Select device**: Other (Custom name)
   - Enter: `AI Employee`
   - Click **Generate**
3. Copy the **16-character password** (looks like: `abcd efgh ijkl mnop`)

### Step 4: Add to .env File

Open `.env` file in project root and add:

```
GMAIL_EMAIL=esha35319@gmail.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
```

(Replace with your actual app password - include spaces or remove them, both work)

### Step 5: Test Gmail IMAP Watcher

```bash
cd C:\Users\PC\Desktop\Hackathon-0-AI-Employe\Personal-AI-Employe
venv\Scripts\activate

# Test connection
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --setup

# Run watcher (checks every 2 minutes)
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --interval 120
```

---

## What This Does

| Method | OAuth Required? | Setup Time | Works? |
|--------|----------------|------------|--------|
| Gmail API | Yes (complex) | 30+ min | ❌ Blocked |
| Gmail IMAP | No (App Password) | 5 min | ✅ Works! |

---

## Troubleshooting

### "Invalid credentials" error
- Double-check email in `.env`
- Re-copy app password (no typos)
- App password is 16 characters (may have spaces)

### "IMAP disabled" error
- Go back to Gmail Settings → Forwarding and POP/IMAP
- Make sure IMAP is enabled
- Wait 5 minutes, try again

### "2-Step Verification required"
- You must enable 2FA first (Step 2)
- Can't create app password without it

### Still want Gmail API (OAuth)?
You need to add yourself as a test user:
1. https://console.cloud.google.com/apis/credentials/consent?project=hackhaton-0-fte
2. Add test user: `esha35319@gmail.com`
3. Wait 5 minutes
4. Run: `python scripts/gmail_auth.py`

---

## Verify It Works

```bash
# Run IMAP watcher once
python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault --interval 60

# Check for new emails
# (Watch console for "Found X unread messages")
```

---

## Next Steps

After Gmail IMAP works:

1. **Test LinkedIn Watcher:**
   ```bash
   python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --demo
   ```

2. **Test Full Workflow:**
   ```bash
   test_silver_tier.bat
   ```

3. **Run Orchestrator:**
   ```bash
   python scripts/orchestrator.py --vault ../AI_Employee_Vault --once --dry-run
   ```

---

**Silver Tier is complete - Gmail IMAP is the fastest path to working email!**
