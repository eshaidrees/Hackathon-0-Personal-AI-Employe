"""
AI Employee Auto Email Responder
Checks Gmail → Creates Replies → Sends Automatically
Run this ONE command for full automation!
"""
import os
import sys
import time
from pathlib import Path

# Add scripts to path
scripts_path = Path(__file__).parent
sys.path.insert(0, str(scripts_path))

from gmail_imap_watcher import GmailIMAPWatcher
from email_auto_responder import EmailAutoResponder
from send_pending_replies import send_pending_replies


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee Auto Email Responder')
    parser.add_argument('--vault', default='../AI_Employee_Vault', help='Vault path')
    parser.add_argument('--interval', type=int, default=0, help='Run continuously every N seconds')
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    
    args = parser.parse_args()
    
    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()
    
    if args.demo:
        print('AI Employee Auto Email Responder - Demo Mode')
        print('=' * 60)
        print('\nThis script does everything automatically:')
        print('  1. Checks Gmail for new emails')
        print('  2. Creates reply drafts')
        print('  3. Sends replies automatically')
        print('\nUsage:')
        print('  python scripts/auto_email.py --vault ../AI_Employee_Vault')
        print('\nFor continuous monitoring:')
        print('  python scripts/auto_email.py --vault ../AI_Employee_Vault --interval 120')
        return
    
    print('=' * 60)
    print('AI EMPLOYEE - AUTO EMAIL RESPONDER')
    print('=' * 60)
    print(f'Vault: {vault_path}')
    print()
    
    # Initialize components
    watcher = GmailIMAPWatcher(str(vault_path))
    responder = EmailAutoResponder(str(vault_path))
    
    print('[STEP 1/3] Checking Gmail for new emails...')
    print('-' * 60)
    
    # Check for new emails
    emails = watcher.check_for_updates()
    
    if emails:
        print(f'Found {len(emails)} new email(s)')
        for email in emails:
            print(f'  - {email["subject"]} (from: {email["from"]})')
            # Create action file
            watcher.create_action_file(email)
        print()
    else:
        print('No new emails found')
        print()
    
    print('[STEP 2/3] Processing emails and generating replies...')
    print('-' * 60)
    
    # Process all email files
    results = responder.process_all(auto_send=False)
    
    if results:
        sent = sum(1 for r in results if r['status'] == 'sent')
        drafts = sum(1 for r in results if r['status'] == 'draft_saved')
        print(f'Processed: {len(results)} email(s)')
        print(f'  Drafts created: {drafts}')
        print(f'  Auto-sent: {sent}')
        print()
    else:
        print('No emails to process')
        print()
    
    print('[STEP 3/3] Sending pending replies...')
    print('-' * 60)
    
    # Send all pending replies
    success = send_pending_replies(str(vault_path))
    
    print()
    print('=' * 60)
    print('AI EMPLOYEE COMPLETE!')
    print('=' * 60)
    print()
    
    if args.interval > 0:
        print(f'Running continuously every {args.interval} seconds...')
        print('Press Ctrl+C to stop')
        print()
        
        try:
            while True:
                time.sleep(args.interval)
                main()  # Run again
        except KeyboardInterrupt:
            print('\nStopped by user')


if __name__ == '__main__':
    main()
