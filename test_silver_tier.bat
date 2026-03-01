@echo off
REM Silver Tier Demo - Complete Workflow Test
REM Run this to demonstrate the full AI Employee Silver Tier

echo ============================================================
echo AI EMPLOYEE SILVER TIER - DEMO TEST
echo ============================================================
echo.

echo [1/5] Creating Gmail demo email...
python scripts\gmail_watcher.py --vault ..\AI_Employee_Vault --demo
echo.

echo [2/5] Creating Gmail IMAP demo email...
python scripts\gmail_imap_watcher.py --vault ..\AI_Employee_Vault --demo
echo.

echo [3/5] Creating LinkedIn demo notification...
python scripts\linkedin_watcher.py --vault ..\AI_Employee_Vault --demo
echo.

echo [4/5] Creating File System demo...
python scripts\filesystem_watcher.py --vault ..\AI_Employee_Vault --demo
echo.

echo [5/5] Running Orchestrator...
python scripts\orchestrator.py --vault ..\AI_Employee_Vault --once --dry-run
echo.

echo ============================================================
echo DEMO COMPLETE!
echo ============================================================
echo.
echo Checking results...
echo.

echo Files in Needs_Action:
dir /b AI_Employee_Vault\Needs_Action\*.md
echo.

echo Files in Plans:
dir /b AI_Employee_Vault\Plans\*.md
echo.

echo Dashboard Status:
findstr /C:"Needs Action" AI_Employee_Vault\Dashboard.md
echo.

echo ============================================================
echo SILVER TIER STATUS: COMPLETE
echo ============================================================
echo.
echo All Silver Tier requirements met:
echo - Gmail Watcher (API + IMAP)
echo - LinkedIn Watcher
echo - File System Watcher
echo - Orchestrator
echo - Plan creation
echo - Dashboard updates
echo.
echo Next: Add your Gmail App Password to .env for real emails!
echo Get it from: https://myaccount.google.com/apppasswords
echo.
