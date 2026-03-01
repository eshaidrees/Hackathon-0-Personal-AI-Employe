# Gmail API Setup - Complete Guide

## The Problem
Your Google Cloud project needs proper OAuth setup. Let's fix it step by step.

---

## Solution: Complete Re-Setup (10 minutes)

### Step 1: Open Google Cloud Console

Go to: https://console.cloud.google.com/

### Step 2: Select or Create Project

1. Click the project dropdown at the top
2. Select **hackathon-0-ai** (your existing project)
   - OR create a new project called "ai-employee"

### Step 3: Enable Gmail API

1. In the search bar at top, type: `Gmail API`
2. Click **Gmail API**
3. Click **ENABLE**

### Step 4: Configure OAuth Consent Screen

1. Go to: https://console.cloud.google.com/apis/credentials/consent

2. Fill in the form:
   - **User Type**: Select **External**
   - **App name**: `AI Employee`
   - **User support email**: `esha35319@gmail.com`
   - **Developer contact**: `esha35319@gmail.com`

3. Click **SAVE AND CONTINUE**

4. **Scopes page**: Click **SAVE AND CONTINUE** (skip for now)

5. **Test users page**: 
   - Click **+ ADD USERS**
   - Add: `esha35319@gmail.com`
   - Click **ADD**
   - Click **SAVE AND CONTINUE**

6. Click **BACK TO DASHBOARD**

### Step 5: Create OAuth Credentials

1. Go to: https://console.cloud.google.com/apis/credentials

2. Click **+ CREATE CREDENTIALS**

3. Select **OAuth client ID**

4. **Application type**: Select **Desktop app**

5. **Name**: `AI Employee Desktop`

6. Click **CREATE**

7. **Download the credentials**:
   - Click the **Download** icon (down arrow)
   - Save as `credentials.json`
   - Replace the existing file in your project

### Step 6: Authenticate

```bash
cd C:\Users\PC\Desktop\Hackathon-0-AI-Employe\Personal-AI-Employe
venv\Scripts\activate
python scripts/quick_gmail_auth.py
```

---

## Quick Check: Is OAuth Consent Screen Set Up?

Run this command to see your current setup:

```bash
# Check if you can access the consent screen
# Open in browser:
https://console.cloud.google.com/apis/credentials/consent?project=hackathon-0-ai
```

If you see a blank page or error, you need to create the OAuth consent screen first (Step 4 above).

---

## Alternative: Use Existing Credentials Without Verification

For **development/testing only**, you can use the credentials in "Testing" mode:

1. Your current `credentials.json` is valid
2. The issue is your email isn't added as a test user
3. The OAuth consent screen MUST be configured

### Direct Link to Add Test User:
```
https://console.cloud.google.com/apis/credentials/consent?project=hackathon-0-ai
```

If this page shows an error or is blank, you need to **create a new OAuth consent screen**:

1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. If prompted, select your project: `hackathon-0-ai`
3. Fill in:
   - App name: `AI Employee`
   - User Type: **External**
   - Email: `esha35319@gmail.com`
4. Complete all steps above

---

## Troubleshooting

### "Page not found" or "Project not found"
- Make sure you're logged into the correct Google account
- Verify project exists: https://console.cloud.google.com/project?project=hackathon-0-ai

### "Access denied" after adding test user
- Wait 5 minutes for changes to propagate
- Clear browser cache
- Try incognito/private browsing mode

### Still stuck?
Use the demo mode for now:

```bash
python scripts/gmail_watcher.py --vault ../AI_Employee_Vault --demo
python scripts/orchestrator.py --vault ../AI_Employee_Vault --once --dry-run
```

The Silver Tier is complete - you can demo with sample files while fixing Gmail auth.

---

## Demo Mode Works Without Authentication

You can test the full workflow with demo files:

```bash
# Create demo email
python scripts/gmail_watcher.py --vault ../AI_Employee_Vault --demo

# Create demo LinkedIn
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --demo

# Run orchestrator
python scripts/orchestrator.py --vault ../AI_Employee_Vault --once --dry-run

# Check results
type AI_Employee_Vault\Needs_Action\*.md
type AI_Employee_Vault\Plans\*.md
```

This proves the Silver Tier architecture works. Gmail API auth is just for production use.
