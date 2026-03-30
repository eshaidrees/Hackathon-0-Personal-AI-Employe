# 🚀 AI Employee - Complete Commands Guide

**All commands you need to run your Personal AI Employee**

---

## 📋 Table of Contents

1. [Setup Commands](#1-setup-commands)
2. [Twitter/X Commands](#2-twitterx-commands)
3. [Facebook Commands](#3-facebook-commands)
4. [Instagram Commands](#4-instagram-commands)
5. [LinkedIn Commands](#5-linkedin-commands)
6. [Gmail Commands](#6-gmail-commands)
7. [WhatsApp Commands](#7-whatsapp-commands)
8. [Odoo ERP Commands](#8-odoo-erp-commands)
9. [Watcher Commands](#9-watcher-commands)
10. [Orchestrator Commands](#10-orchestrator-commands)
11. [Audit & Logging Commands](#11-audit--logging-commands)
12. [Utility Commands](#12-utility-commands)

---

## 1. Setup Commands

### Activate Virtual Environment
```bash
cd C:\Users\PC\Desktop\Hackathon-0-AI-Employe\Personal-AI-Employe
venv\Scripts\activate
```

### Create Virtual Environment (First Time Only)
```bash
cd C:\Users\PC\Desktop\Hackathon-0-AI-Employe\Personal-AI-Employe
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Install Playwright Browsers
```bash
playwright install
```

### Verify Installation
```bash
python --version
pip list
```

---

## 2. Twitter/X Commands

### Test Connection (Demo Mode)
```bash
python scripts/twitter_api.py demo
```

### Post a Tweet
```bash
python scripts/twitter_api.py post --text "Your tweet here"
```

### Post a Thread (Multiple Tweets)
```bash
python scripts/twitter_api.py thread --texts "First tweet" "Second tweet" "Third tweet"
```

### View Your Recent Tweets
```bash
python scripts/twitter_api.py tweets --limit 10
```

### View Mentions
```bash
python scripts/twitter_api.py mentions --limit 25
```

### Search Tweets
```bash
python scripts/twitter_api.py search --query "#AI" --limit 10
```

### View Account Metrics
```bash
python scripts/twitter_api.py metrics
```

### Post via Social Media MCP
```bash
python scripts/social_media_mcp.py post --platform twitter --content "Your content here"
```

### Create Draft (Approval Required)
```bash
python scripts/twitter_poster.py --vault ../AI_Employee_Vault --demo
```

### Post Approved Tweets
```bash
python scripts/twitter_poster.py --vault ../AI_Employee_Vault
```

---

## 3. Facebook Commands

### Test Connection (Demo Mode)
```bash
python scripts/facebook_graph_api.py demo
```

### Get Page Info
```bash
python scripts/facebook_graph_api.py info
```

### Post Text Update
```bash
python scripts/facebook_graph_api.py post --message "Your post message here"
```

### Post with Link
```bash
python scripts/facebook_graph_api.py post --message "Check this out!" --link "https://yourwebsite.com"
```

### Post Photo
```bash
python scripts/facebook_graph_api.py photo --photo-url "https://example.com/image.jpg" --caption "Photo caption here"
```

### View Recent Posts
```bash
python scripts/facebook_graph_api.py posts --limit 10
```

### View Page Insights
```bash
python scripts/facebook_graph_api.py insights
```

### View Notifications
```bash
python scripts/facebook_graph_api.py notifications --limit 25
```

### Verify Token
```bash
python scripts/facebook_graph_api.py verify
```

---

## 4. Instagram Commands

### Test Connection (Demo Mode)
```bash
python scripts/instagram_graph_api.py demo
```

### Get Account Info
```bash
python scripts/instagram_graph_api.py info
```

### Post Photo
```bash
python scripts/instagram_graph_api.py photo --image-url "https://example.com/image.jpg" --caption "Your caption here"
```

### Post Video
```bash
python scripts/instagram_graph_api.py video --video-url "https://example.com/video.mp4" --caption "Your caption here"
```

### Post Carousel (Multiple Images)
```bash
python scripts/instagram_graph_api.py carousel --media-urls "https://example.com/img1.jpg" "https://example.com/img2.jpg" --caption "Carousel caption"
```

### View Recent Posts
```bash
python scripts/instagram_graph_api.py posts --limit 10
```

### View Account Insights
```bash
python scripts/instagram_graph_api.py insights
```

### Verify Account
```bash
python scripts/instagram_graph_api.py verify
```

---

## 5. LinkedIn Commands

### Test Connection (Demo Mode)
```bash
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --demo
```

### Run Watcher (Monitor Notifications)
```bash
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --interval 300
```

### Create Demo Post (Approval Required)
```bash
python scripts/linkedin_poster.py --vault ../AI_Employee_Vault --demo
```

### Post Approved Content
```bash
python scripts/linkedin_poster.py --vault ../AI_Employee_Vault
```

---

## 6. Gmail Commands

### Authenticate Gmail (First Time)
```bash
python scripts/gmail_auth.py
```

### Test Connection
```bash
python scripts/gmail_watcher.py --vault ../AI_Employee_Vault --test
```

### Run Watcher (Monitor Emails)
```bash
python scripts/gmail_watcher.py --vault ../AI_Employee_Vault --interval 120
```

### Create Demo Email Action
```bash
python scripts/gmail_watcher.py --vault ../AI_Employee_Vault --demo
```

### Send Email via MCP
```bash
python scripts/email_mcp_server.py demo
```

---

## 7. WhatsApp Commands

### Run Watcher (Monitor Messages)
```bash
python scripts/whatsapp_watcher.py --vault ../AI_Employee_Vault --interval 30
```

### Create Demo Message Action
```bash
python scripts/whatsapp_watcher.py --vault ../AI_Employee_Vault --demo
```

---

## 8. Odoo ERP Commands

### Test Connection (Demo Mode)
```bash
python scripts/odoo_mcp_server.py demo
```

### Authenticate
```bash
python scripts/odoo_mcp_server.py auth
```

### Create Invoice
```bash
python scripts/odoo_mcp_server.py create_invoice --partner-id 1 --amount 1500
```

### Search Business Partner
```bash
python scripts/odoo_mcp_server.py search_partner --name "Client Name"
```

### Create Business Partner
```bash
python scripts/odoo_mcp_server.py create_partner --name "New Client" --email "client@example.com"
```

### Get Invoices
```bash
python scripts/odoo_mcp_server.py get_invoices
```

### Get Account Summary
```bash
python scripts/odoo_mcp_server.py summary
```

---

## 9. Watcher Commands

### Gmail Watcher
```bash
python scripts/gmail_watcher.py --vault ../AI_Employee_Vault --interval 120
```

### LinkedIn Watcher
```bash
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --interval 300
```

### Twitter Watcher
```bash
python scripts/twitter_watcher.py --vault ../AI_Employee_Vault --interval 300
```

### Facebook Watcher
```bash
python scripts/facebook_instagram_watcher.py --platform facebook --vault ../AI_Employee_Vault --interval 300
```

### Instagram Watcher
```bash
python scripts/facebook_instagram_watcher.py --platform instagram --vault ../AI_Employee_Vault --interval 300
```

### File System Watcher
```bash
python scripts/filesystem_watcher.py --vault ../AI_Employee_Vault --interval 30
```

### WhatsApp Watcher
```bash
python scripts/whatsapp_watcher.py --vault ../AI_Employee_Vault --interval 30
```

---

## 10. Orchestrator Commands

### Test Run (Single Cycle, Dry Run)
```bash
python scripts/orchestrator.py --vault ../AI_Employee_Vault --once --dry-run
```

### Continuous Mode (Testing)
```bash
python scripts/orchestrator.py --vault ../AI_Employee_Vault --interval 60
```

### Production Mode (Real Actions)
```bash
python scripts/orchestrator.py --vault ../AI_Employee_Vault --interval 60
```

### Run Weekly Review
```bash
python scripts/orchestrator.py --vault ../AI_Employee_Vault --action weekly-review
```

---

## 11. Audit & Logging Commands

### View Audit Statistics
```bash
python scripts/audit_logger.py --vault ../AI_Employee_Vault stats --days 7
```

### Query Audit Logs
```bash
python scripts/audit_logger.py --vault ../AI_Employee_Vault query --type email_send
```

### Export Audit Trail
```bash
python scripts/audit_logger.py --vault ../AI_Employee_Vault export --output audit_export.json
```

### Cleanup Old Logs
```bash
python scripts/audit_logger.py --vault ../AI_Employee_Vault cleanup
```

### Generate Weekly Briefing
```bash
python scripts/weekly_audit.py --vault ../AI_Employee_Vault
```

### System Health Check
```bash
python scripts/error_recovery.py --vault ../AI_Employee_Vault health
```

### Cleanup Old Errors
```bash
python scripts/error_recovery.py --vault ../AI_Employee_Vault cleanup --days 30
```

---

## 12. Utility Commands

### Ralph Wiggum Loop (Autonomous Tasks)
```bash
python scripts/ralph_wiggum_loop.py --vault ../AI_Employee_Vault --task-id my_task --prompt "Process all pending items" --max-iterations 10
```

### Ralph Loop Demo
```bash
python scripts/ralph_wiggum_loop.py --vault ../AI_Employee_Vault --task-id demo --prompt "Test task" --demo
```

### Setup Scheduled Tasks
```bash
python scripts/scheduler_setup.py setup
```

### List Scheduled Tasks
```bash
python scripts/scheduler_setup.py list
```

### Remove Scheduled Tasks
```bash
python scripts/scheduler_setup.py remove
```

### View Pending Approvals
```bash
python scripts/approval_manager.py --vault ../AI_Employee_Vault list --type pending
```

### Social Media MCP Demo
```bash
python scripts/social_media_mcp.py demo
```

### Social Media MCP - Post to Any Platform
```bash
python scripts/social_media_mcp.py post --platform twitter --content "Your content here"
python scripts/social_media_mcp.py post --platform facebook --content "Your content here"
python scripts/social_media_mcp.py post --platform instagram --content "Your content here"
```

### Social Media MCP - Get Posts
```bash
python scripts/social_media_mcp.py posts --platform twitter --limit 5
python scripts/social_media_mcp.py posts --platform facebook --limit 5
python scripts/social_media_mcp.py posts --platform instagram --limit 5
```

### Social Media MCP - Get Notifications
```bash
python scripts/social_media_mcp.py notifications --platform twitter --limit 10
python scripts/social_media_mcp.py notifications --platform facebook --limit 10
```

### Social Media MCP - Get Insights
```bash
python scripts/social_media_mcp.py insights --platform twitter
python scripts/social_media_mcp.py insights --platform facebook
python scripts/social_media_mcp.py insights --platform instagram
```

---

## 🚀 Quick Start - All in One

### Start All Watchers (Open 7 Terminal Windows)

**Create `start_all.bat`:**

```batch
@echo off
echo Starting AI Employee - All Watchers
echo =====================================

start "Gmail" cmd /k "cd /d %~dp0 && venv\Scripts\activate && python scripts/gmail_watcher.py --vault ../AI_Employee_Vault --interval 120"

start "LinkedIn" cmd /k "cd /d %~dp0 && venv\Scripts\activate && python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --interval 300"

start "Twitter" cmd /k "cd /d %~dp0 && venv\Scripts\activate && python scripts/twitter_watcher.py --vault ../AI_Employee_Vault --interval 300"

start "Facebook" cmd /k "cd /d %~dp0 && venv\Scripts\activate && python scripts/facebook_instagram_watcher.py --platform facebook --vault ../AI_Employee_Vault --interval 300"

start "Instagram" cmd /k "cd /d %~dp0 && venv\Scripts\activate && python scripts/facebook_instagram_watcher.py --platform instagram --vault ../AI_Employee_Vault --interval 300"

start "FileSystem" cmd /k "cd /d %~dp0 && venv\Scripts\activate && python scripts/filesystem_watcher.py --vault ../AI_Employee_Vault --interval 30"

start "Orchestrator" cmd /k "cd /d %~dp0 && venv\Scripts\activate && python scripts/orchestrator.py --vault ../AI_Employee_Vault --interval 60"

echo All watchers started!
pause > nul
```

**Run it:**
```bash
start_all.bat
```

---

## 📊 Command Quick Reference

| Action | Command |
|--------|---------|
| **Post to X/Twitter** | `python scripts/twitter_api.py post --text "Your tweet"` |
| **Post to Facebook** | `python scripts/facebook_graph_api.py post --message "Your post"` |
| **Post to Instagram** | `python scripts/instagram_graph_api.py photo --image-url "URL" --caption "Caption"` |
| **Test All APIs** | `python scripts/social_media_mcp.py demo` |
| **Start All Watchers** | `start_all.bat` |
| **Run Orchestrator** | `python scripts/orchestrator.py --vault ../AI_Employee_Vault --interval 60` |
| **Weekly Briefing** | `python scripts/weekly_audit.py --vault ../AI_Employee_Vault` |
| **Health Check** | `python scripts/error_recovery.py --vault ../AI_Employee_Vault health` |

---

## 🔧 Troubleshooting Commands

### Check Python Version
```bash
python --version
```

### Check Installed Packages
```bash
pip list
```

### Reinstall Dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

### Clear Python Cache
```bash
del /s /q __pycache__
del /s /q *.pyc
```

### Check .env File
```bash
type .env
```

### View Today's Logs
```bash
type AI_Employee_Vault\Logs\%date:~-4,4%-%date:~-7,2%-%date:~-10,2%.json
```

---

## ✅ Daily Workflow

### Morning (8:00 AM)
```bash
# Check dashboard
type AI_Employee_Vault\Dashboard.md

# Check health
python scripts/error_recovery.py --vault ../AI_Employee_Vault health
```

### During Day
```bash
# Post to social media
python scripts/twitter_api.py post --text "Your content"
python scripts/social_media_mcp.py post --platform facebook --content "Your content"
```

### Evening (6:00 PM)
```bash
# Check audit logs
python scripts/audit_logger.py --vault ../AI_Employee_Vault stats --days 1

# Review pending approvals
python scripts/approval_manager.py --vault ../AI_Employee_Vault list --type pending
```

---

**Save this file for quick reference!** 📌

*Last Updated: 2026-03-26*
*AI Employee v0.3 - Gold Tier*
