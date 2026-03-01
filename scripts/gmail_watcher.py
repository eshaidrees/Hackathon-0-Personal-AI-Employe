"""
Gmail Watcher - Monitors Gmail for new important/unread messages
Creates action files in Needs_Action folder for Qwen Code to process
Uses Gmail API with OAuth2 authentication
"""
import os
import sys
import pickle
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

# Load environment variables
load_dotenv()


class GmailWatcher(BaseWatcher):
    """
    Gmail Watcher implementation using Gmail API.
    Monitors Gmail for unread/important messages and creates action files.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 120, 
                 credentials_path: str = None, token_path: str = None):
        """
        Initialize Gmail Watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 120)
            credentials_path: Path to OAuth credentials JSON
            token_path: Path to OAuth token pickle file
        """
        super().__init__(vault_path, check_interval)
        
        # Gmail API configuration
        self.credentials_path = Path(credentials_path or os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json'))
        self.token_path = Path(token_path or os.getenv('GMAIL_TOKEN_PATH', 'token.json'))
        self.service = None
        self.authenticated = False
        
        # Initialize Gmail API
        self._init_gmail_api()
    
    def _init_gmail_api(self):
        """Initialize Gmail API service."""
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            
            # Gmail API scopes
            SCOPES = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.modify'
            ]
            
            creds = None
            
            # Load existing token
            if self.token_path.exists():
                try:
                    with open(self.token_path, 'rb') as f:
                        creds = pickle.load(f)
                    self.logger.info(f'Loaded token from {self.token_path}')
                except Exception as e:
                    self.logger.warning(f'Could not load token: {e}')
                    creds = None
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        self._save_token(creds)
                        self.logger.info('Token refreshed')
                    except Exception as e:
                        self.logger.error(f'Token refresh failed: {e}')
                        creds = None
            
            if creds and creds.valid:
                # Build Gmail service
                self.service = build('gmail', 'v1', credentials=creds)
                self.authenticated = True
                
                # Get profile for logging
                try:
                    profile = self.service.users().getProfile(userId='me').execute()
                    self.logger.info(f'Authenticated as: {profile["emailAddress"]}')
                except:
                    pass
            else:
                self.logger.warning('Gmail API not authenticated. Run gmail_auth.py first.')
                self.logger.warning(f'Credentials path: {self.credentials_path}')
                self.logger.warning(f'Token path: {self.token_path}')
                
        except ImportError:
            self.logger.error('Gmail API libraries not installed')
            self.logger.error('Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib')
        except Exception as e:
            self.logger.error(f'Gmail API initialization error: {e}')
    
    def _save_token(self, creds):
        """Save token to file."""
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.token_path, 'wb') as f:
            pickle.dump(creds, f)
    
    def check_for_updates(self) -> list:
        """
        Check for new Gmail messages.
        
        Returns:
            List of new messages
        """
        if not self.authenticated or not self.service:
            self.logger.debug('Gmail API not available, skipping check')
            return []
        
        try:
            # Query for unread important messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=20
            ).execute()
            
            messages = results.get('messages', [])
            
            # Filter out already processed
            new_messages = [
                m for m in messages 
                if m['id'] not in self.processed_ids
            ]
            
            if new_messages:
                self.logger.info(f'Found {len(new_messages)} new messages')
            
            return new_messages
            
        except Exception as e:
            self.logger.error(f'Gmail API error: {e}')
            # Try to re-authenticate
            self._init_gmail_api()
            return []
    
    def create_action_file(self, message) -> Path:
        """
        Create action file for a Gmail message.
        
        Args:
            message: Gmail message dict from API
            
        Returns:
            Path to created file
        """
        try:
            # Get full message details
            msg = self.service.users().messages().get(
                userId='me', 
                id=message['id'],
                format='metadata',
                metadataHeaders=['From', 'To', 'Subject', 'Date']
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            
            # Generate filename
            filename = self.generate_filename('EMAIL', message['id'])
            filepath = self.needs_action / filename
            
            # Get sender name
            from_email = headers.get('From', 'Unknown')
            from_name = from_email.split('<')[0].strip() if '<' in from_email else from_email
            
            # Create markdown content
            content = f'''---
type: email
from: {from_email}
from_name: {from_name}
to: {headers.get('To', 'me')}
subject: {headers.get('Subject', 'No Subject')}
received: {datetime.now().isoformat()}
message_id: {message['id']}
priority: normal
status: pending
---

# Email: {headers.get('Subject', 'No Subject')}

## Header Information
- **From:** {from_email}
- **To:** {headers.get('To', 'me')}
- **Received:** {headers.get('Date', datetime.now().isoformat())}

## Email Content
{msg.get('snippet', 'Content not available')}

## Suggested Actions
- [ ] Read and categorize
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing

## Notes
<!-- Add any notes or context here -->

---
*Created by Gmail Watcher - AI Employee v0.2*
'''
            
            filepath.write_text(content, encoding='utf-8')
            self.processed_ids.add(message['id'])
            
            self.logger.info(f'Created action file: {filepath.name}')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            raise
    
    def mark_as_read(self, message_id: str):
        """Mark a message as read."""
        if not self.service:
            return
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            self.logger.debug(f'Marked message {message_id} as read')
        except Exception as e:
            self.logger.error(f'Error marking as read: {e}')
    
    def get_unread_count(self) -> int:
        """Get count of unread messages."""
        if not self.service:
            return 0
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=1
            ).execute()
            return len(results.get('messages', []))
        except:
            return 0
    
    def demo_mode_create_sample(self) -> Path:
        """
        Create a sample email action file for testing.
        
        Returns:
            Path to created file
        """
        filename = self.generate_filename('EMAIL', 'DEMO001')
        filepath = self.needs_action / filename
        
        content = '''---
type: email
from: demo@example.com
from_name: Demo User
to: me
subject: [DEMO] Test Email for AI Employee
received: 2026-02-28T10:00:00Z
message_id: DEMO001
priority: normal
status: pending
---

# Email: [DEMO] Test Email for AI Employee

## Header Information
- **From:** demo@example.com
- **To:** me
- **Received:** 2026-02-28 10:00 AM

## Email Content
This is a demo email created for testing the AI Employee system.
The Gmail Watcher created this file to demonstrate functionality.

In production, this would be a real email from your Gmail account.

## Suggested Actions
- [ ] Acknowledge this is a demo
- [ ] Move to Done folder to complete

## Notes
This demo file helps test the watcher -> Qwen Code -> action workflow.

---
*Created by Gmail Watcher (Demo Mode) - AI Employee v0.2*
'''
        
        filepath.write_text(content, encoding='utf-8')
        self.logger.info('Created demo email action file')
        return filepath


def main():
    """
    Main entry point for Gmail Watcher.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument(
        '--vault', 
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--interval', 
        type=int, 
        default=120,
        help='Check interval in seconds'
    )
    parser.add_argument(
        '--credentials',
        default='credentials.json',
        help='Path to Gmail OAuth credentials'
    )
    parser.add_argument(
        '--token',
        default='token.json',
        help='Path to Gmail OAuth token'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Create demo email file and exit'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test Gmail API connection'
    )
    
    args = parser.parse_args()
    
    # Resolve vault path relative to script location
    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()
    
    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        sys.exit(1)
    
    if args.test:
        # Test mode
        watcher = GmailWatcher(
            str(vault_path), 
            args.interval,
            args.credentials,
            args.token
        )
        if watcher.authenticated:
            unread = watcher.get_unread_count()
            print(f'✓ Gmail API connected')
            print(f'Unread messages: {unread}')
        else:
            print('✗ Gmail API not authenticated')
            print('Run: python scripts/gmail_auth.py')
        return
    
    watcher = GmailWatcher(
        str(vault_path), 
        args.interval,
        args.credentials,
        args.token
    )
    
    if args.demo:
        watcher.demo_mode_create_sample()
        print(f'Demo file created in {vault_path}/Needs_Action/')
        return
    
    print(f'Starting Gmail Watcher...')
    print(f'Vault: {vault_path}')
    print(f'Interval: {args.interval}s')
    print(f'Authenticated: {watcher.authenticated}')
    
    if not watcher.authenticated:
        print('\nNot authenticated. Run: python scripts/gmail_auth.py')
        print('Continuing in demo mode (will not fetch real emails)')
    
    watcher.run()


if __name__ == '__main__':
    main()
