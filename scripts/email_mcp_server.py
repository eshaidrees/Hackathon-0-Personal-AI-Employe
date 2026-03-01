"""
Email MCP Server - Gmail API integration for sending/managing emails
Supports OAuth2 authentication, attachments, and approval workflow
"""
import os
import sys
import json
import base64
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class EmailMCP:
    """
    Email MCP for Gmail operations.
    Handles sending, drafting, and managing emails via Gmail API.
    """
    
    def __init__(self, credentials_path: str = None, token_path: str = None):
        """
        Initialize Email MCP.
        
        Args:
            credentials_path: Path to OAuth credentials JSON
            token_path: Path to OAuth token JSON
        """
        self.credentials_path = credentials_path or os.getenv('GMAIL_CREDENTIALS', 'credentials.json')
        self.token_path = token_path or os.getenv('GMAIL_TOKEN', 'token.json')
        self.service = None
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        
        import logging
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            from google.auth.exceptions import RefreshError
            
            # Scopes for Gmail API
            SCOPES = ['https://www.googleapis.com/auth/gmail.send',
                      'https://www.googleapis.com/auth/gmail.readonly',
                      'https://www.googleapis.com/auth/gmail.modify']
            
            creds = None
            
            # Load existing token
            if os.path.exists(self.token_path):
                try:
                    creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
                except Exception as e:
                    self.logger.warning(f'Error loading token: {e}')
                    creds = None
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except RefreshError:
                        self.logger.error('Token refresh failed, re-authentication required')
                        creds = None
                
                if not creds:
                    self.logger.error('No valid credentials. Run email_auth.py first.')
                    return False
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info('Gmail API authenticated')
            return True
            
        except ImportError:
            self.logger.error('Gmail API libraries not installed')
            self.logger.error('Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib')
            return False
        except Exception as e:
            self.logger.error(f'Authentication error: {e}')
            return False
    
    def send_email(self, to: str, subject: str, body: str, 
                   cc: str = None, bcc: str = None,
                   attachments: list = None) -> dict:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            cc: CC recipients (comma-separated)
            bcc: BCC recipients (comma-separated)
            attachments: List of file paths to attach
            
        Returns:
            dict with message_id and status
        """
        if self.dry_run:
            self.logger.info(f'[DRY RUN] Would send email to {to}')
            self.logger.info(f'[DRY RUN] Subject: {subject}')
            return {'status': 'dry_run', 'message_id': None}
        
        # Authenticate if needed
        if not self.service:
            if not self._authenticate():
                return {'status': 'error', 'error': 'Authentication failed'}
        
        try:
            # Create message
            message = self._create_message(to, subject, body, cc, bcc, attachments)
            
            # Send via Gmail API
            sent_message = self.service.users().messages().send(
                userId='me', 
                body=message
            ).execute()
            
            self.logger.info(f'Email sent to {to}, message ID: {sent_message["id"]}')
            return {'status': 'sent', 'message_id': sent_message['id']}
            
        except Exception as e:
            self.logger.error(f'Send error: {e}')
            return {'status': 'error', 'error': str(e)}
    
    def _create_message(self, to: str, subject: str, body: str,
                        cc: str = None, bcc: str = None,
                        attachments: list = None) -> dict:
        """Create MIME message and encode for Gmail API."""
        try:
            if cc or bcc:
                # Multipart for CC/BCC
                message = MIMEMultipart()
                message['To'] = to
                if cc:
                    message['Cc'] = cc
                if bcc:
                    message['Bcc'] = bcc
            else:
                # Simple message
                message = MIMEText(body, 'html' if '<' in body else 'plain')
                message['To'] = to
            
            message['From'] = 'me'
            message['Subject'] = subject
            
            # Add attachments
            if attachments:
                if not isinstance(attachments, list):
                    attachments = [attachments]
                
                main_message = MIMEMultipart()
                main_message.attach(MIMEText(body, 'html' if '<' in body else 'plain'))
                
                for file_path in attachments:
                    main_message.attach(self._create_attachment(file_path))
                
                message = main_message
            
            # Encode to base64
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            return {'raw': raw}
            
        except Exception as e:
            self.logger.error(f'Message creation error: {e}')
            raise
    
    def _create_attachment(self, file_path: str) -> MIMEBase:
        """Create MIME attachment from file."""
        filename = os.path.basename(file_path)
        
        with open(file_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{filename}"'
        )
        
        return part
    
    def create_draft(self, to: str, subject: str, body: str,
                     cc: str = None, attachments: list = None) -> dict:
        """
        Create a draft email without sending.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            cc: CC recipients
            attachments: List of file paths
            
        Returns:
            dict with draft_id
        """
        if self.dry_run:
            self.logger.info(f'[DRY RUN] Would create draft to {to}')
            return {'status': 'dry_run', 'draft_id': None}
        
        if not self.service:
            if not self._authenticate():
                return {'status': 'error', 'error': 'Authentication failed'}
        
        try:
            message = self._create_message(to, subject, body, cc, None, attachments)
            
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': message}
            ).execute()
            
            self.logger.info(f'Draft created: {draft["id"]}')
            return {'status': 'draft_created', 'draft_id': draft['id']}
            
        except Exception as e:
            self.logger.error(f'Draft error: {e}')
            return {'status': 'error', 'error': str(e)}
    
    def list_emails(self, query: str = None, max_results: int = 10) -> list:
        """
        List emails matching query.
        
        Args:
            query: Gmail search query
            max_results: Max results to return
            
        Returns:
            List of email summaries
        """
        if not self.service:
            if not self._authenticate():
                return []
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query or '',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                detail = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'To', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in detail['payload']['headers']}
                emails.append({
                    'id': msg['id'],
                    'from': headers.get('From', ''),
                    'to': headers.get('To', ''),
                    'subject': headers.get('Subject', ''),
                    'date': headers.get('Date', '')
                })
            
            return emails
            
        except Exception as e:
            self.logger.error(f'List error: {e}')
            return []
    
    def get_email(self, message_id: str) -> dict:
        """
        Get full email content.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Email details with body
        """
        if not self.service:
            if not self._authenticate():
                return {}
        
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract body
            body = ''
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'body' in part:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode()
                        break
            elif 'body' in message['payload']:
                body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in message['payload']['headers']}
            
            return {
                'id': message['id'],
                'from': headers.get('From', ''),
                'to': headers.get('To', ''),
                'subject': headers.get('Subject', ''),
                'date': headers.get('Date', ''),
                'body': body,
                'snippet': message.get('snippet', '')
            }
            
        except Exception as e:
            self.logger.error(f'Get email error: {e}')
            return {}
    
    def label_email(self, message_id: str, action: str) -> dict:
        """
        Modify email labels.
        
        Args:
            message_id: Gmail message ID
            action: read/unread/archive/star/trash
            
        Returns:
            Status dict
        """
        if not self.service:
            if not self._authenticate():
                return {'status': 'error', 'error': 'Not authenticated'}
        
        label_actions = {
            'read': {'remove': 'UNREAD'},
            'unread': {'add': 'UNREAD'},
            'archive': {'remove': 'INBOX'},
            'star': {'add': 'STARRED'},
            'unstar': {'remove': 'STARRED'},
            'trash': {'add': 'TRASH'}
        }
        
        if action not in label_actions:
            return {'status': 'error', 'error': f'Unknown action: {action}'}
        
        try:
            modify = label_actions[action]
            
            if 'add' in modify:
                result = self.service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'addLabelIds': [modify['add']]}
                ).execute()
            else:
                result = self.service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'removeLabelIds': [modify['remove']]}
                ).execute()
            
            self.logger.info(f'Email {action}: {message_id}')
            return {'status': 'success', 'action': action}
            
        except Exception as e:
            self.logger.error(f'Label error: {e}')
            return {'status': 'error', 'error': str(e)}
    
    def create_approval_request(self, to: str, subject: str, body: str,
                                vault_path: str, attachments: list = None) -> Path:
        """
        Create approval request file for sensitive emails.
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            vault_path: Path to Obsidian vault
            attachments: List of attachments
            
        Returns:
            Path to approval file
        """
        vault = Path(vault_path)
        pending = vault / 'Pending_Approval'
        pending.mkdir(parents=True, exist_ok=True)
        
        filename = f"EMAIL_APPROVAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = pending / filename
        
        attachment_list = '\n'.join(f'- {a}' for a in (attachments or [])) or '- None'
        
        content = f'''---
type: approval_request
action: email_send
to: {to}
subject: {subject}
created: {datetime.now().isoformat()}
expires: {(datetime.now().replace(hour=23, minute=59)).isoformat()}
status: pending
---

# Email Approval Request

## Details
- **To:** {to}
- **Subject:** {subject}
- **Attachments:** 
{attachment_list}

## Content
{body}

## To Approve
Move this file to /Approved/ folder.

## To Reject
Move this file to /Rejected/ folder.

---
*Created by Email MCP - AI Employee v0.1*
'''
        
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f'Approval request created: {filepath.name}')
        return filepath


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Email MCP Server')
    parser.add_argument('action', choices=['send', 'draft', 'list', 'get', 'label', 'demo'])
    parser.add_argument('--to', default='', help='Recipient email')
    parser.add_argument('--subject', default='', help='Email subject')
    parser.add_argument('--body', default='', help='Email body')
    parser.add_argument('--id', default='', help='Message ID')
    parser.add_argument('--query', default='', help='Search query')
    parser.add_argument('--vault', default='../AI_Employee_Vault', help='Vault path')
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    
    args = parser.parse_args()
    
    mcp = EmailMCP()
    
    if args.demo or args.action == 'demo':
        print('Email MCP Demo Mode')
        print(f'Dry Run: {mcp.dry_run}')
        print('\nTest sending email:')
        result = mcp.send_email(
            to='test@example.com',
            subject='Test Email',
            body='This is a test email from AI Employee'
        )
        print(f'Result: {result}')
    
    elif args.action == 'send':
        if not args.to or not args.subject:
            print('Error: --to and --subject required')
            sys.exit(1)
        result = mcp.send_email(args.to, args.subject, args.body)
        print(f'Result: {result}')
    
    elif args.action == 'draft':
        if not args.to or not args.subject:
            print('Error: --to and --subject required')
            sys.exit(1)
        result = mcp.create_draft(args.to, args.subject, args.body)
        print(f'Result: {result}')
    
    elif args.action == 'list':
        emails = mcp.list_emails(args.query or '', 10)
        for e in emails:
            print(f"{e['id'][:8]} | {e['from'][:30]} | {e['subject'][:50]}")
    
    elif args.action == 'get':
        if not args.id:
            print('Error: --id required')
            sys.exit(1)
        email = mcp.get_email(args.id)
        print(json.dumps(email, indent=2))
    
    elif args.action == 'label':
        print('Use: python email_mcp_server.py label --id MSG_ID --action read/unread/archive')


if __name__ == '__main__':
    main()
