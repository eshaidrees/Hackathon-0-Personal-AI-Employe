"""
Gmail IMAP Watcher - Monitors Gmail using IMAP (No OAuth verification needed)
Uses App Password instead of OAuth2
FIXED: Prevents duplicates, faster connection, marks as read
"""
import os
import sys
import email
import imaplib
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

# Load environment variables
load_dotenv()


class GmailIMAPWatcher(BaseWatcher):
    """
    Gmail Watcher using IMAP protocol.
    No OAuth verification required - uses App Password.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 120,
                 email_address: str = None, app_password: str = None):
        """
        Initialize Gmail IMAP Watcher.
        """
        super().__init__(vault_path, check_interval)
        
        self.email_address = email_address or os.getenv('GMAIL_EMAIL', '')
        self.app_password = app_password or os.getenv('GMAIL_APP_PASSWORD', '')
        self.imap_server = 'imap.gmail.com'
        self.imap_port = 993
        
        # Track processed message IDs in a file for persistence
        self.processed_file = self.vault_path / 'Logs' / 'gmail_processed.txt'
        self._load_processed_ids()
        
        self.logger.info(f'IMAP Server: {self.imap_server}')
        self.logger.info(f'Email: {self.email_address}')
        self.logger.info(f'Processed IDs file: {self.processed_file}')
    
    def _load_processed_ids(self):
        """Load processed message IDs from file."""
        if self.processed_file.exists():
            try:
                content = self.processed_file.read_text()
                self.processed_ids = set(content.strip().split('\n'))
                self.processed_ids.discard('')  # Remove empty strings
                self.logger.info(f'Loaded {len(self.processed_ids)} processed IDs')
            except Exception as e:
                self.logger.warning(f'Could not load processed IDs: {e}')
                self.processed_ids = set()
        else:
            self.processed_ids = set()
    
    def _save_processed_ids(self):
        """Save processed message IDs to file."""
        self.processed_file.parent.mkdir(parents=True, exist_ok=True)
        self.processed_file.write_text('\n'.join(self.processed_ids))
    
    def _add_processed_id(self, msg_id: str):
        """Add message ID to processed set and save."""
        self.processed_ids.add(msg_id)
        self._save_processed_ids()
    
    def connect_imap(self):
        """Connect to Gmail IMAP server with timeout."""
        try:
            if not self.email_address or not self.app_password:
                self.logger.error('Gmail credentials not configured')
                return None
            
            # Connect with timeout
            self.logger.debug('Connecting to Gmail IMAP...')
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port, timeout=10)
            mail.login(self.email_address, self.app_password)
            mail.select('inbox')
            
            self.logger.debug('Connected to Gmail IMAP')
            return mail
            
        except imaplib.IMAP4.error as e:
            self.logger.error(f'IMAP login failed: {e}')
            return None
        except Exception as e:
            self.logger.error(f'IMAP connection error: {e}')
            return None
    
    def check_for_updates(self) -> list:
        """
        Check for new unread Gmail messages via IMAP.
        """
        if not self.email_address or not self.app_password:
            self.logger.debug('Gmail IMAP not configured, skipping check')
            return []
        
        mail = None
        new_messages = []
        
        try:
            mail = self.connect_imap()
            if not mail:
                return []
            
            # Search for unread messages (UNSEEN)
            self.logger.debug('Searching for UNSEEN messages...')
            status, messages = mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                self.logger.warning('Search failed')
                return []
            
            message_ids = messages[0].split()
            self.logger.info(f'Found {len(message_ids)} unread messages')
            
            # Process only recent messages (last 10)
            recent_ids = message_ids[-10:] if len(message_ids) > 10 else message_ids
            
            for msg_id in recent_ids:
                msg_id_str = msg_id.decode('utf-8')
                
                # Skip if already processed
                if msg_id_str in self.processed_ids:
                    self.logger.debug(f'Skipping already processed: {msg_id_str}')
                    continue
                
                # Fetch message headers only (faster)
                status, msg_data = mail.fetch(msg_id, '(RFC822.HEADER)')
                
                if status != 'OK':
                    self.logger.warning(f'Fetch failed for {msg_id_str}')
                    continue
                
                # Parse headers
                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                # Extract headers
                subject = email_message.get('Subject', 'No Subject')
                from_header = email_message.get('From', 'Unknown')
                to_header = email_message.get('To', '')
                date_header = email_message.get('Date', '')
                
                new_messages.append({
                    'id': msg_id_str,
                    'from': from_header,
                    'to': to_header,
                    'subject': subject,
                    'date': date_header,
                    'snippet': self._decode_snippet(email_message)
                })
            
            return new_messages
            
        except Exception as e:
            self.logger.error(f'IMAP check error: {e}')
            return []
        finally:
            if mail:
                try:
                    mail.close()
                    mail.logout()
                    self.logger.debug('Disconnected from Gmail')
                except:
                    pass
    
    def _decode_snippet(self, email_message) -> str:
        """Get email snippet/body preview."""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        try:
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            return body[:200]  # First 200 chars
                        except:
                            pass
            else:
                try:
                    body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                    return body[:200]
                except:
                    pass
        except:
            pass
        
        return email_message.get('Subject', 'No content')
    
    def create_action_file(self, message) -> Path:
        """Create action file for a Gmail message."""
        # Check if file already exists (prevent duplicates)
        existing = list(self.needs_action.glob(f'EMAIL_{message["id"]}_*.md'))
        if existing:
            self.logger.info(f'Action file already exists for message {message["id"]}')
            return existing[0]
        
        filename = self.generate_filename('EMAIL', message['id'])
        filepath = self.needs_action / filename
        
        # Extract sender name
        from_email = message['from']
        from_name = from_email.split('<')[0].strip() if '<' in from_email else from_email
        
        content = f'''---
type: email
from: {from_email}
from_name: {from_name}
to: {message.get('to', 'me')}
subject: {message['subject']}
received: {datetime.now().isoformat()}
message_id: IMAP_{message['id']}
priority: normal
status: pending
---

# Email: {message['subject']}

## Header Information
- **From:** {from_email}
- **To:** {message.get('to', 'me')}
- **Received:** {message.get('date', datetime.now().isoformat())}

## Email Content
{message.get('snippet', 'Content not available')}

## Suggested Actions
- [ ] Read and categorize
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing

## Notes
<!-- Add any notes or context here -->

---
*Created by Gmail IMAP Watcher - AI Employee v0.2*
'''
        
        filepath.write_text(content, encoding='utf-8')
        
        # Mark as processed
        self._add_processed_id(message['id'])
        
        self.logger.info(f'Created action file: {filepath.name}')
        return filepath
    
    def mark_email_as_read(self, message_id: str):
        """Mark email as read in Gmail."""
        mail = None
        try:
            mail = self.connect_imap()
            if not mail:
                return False
            
            # Mark as \\Seen (read)
            mail.store(message_id.encode('utf-8'), '+FLAGS', '\\Seen')
            self.logger.debug(f'Marked message {message_id} as read')
            return True
            
        except Exception as e:
            self.logger.error(f'Error marking as read: {e}')
            return False
        finally:
            if mail:
                try:
                    mail.close()
                    mail.logout()
                except:
                    pass
    
    def demo_mode_create_sample(self) -> Path:
        """Create demo email file."""
        filename = self.generate_filename('EMAIL', 'DEMO_IMAP')
        filepath = self.needs_action / filename
        
        content = '''---
type: email
from: demo@gmail.com
from_name: Demo User
to: me
subject: [DEMO] Gmail IMAP Test Email
received: 2026-02-28T10:00:00Z
message_id: IMAP_DEMO001
priority: normal
status: pending
---

# Email: [DEMO] Gmail IMAP Test Email

## Header Information
- **From:** demo@gmail.com
- **To:** me
- **Received:** 2026-02-28 10:00 AM

## Email Content
This is a demo email created by Gmail IMAP Watcher.

This method uses IMAP protocol instead of Gmail API,
so it doesn't require OAuth verification!

## Suggested Actions
- [ ] Acknowledge this is a demo
- [ ] Move to Done folder to complete

## Notes
IMAP method works without Google Cloud Console setup.
Just need Gmail App Password.

---
*Created by Gmail IMAP Watcher (Demo Mode) - AI Employee v0.2*
'''
        
        filepath.write_text(content, encoding='utf-8')
        self.logger.info('Created demo email action file')
        return filepath


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Gmail IMAP Watcher')
    parser.add_argument('--vault', default='../AI_Employee_Vault', help='Vault path')
    parser.add_argument('--interval', type=int, default=120, help='Check interval')
    parser.add_argument('--email', help='Gmail address')
    parser.add_argument('--app-password', help='Gmail App Password')
    parser.add_argument('--demo', action='store_true', help='Create demo file')
    parser.add_argument('--setup', action='store_true', help='Show setup instructions')
    parser.add_argument('--clean', action='store_true', help='Clear processed IDs and re-check')
    
    args = parser.parse_args()
    
    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()
    
    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        sys.exit(1)
    
    if args.setup:
        print("""
GMAIL IMAP SETUP (No OAuth Required!)
======================================

1. Enable IMAP in Gmail:
   - Go to Gmail Settings → See all settings
   - Click 'Forwarding and POP/IMAP' tab
   - Select 'Enable IMAP'
   - Click 'Save Changes'

2. Enable 2-Factor Authentication:
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification

3. Create App Password:
   - Go to: https://myaccount.google.com/apppasswords
   - Select 'Mail' and your device
   - Click 'Generate'
   - Copy the 16-character password

4. Add to .env file:
   GMAIL_EMAIL=your.email@gmail.com
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

5. Run watcher:
   python scripts/gmail_imap_watcher.py --vault ../AI_Employee_Vault

That's it! No OAuth verification needed!
""")
        return
    
    watcher = GmailIMAPWatcher(
        str(vault_path),
        args.interval,
        args.email,
        args.app_password
    )
    
    if args.clean:
        print('Clearing processed IDs...')
        watcher.processed_ids = set()
        watcher._save_processed_ids()
        print('Processed IDs cleared. Next run will re-check all emails.')
        return
    
    if args.demo:
        watcher.demo_mode_create_sample()
        print(f'Demo file created in {vault_path}/Needs_Action/')
        return
    
    print(f'Starting Gmail IMAP Watcher...')
    print(f'Email: {watcher.email_address}')
    print(f'Configured: {bool(watcher.email_address and watcher.app_password)}')
    print(f'Check interval: {args.interval}s')
    print(f'Processed IDs loaded: {len(watcher.processed_ids)}')
    
    if not watcher.email_address or not watcher.app_password:
        print('\nNot configured. Run with --setup for instructions.')
        print('Or add to .env: GMAIL_EMAIL and GMAIL_APP_PASSWORD')
    
    watcher.run()


if __name__ == '__main__':
    main()
