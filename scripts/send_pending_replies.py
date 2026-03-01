"""
Send Pending Replies - Sends all draft replies in Pending_Approval folder
"""
import os
import sys
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()


def send_pending_replies(vault_path: str):
    """Send all pending email replies."""
    
    vault = Path(vault_path).resolve()
    pending = vault / 'Pending_Approval'
    done = vault / 'Done'
    
    email_addr = os.getenv('GMAIL_EMAIL', '')
    app_password = os.getenv('GMAIL_APP_PASSWORD', '')
    
    if not email_addr or not app_password:
        print('ERROR: Gmail credentials not configured!')
        print('Add to .env:')
        print('  GMAIL_EMAIL=your.email@gmail.com')
        print('  GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx')
        return False
    
    if not pending.exists():
        print('No Pending_Approval folder found')
        return False
    
    # Find all reply drafts
    reply_files = list(pending.glob('REPLY_EMAIL_*.md'))
    
    if not reply_files:
        print('No pending replies found')
        return False
    
    print(f'Found {len(reply_files)} pending reply(ies)')
    print('=' * 60)
    
    sent = 0
    failed = 0
    
    for filepath in reply_files:
        content = filepath.read_text(encoding='utf-8')
        
        # Extract reply info
        to_email = ''
        subject = ''
        body = ''
        
        for line in content.split('\n'):
            if line.startswith('to:'):
                to_email = line.split(':', 1)[1].strip()
            elif line.startswith('subject:'):
                subject = line.split(':', 1)[1].strip()
            elif line.startswith('## Subject:'):
                subject = line.split(':', 1)[1].strip()
        
        # Extract body (after "# Email Reply Draft")
        in_body = False
        body_lines = []
        for line in content.split('\n'):
            if line.startswith('## To:'):
                in_body = True
                continue
            if in_body and line.startswith('---'):
                break
            if in_body and line.strip():
                body_lines.append(line)
        
        body = '\n'.join(body_lines).strip()
        
        # Send email
        print(f'Sending to: {to_email}')
        print(f'Subject: {subject}')
        print('-' * 60)
        
        try:
            # Create message
            msg = MIMEText(body, 'plain')
            msg['From'] = email_addr
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Send via Gmail SMTP
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
            server.login(email_addr, app_password)
            server.send_message(msg)
            server.quit()
            
            print(f'[SENT] to {to_email}')
            
            # Move to Done
            dest = done / filepath.name
            filepath.rename(dest)
            print(f'  Moved to Done: {dest.name}')
            print()
            
            sent += 1
            
        except Exception as e:
            print(f'[FAILED] {e}')
            print()
            failed += 1
    
    print('=' * 60)
    print(f'Sent: {sent}, Failed: {failed}')
    
    return sent > 0


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Send Pending Email Replies')
    parser.add_argument('--vault', default='../AI_Employee_Vault', help='Vault path')
    parser.add_argument('--demo', action='store_true', help='Demo mode (show only)')
    
    args = parser.parse_args()
    
    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()
    
    if args.demo:
        print('Send Pending Replies - Demo Mode')
        print('=' * 60)
        print('\nThis script sends all draft replies in Pending_Approval/')
        print('\nUsage:')
        print('  python scripts/send_pending_replies.py --vault ../AI_Employee_Vault')
        print('\nWhat it does:')
        print('  1. Reads all REPLY_*.md files from Pending_Approval/')
        print('  2. Sends each reply via Gmail SMTP')
        print('  3. Moves sent replies to Done/')
        sys.exit(0)

    print('Send Pending Replies')
    print('=' * 60)
    
    success = send_pending_replies(str(vault_path))
    
    if success:
        print('\n[SUCCESS] Replies sent successfully!')
    else:
        print('\n[FAILED] No replies sent')
    
    sys.exit(0 if success else 1)
