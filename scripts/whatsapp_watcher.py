"""
WhatsApp Watcher - Monitors WhatsApp Web for important messages
Creates action files in Needs_Action folder for Claude to process
Uses Playwright for browser automation
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

# Load environment variables
load_dotenv()


class WhatsAppWatcher(BaseWatcher):
    """
    WhatsApp Watcher implementation using Playwright.
    Monitors WhatsApp Web for unread messages containing priority keywords.
    
    NOTE: First run requires manual QR code scan for authentication.
    Be aware of WhatsApp's terms of service regarding automation.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 30, session_path: str = None):
        """
        Initialize WhatsApp Watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 30)
            session_path: Path to store browser session (default: ./whatsapp_session)
        """
        super().__init__(vault_path, check_interval)
        
        # Session configuration
        self.session_path = Path(session_path) if session_path else Path('./whatsapp_session')
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Priority keywords for filtering
        keywords_str = os.getenv('WHATSAPP_KEYWORDS', 'urgent,asap,invoice,payment,help')
        self.keywords = [k.strip().lower() for k in keywords_str.split(',')]
        
        # Playwright browser context
        self.browser = None
        self.page = None
        
        self.logger.info(f'Priority keywords: {self.keywords}')
        self.logger.info(f'Session path: {self.session_path}')
    
    def _init_browser(self):
        """Initialize Playwright browser with persistent context."""
        try:
            from playwright.sync_api import sync_playwright
            
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch_persistent_context(
                str(self.session_path),
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )
            
            if not self.browser.pages:
                self.page = self.browser.new_page()
            else:
                self.page = self.browser.pages[0]
            
            # Set anti-detection headers
            self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            self.logger.info('Browser initialized successfully')
            return True
            
        except Exception as e:
            self.logger.error(f'Failed to initialize browser: {e}')
            return False
    
    def _navigate_to_whatsapp(self):
        """Navigate to WhatsApp Web and wait for load."""
        try:
            self.page.goto('https://web.whatsapp.com', wait_until='networkidle')
            
            # Wait for chat list or QR code
            try:
                self.page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)
                self.logger.info('WhatsApp Web loaded (authenticated)')
                return True
            except:
                self.logger.warning('QR code scan required - waiting 60 seconds...')
                self.logger.info('Open WhatsApp on phone > Linked Devices > Link a Device')
                try:
                    self.page.wait_for_selector('[data-testid="chat-list"]', timeout=60000)
                    self.logger.info('QR code scanned successfully!')
                    return True
                except:
                    self.logger.error('QR code scan timeout')
                    return False
                    
        except Exception as e:
            self.logger.error(f'Navigation error: {e}')
            return False
    
    def check_for_updates(self) -> list:
        """
        Check for new WhatsApp messages with priority keywords.
        
        Returns:
            List of new messages (dict with text, chat, timestamp)
        """
        messages = []
        
        try:
            # Initialize browser if needed
            if not self.browser:
                if not self._init_browser():
                    return []
            
            # Navigate to WhatsApp if needed
            if not self.page:
                if not self._navigate_to_whatsapp():
                    return []
            
            # Find unread chats
            try:
                # Selector for unread messages (may need adjustment based on WhatsApp Web updates)
                unread_selector = '[aria-label*="unread"], [data-testid="chat-list"] [role="listitem"]'
                unread_chats = self.page.query_selector_all(unread_selector)
                
                self.logger.info(f'Found {len(unread_chats)} potential unread chats')
                
                for chat in unread_chats:
                    try:
                        # Extract chat name/number
                        chat_name_elem = chat.query_selector('[data-testid="chat-list"] > div > div:first-child')
                        chat_name = chat_name_elem.inner_text() if chat_name_elem else 'Unknown'
                        
                        # Extract message text
                        message_elem = chat.query_selector('[data-testid="message"]')
                        if not message_elem:
                            message_elem = chat.query_selector('span[dir="auto"]')
                        
                        if message_elem:
                            text = message_elem.inner_text().lower()
                            
                            # Check for priority keywords
                            matched_keywords = [kw for kw in self.keywords if kw in text]
                            
                            if matched_keywords:
                                messages.append({
                                    'text': text,
                                    'chat': chat_name,
                                    'keywords': matched_keywords,
                                    'timestamp': datetime.now()
                                })
                                self.logger.info(f"Priority message from {chat_name}: {matched_keywords}")
                        
                    except Exception as e:
                        self.logger.debug(f'Error processing chat: {e}')
                        continue
                
            except Exception as e:
                self.logger.error(f'Error finding unread messages: {e}')
            
        except Exception as e:
            self.logger.error(f'Check updates error: {e}')
            # Try to recover by reinitializing
            self._cleanup()
        
        return messages
    
    def create_action_file(self, item) -> Path:
        """
        Create action file for a WhatsApp message.
        
        Args:
            item: Message dict with text, chat, keywords, timestamp
            
        Returns:
            Path to created file
        """
        # Generate unique ID from chat name
        chat_id = item['chat'].replace(' ', '_').replace('+', '')[:20]
        filename = self.generate_filename('WHATSAPP', chat_id)
        filepath = self.needs_action / filename
        
        # Create markdown content
        content = f'''---
type: whatsapp
from: {item['chat']}
chat: {item['chat']}
received: {item['timestamp'].isoformat()}
keywords: {', '.join(item['keywords'])}
priority: high
status: pending
---

# WhatsApp Message: {item['chat']}

## Message Content
{item['text']}

## Detected Keywords
{chr(10).join('- ' + kw for kw in item['keywords'])}

## Suggested Actions
- [ ] Read message
- [ ] Determine required response
- [ ] Draft reply (if needed)
- [ ] Execute response (requires approval for external actions)
- [ ] Mark as done

## Notes
<!-- Add any notes or context here -->

---
*Created by WhatsApp Watcher - AI Employee v0.1*
'''
        
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f'Created action file: {filepath.name}')
        return filepath
    
    def _cleanup(self):
        """Clean up browser resources."""
        try:
            if self.browser:
                self.browser.close()
                self.browser = None
                self.page = None
                self.logger.info('Browser cleanup complete')
        except Exception as e:
            self.logger.error(f'Cleanup error: {e}')
    
    def run(self):
        """
        Main run loop with browser lifecycle management.
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info(f'Session path: {self.session_path}')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    for item in items:
                        try:
                            filepath = self.create_action_file(item)
                            self.logger.info(f'Created action file: {filepath.name}')
                        except Exception as e:
                            self.logger.error(f'Error creating action file: {e}')
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                    self._cleanup()
                
                import time
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info('Stopping WhatsApp Watcher...')
            self._cleanup()
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            self._cleanup()
            raise
    
    def demo_mode_create_sample(self) -> Path:
        """
        Create a sample WhatsApp action file for testing.
        
        Returns:
            Path to created file
        """
        filename = self.generate_filename('WHATSAPP', 'DEMO_Client')
        filepath = self.needs_action / filename
        
        content = '''---
type: whatsapp
from: +1234567890 (John Doe)
chat: John Doe
received: 2026-02-28T10:30:00Z
keywords: urgent, invoice
priority: high
status: pending
---

# WhatsApp Message: John Doe

## Message Content
Hey, can you send me the invoice for January? This is urgent.

## Detected Keywords
- urgent
- invoice

## Suggested Actions
- [ ] Read message
- [ ] Generate January invoice for John Doe
- [ ] Send via email (requires approval)
- [ ] Mark as done

## Notes
This is a DEMO message for testing the WhatsApp Watcher.
In production, this would be a real WhatsApp message.

---
*Created by WhatsApp Watcher (Demo Mode) - AI Employee v0.1*
'''
        
        filepath.write_text(content, encoding='utf-8')
        self.logger.info('Created demo WhatsApp action file')
        return filepath


def main():
    """
    Main entry point for WhatsApp Watcher.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='WhatsApp Watcher for AI Employee')
    parser.add_argument(
        '--vault', 
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--interval', 
        type=int, 
        default=30,
        help='Check interval in seconds'
    )
    parser.add_argument(
        '--session-path',
        default='./whatsapp_session',
        help='Path to store browser session'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Create demo WhatsApp message file and exit'
    )
    
    args = parser.parse_args()
    
    # Resolve vault path relative to script location
    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()
    
    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        sys.exit(1)
    
    watcher = WhatsAppWatcher(
        str(vault_path), 
        args.interval,
        args.session_path
    )
    
    if args.demo:
        watcher.demo_mode_create_sample()
        print(f'Demo file created in {vault_path}/Needs_Action/')
        return
    
    watcher.run()


if __name__ == '__main__':
    main()
