"""
LinkedIn Watcher - Monitors LinkedIn for notifications and engagement
Uses Playwright for browser automation
Creates action files for Qwen Code to process
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


class LinkedInWatcher(BaseWatcher):
    """
    LinkedIn Watcher using Playwright.
    Monitors LinkedIn for notifications, messages, and engagement.
    
    NOTE: First run requires manual login. Session is saved for reuse.
    Be aware of LinkedIn's terms of service regarding automation.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 300,
                 session_path: str = None, email: str = None, password: str = None):
        """
        Initialize LinkedIn Watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 300 = 5 min)
            session_path: Path to store browser session
            email: LinkedIn email (optional, for auto-login)
            password: LinkedIn password (optional, for auto-login)
        """
        super().__init__(vault_path, check_interval)
        
        # Session configuration
        self.session_path = Path(session_path or os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session'))
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Credentials (optional - manual login supported)
        self.email = email or os.getenv('LINKEDIN_EMAIL', '')
        self.password = password or os.getenv('LINKEDIN_PASSWORD', '')
        
        # Keywords for filtering notifications
        keywords_str = os.getenv('LINKEDIN_KEYWORDS', 'message,connection,job,post')
        self.keywords = [k.strip().lower() for k in keywords_str.split(',')]
        
        # Playwright browser context
        self.browser = None
        self.page = None
        
        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Keywords: {self.keywords}')
    
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
                    '--disable-dev-shm-usage',
                    '--disable-setuid-sandbox'
                ]
            )
            
            if not self.browser.pages:
                self.page = self.browser.new_page()
            else:
                self.page = self.browser.pages[0]
            
            # Set anti-detection headers
            self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            self.logger.info('Browser initialized')
            return True
            
        except Exception as e:
            self.logger.error(f'Failed to initialize browser: {e}')
            return False
    
    def _login(self):
        """Log in to LinkedIn."""
        try:
            self.page.goto('https://www.linkedin.com/login', wait_until='networkidle')
            
            # Check if already logged in
            if 'feed' in self.page.url or 'mynetwork' in self.page.url:
                self.logger.info('Already logged in')
                return True
            
            # Auto-login if credentials provided
            if self.email and self.password:
                self.logger.info('Attempting auto-login...')
                
                try:
                    # Fill login form
                    self.page.fill('#username', self.email)
                    self.page.fill('#password', self.password)
                    self.page.click('button[type="submit"]')
                    
                    # Wait for navigation
                    self.page.wait_for_url('**/feed/**', timeout=30000)
                    
                    if 'feed' in self.page.url:
                        self.logger.info('Auto-login successful')
                        return True
                    else:
                        self.logger.warning('Auto-login failed - may require verification')
                        
                except Exception as e:
                    self.logger.warning(f'Auto-login error: {e}')
            
            # Manual login fallback
            self.logger.warning('Manual login required')
            self.logger.info('Please log in within 60 seconds...')
            
            try:
                self.page.wait_for_url('**/feed/**', timeout=60000)
                self.logger.info('Manual login detected!')
                return True
            except:
                self.logger.error('Login timeout')
                return False
                    
        except Exception as e:
            self.logger.error(f'Login error: {e}')
            return False
    
    def check_for_updates(self) -> list:
        """
        Check for new LinkedIn notifications and activity.
        
        Returns:
            List of new notifications/activity
        """
        notifications = []
        
        try:
            # Initialize browser if needed
            if not self.browser:
                if not self._init_browser():
                    return []
            
            # Login if needed
            if not self.page or 'linkedin' not in str(self.page.url):
                if not self._login():
                    return []
            
            # Navigate to notifications
            try:
                self.page.goto('https://www.linkedin.com/notifications/', wait_until='networkidle')
                self.page.wait_for_timeout(3000)  # Wait for content to load
                
                # Find unread notifications
                # Note: Selectors may need adjustment based on LinkedIn updates
                notification_selectors = [
                    '[data-test-id="notification-item"]',
                    '.notification-item',
                    '[aria-label*="notification"]'
                ]
                
                notification_elements = []
                for selector in notification_selectors:
                    try:
                        elements = self.page.query_selector_all(selector)
                        if elements:
                            notification_elements = elements
                            break
                    except:
                        continue
                
                self.logger.info(f'Found {len(notification_elements)} notifications')
                
                for notif in notification_elements[:10]:  # Limit to 10
                    try:
                        # Extract notification text
                        text_elem = notif.query_selector('span[dir="auto"]')
                        text = text_elem.inner_text() if text_elem else 'Unknown'
                        
                        # Check for unread indicator
                        is_unread = 'unread' in str(notif) or 'new' in text.lower()
                        
                        # Check for keywords
                        text_lower = text.lower()
                        matched_keywords = [kw for kw in self.keywords if kw in text_lower]
                        
                        if matched_keywords or is_unread:
                            notifications.append({
                                'text': text,
                                'type': 'notification',
                                'keywords': matched_keywords,
                                'unread': is_unread,
                                'timestamp': datetime.now()
                            })
                            
                    except Exception as e:
                        self.logger.debug(f'Error processing notification: {e}')
                        continue
                
            except Exception as e:
                self.logger.error(f'Error fetching notifications: {e}')
            
            # Also check for new messages
            try:
                messages = self._check_messages()
                notifications.extend(messages)
            except Exception as e:
                self.logger.debug(f'Error checking messages: {e}')
            
        except Exception as e:
            self.logger.error(f'Check updates error: {e}')
            self._cleanup()
        
        return notifications
    
    def _check_messages(self) -> list:
        """Check LinkedIn messages."""
        messages = []
        
        try:
            self.page.goto('https://www.linkedin.com/messaging/', wait_until='networkidle')
            self.page.wait_for_timeout(2000)
            
            # Find conversations with unread messages
            # Note: Selectors may need adjustment
            conversation_selectors = [
                '[data-test-id="conversation"]',
                '.msg-conversation-card'
            ]
            
            for selector in conversation_selectors:
                try:
                    conversations = self.page.query_selector_all(selector)
                    for conv in conversations:
                        # Check for unread indicator
                        unread_elem = conv.query_selector('[aria-label*="unread"]')
                        if unread_elem:
                            name_elem = conv.query_selector('span[dir="auto"]')
                            name = name_elem.inner_text() if name_elem else 'Unknown'
                            
                            messages.append({
                                'text': f'New message from {name}',
                                'type': 'message',
                                'from': name,
                                'keywords': ['message'],
                                'unread': True,
                                'timestamp': datetime.now()
                            })
                    break
                except:
                    continue
                    
        except Exception as e:
            self.logger.debug(f'Message check error: {e}')
        
        return messages
    
    def create_action_file(self, item) -> Path:
        """
        Create action file for a LinkedIn notification/message.
        
        Args:
            item: Notification/message dict
            
        Returns:
            Path to created file
        """
        item_type = item.get('type', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if item_type == 'message':
            chat_id = item.get('from', 'Unknown').replace(' ', '_')[:20]
            filename = f'LINKEDIN_MSG_{chat_id}_{timestamp}.md'
        else:
            filename = f'LINKEDIN_NOTIF_{timestamp}.md'
        
        filepath = self.needs_action / filename
        
        content = f'''---
type: linkedin_{item_type}
from: {item.get('from', 'LinkedIn')}
received: {item['timestamp'].isoformat()}
keywords: {', '.join(item.get('keywords', []))}
priority: normal
status: pending
---

# LinkedIn {item_type.title()}: {item.get('from', 'Notification')}

## Content
{item['text']}

## Detected Keywords
{chr(10).join('- ' + kw for kw in item.get('keywords', []))}

## Suggested Actions
- [ ] Review notification/message
- [ ] Determine required response
- [ ] Draft reply (if needed)
- [ ] Engage with content (like/comment)
- [ ] Mark as done

## Notes
<!-- Add any notes or context here -->

---
*Created by LinkedIn Watcher - AI Employee v0.2*
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
        """Main run loop with browser lifecycle management."""
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
            self.logger.info('Stopping LinkedIn Watcher...')
            self._cleanup()
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            self._cleanup()
            raise
    
    def demo_mode_create_sample(self) -> Path:
        """
        Create a sample LinkedIn action file for testing.
        
        Returns:
            Path to created file
        """
        filename = self.generate_filename('LINKEDIN', 'DEMO_Connection')
        filepath = self.needs_action / filename
        
        content = '''---
type: linkedin_notification
from: John Doe
received: 2026-02-28T10:30:00Z
keywords: connection, message
priority: normal
status: pending
---

# LinkedIn Notification: Connection Request

## Content
John Doe wants to connect with you on LinkedIn

Message: "Hi, I'd love to connect and discuss potential business opportunities."

## Detected Keywords
- connection
- message

## Suggested Actions
- [ ] Review sender profile
- [ ] Accept or decline connection request
- [ ] Draft response message
- [ ] Mark as done

## Notes
This is a DEMO notification for testing the LinkedIn Watcher.
In production, this would be a real LinkedIn notification.

---
*Created by LinkedIn Watcher (Demo Mode) - AI Employee v0.2*
'''
        
        filepath.write_text(content, encoding='utf-8')
        self.logger.info('Created demo LinkedIn action file')
        return filepath


def main():
    """Main entry point for LinkedIn Watcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Watcher for AI Employee')
    parser.add_argument(
        '--vault', 
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--interval', 
        type=int, 
        default=300,
        help='Check interval in seconds'
    )
    parser.add_argument(
        '--session-path',
        default='./linkedin_session',
        help='Path to store browser session'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Create demo LinkedIn notification file and exit'
    )
    
    args = parser.parse_args()
    
    # Resolve vault path relative to script location
    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()
    
    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        sys.exit(1)
    
    watcher = LinkedInWatcher(
        str(vault_path), 
        args.interval,
        args.session_path
    )
    
    if args.demo:
        watcher.demo_mode_create_sample()
        print(f'Demo file created in {vault_path}/Needs_Action/')
        return
    
    print(f'Starting LinkedIn Watcher...')
    print(f'Vault: {vault_path}')
    print(f'Interval: {args.interval}s')
    print(f'Session: {watcher.session_path}')
    print('\nNote: First run requires manual login')
    print('Session will be saved for subsequent runs')
    
    watcher.run()


if __name__ == '__main__':
    main()
