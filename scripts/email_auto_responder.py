"""
Email Auto-Responder - Reads emails and sends replies using Qwen Code
Connects Gmail Watcher → Qwen Code → Email MCP
"""
import os
import sys
import imaplib
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class EmailAutoResponder:
    """
    Automatically reads emails and sends replies.
    Uses Qwen Code for generating responses.
    """
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path).resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        
        # Gmail credentials
        self.email = os.getenv('GMAIL_EMAIL', '')
        self.app_password = os.getenv('GMAIL_APP_PASSWORD', '')
        
        # Ensure folders exist
        for folder in [self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        import logging
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def read_email_file(self, filepath: Path) -> dict:
        """Read email action file and extract info."""
        content = filepath.read_text(encoding='utf-8')
        
        # Extract frontmatter
        email_data = {
            'from': '',
            'from_name': '',
            'subject': '',
            'content': '',
            'filepath': filepath
        }
        
        lines = content.split('\n')
        in_content = False
        content_lines = []
        
        for line in lines:
            if line.startswith('from:'):
                email_data['from'] = line.split(':', 1)[1].strip()
            elif line.startswith('from_name:'):
                email_data['from_name'] = line.split(':', 1)[1].strip()
            elif line.startswith('subject:'):
                email_data['subject'] = line.split(':', 1)[1].strip()
            elif line.startswith('## Email Content'):
                in_content = True
            elif in_content and line.startswith('##'):
                break
            elif in_content:
                content_lines.append(line)
        
        email_data['content'] = '\n'.join(content_lines).strip()
        return email_data
    
    def generate_reply(self, email_data: dict) -> str:
        """
        Generate reply using Qwen Code.
        In production, this would call Qwen Code API.
        For now, uses template-based responses.
        """
        subject = email_data['subject'].lower()
        content = email_data['content'].lower()
        
        # Template-based responses (replace with Qwen Code in production)
        if 'invoice' in subject or 'invoice' in content:
            return f"""Dear {email_data['from_name']},

Thank you for your email regarding the invoice.

I'm processing your request and will send the invoice shortly.

Best regards,
AI Employee"""
        
        elif 'hello' in subject or 'hi' in content:
            return f"""Dear {email_data['from_name']},

Thank you for reaching out!

How can I help you today?

Best regards,
AI Employee"""
        
        elif 'meeting' in subject or 'meeting' in content:
            return f"""Dear {email_data['from_name']},

Thank you for your email about the meeting.

I'll check the schedule and get back to you with available times.

Best regards,
AI Employee"""
        
        else:
            return f"""Dear {email_data['from_name']},

Thank you for your email.

I've received your message and will respond shortly.

Best regards,
AI Employee"""
    
    def send_reply(self, to_email: str, subject: str, body: str, 
                   original_subject: str = '') -> bool:
        """
        Send email reply via Gmail SMTP.
        """
        if not self.email or not self.app_password:
            self.logger.error('Gmail credentials not configured')
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = f'Re: {original_subject}' if original_subject else subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Send via SMTP
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
            server.login(self.email, self.app_password)
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f'Reply sent to {to_email}')
            return True
            
        except Exception as e:
            self.logger.error(f'Failed to send reply: {e}')
            return False
    
    def process_email(self, filepath: Path, auto_send: bool = False) -> dict:
        """
        Process a single email file.
        
        Args:
            filepath: Path to email action file
            auto_send: If True, send reply automatically
            
        Returns:
            Processing result dict
        """
        result = {
            'file': filepath.name,
            'status': 'pending',
            'reply_sent': False,
            'reply_content': ''
        }
        
        try:
            # Read email
            self.logger.info(f'Reading: {filepath.name}')
            email_data = self.read_email_file(filepath)
            
            # Generate reply
            self.logger.info('Generating reply...')
            reply = self.generate_reply(email_data)
            result['reply_content'] = reply
            
            # Extract recipient email
            to_email = email_data['from'].split('<')[-1].split('>')[0] if '<' in email_data['from'] else email_data['from']
            
            # Send or save reply
            if auto_send:
                self.logger.info('Sending reply...')
                success = self.send_reply(
                    to_email, 
                    reply, 
                    email_data['subject']
                )
                result['reply_sent'] = success
                result['status'] = 'sent' if success else 'failed'
            else:
                # Save draft reply
                draft_path = self.vault_path / 'Pending_Approval' / f'REPLY_{filepath.stem}.md'
                draft_path.parent.mkdir(parents=True, exist_ok=True)
                
                draft_content = f"""---
type: email_reply
to: {to_email}
subject: Re: {email_data['subject']}
original_file: {filepath.name}
status: draft
---

# Email Reply Draft

## To: {to_email}
## Subject: Re: {email_data['subject']}

{reply}

---
*Move to Approved/ to send*
"""
                draft_path.write_text(draft_content, encoding='utf-8')
                result['status'] = 'draft_saved'
                self.logger.info(f'Draft saved: {draft_path.name}')
            
            # Move to Done
            if result['status'] in ['sent', 'draft_saved']:
                dest = self.done / filepath.name
                filepath.rename(dest)
                self.logger.info(f'Moved to Done: {dest.name}')
            
            return result
            
        except Exception as e:
            self.logger.error(f'Error processing {filepath.name}: {e}')
            result['status'] = 'error'
            result['error'] = str(e)
            return result
    
    def process_all(self, auto_send: bool = False) -> list:
        """
        Process all email files in Needs_Action.

        Args:
            auto_send: If True, send replies automatically
        """
        results = []

        if not self.needs_action.exists():
            self.logger.warning('Needs_Action folder not found')
            return results

        # Get all email files
        email_files = list(self.needs_action.glob('EMAIL_*.md'))

        if not email_files:
            self.logger.info('No email files to process')
            return results

        self.logger.info(f'Found {len(email_files)} email files')

        for filepath in email_files:
            result = self.process_email(filepath, auto_send)
            results.append(result)

        # Summary
        sent = sum(1 for r in results if r['status'] == 'sent')
        drafts = sum(1 for r in results if r['status'] == 'draft_saved')
        errors = sum(1 for r in results if r['status'] == 'error')

        self.logger.info(f'Processed: {len(results)} emails')
        self.logger.info(f'Sent: {sent}, Drafts: {drafts}, Errors: {errors}')

        return results

    def send_approved_drafts(self) -> list:
        """
        Send all approved reply drafts from Approved folder.
        """
        results = []
        approved_path = self.vault_path / 'Approved'

        if not approved_path.exists():
            self.logger.warning('Approved folder not found')
            return results

        # Get all reply draft files
        draft_files = list(approved_path.glob('REPLY_*.md'))

        if not draft_files:
            self.logger.info('No approved drafts to send')
            return results

        self.logger.info(f'Found {len(draft_files)} approved drafts')

        for filepath in draft_files:
            result = self.send_approved_draft(filepath)
            results.append(result)

        # Summary
        sent = sum(1 for r in results if r.get('sent') == True)
        errors = sum(1 for r in results if r.get('sent') == False)

        self.logger.info(f'Sent: {sent}, Errors: {errors}')

        return results

    def send_approved_draft(self, filepath: Path) -> dict:
        """
        Send a single approved draft.

        Args:
            filepath: Path to approved draft file

        Returns:
            Result dict with send status
        """
        result = {
            'file': filepath.name,
            'sent': False,
            'error': None
        }

        try:
            # Read draft
            content = filepath.read_text(encoding='utf-8')

            # Extract reply info
            to_email = ''
            subject = ''
            body = ''

            lines = content.split('\n')
            in_body = False
            body_lines = []

            for line in lines:
                if line.startswith('to:'):
                    to_email = line.split(':', 1)[1].strip()
                elif line.startswith('subject:'):
                    subject = line.split(':', 1)[1].strip()
                elif line.startswith('## Subject:') or line.startswith('## To:'):
                    continue
                elif line.startswith('Dear ') or line.startswith('Best regards,') or in_body:
                    in_body = True
                    body_lines.append(line)

            body = '\n'.join(body_lines).strip()

            if not to_email or not body:
                result['error'] = 'Missing to_email or body'
                self.logger.error(f'Invalid draft: {filepath.name}')
                return result

            # Send email
            self.logger.info(f'Sending to {to_email}...')
            success = self.send_reply(to_email, body, subject)

            if success:
                result['sent'] = True
                # Move to Done
                dest = self.done / filepath.name
                filepath.rename(dest)
                self.logger.info(f'Moved to Done: {dest.name}')
            else:
                result['error'] = 'SMTP send failed'

            return result

        except Exception as e:
            self.logger.error(f'Error sending {filepath.name}: {e}')
            result['error'] = str(e)
            return result


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Email Auto-Responder')
    parser.add_argument('--vault', default='../AI_Employee_Vault', help='Vault path')
    parser.add_argument('--auto-send', action='store_true', 
                       help='Send replies automatically (no approval)')
    parser.add_argument('--send-approved', action='store_true',
                       help='Send approved drafts from Approved folder')
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    
    args = parser.parse_args()
    
    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()
    
    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        sys.exit(1)
    
    responder = EmailAutoResponder(str(vault_path))
    
    if args.demo:
        print('Email Auto-Responder Demo')
        print('=' * 60)
        print('\nThis script reads email files and generates replies.')
        print('\nModes:')
        print('  Default: Generate draft replies (saved to Pending_Approval/)')
        print('  --auto-send: Send replies immediately via Gmail')
        print('  --send-approved: Send drafts from Approved/ folder')
        print('\nExample:')
        print('  python scripts/email_auto_responder.py --vault ../AI_Employee_Vault')
        print('  python scripts/email_auto_responder.py --vault ../AI_Employee_Vault --auto-send')
        print('  python scripts/email_auto_responder.py --vault ../AI_Employee_Vault --send-approved')
        return
    
    print('Email Auto-Responder')
    print('=' * 60)
    print(f'Vault: {vault_path}')
    print(f'Gmail configured: {bool(responder.email and responder.app_password)}')
    print()
    
    if not responder.email or not responder.app_password:
        print('WARNING: Gmail credentials not configured!')
        print('Add to .env:')
        print('  GMAIL_EMAIL=your.email@gmail.com')
        print('  GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx')
        print()
        print('Will create draft replies only.')
        print()
    
    # Send approved drafts
    if args.send_approved:
        print('Sending approved drafts...')
        results = responder.send_approved_drafts()
        if results:
            print('\nResults:')
            print('-' * 60)
            for r in results:
                status_icon = '[SENT]' if r.get('sent') else '[ERROR]'
                print(f'{status_icon} {r["file"]}: {"sent" if r.get("sent") else r.get("error")}')
        else:
            print('\nNo approved drafts to send.')
        return
    
    # Process emails from Needs_Action
    results = responder.process_all(args.auto_send)
    
    if results:
        print('\nResults:')
        print('-' * 60)
        for r in results:
            status_icon = '[SENT]' if r['status'] == 'sent' else '[DRAFT]' if r['status'] == 'draft_saved' else '[ERROR]'
            print(f'{status_icon} {r["file"]}: {r["status"]}')
    else:
        print('\nNo emails to process.')


if __name__ == '__main__':
    main()
