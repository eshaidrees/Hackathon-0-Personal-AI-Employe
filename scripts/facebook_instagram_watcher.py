"""
Facebook/Instagram Watcher - Monitors social media notifications
Uses Playwright for browser automation
Creates action files for Claude to process
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


class FacebookInstagramWatcher(BaseWatcher):
    """
    Facebook/Instagram Watcher using Playwright.
    Monitors notifications, messages, and engagement.

    NOTE: Be aware of Meta's terms of service regarding automation.
    First run requires manual login for session capture.
    """

    def __init__(self, vault_path: str, check_interval: int = 300, 
                 session_path: str = None, platform: str = 'facebook'):
        """
        Initialize Facebook/Instagram Watcher.

        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 300 = 5 min)
            session_path: Path to store browser session
            platform: 'facebook' or 'instagram'
        """
        super().__init__(vault_path, check_interval)

        self.platform = platform
        self.session_path = Path(session_path) if session_path else Path(f'./{platform}_session')
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.email = os.getenv(f'{platform.upper()}_EMAIL', '')
        self.password = os.getenv(f'{platform.upper()}_PASSWORD', '')
        
        # Keywords for filtering important notifications
        keywords_str = os.getenv('SOCIAL_KEYWORDS', 'message,comment,share,mention,urgent')
        self.keywords = [k.strip().lower() for k in keywords_str.split(',')]

        # Browser state
        self.browser = None
        self.page = None

        self.logger.info(f'Platform: {platform}')
        self.logger.info(f'Priority keywords: {self.keywords}')
        self.logger.info(f'Session path: {self.session_path}')

    def _get_base_url(self):
        """Get base URL for platform."""
        return 'https://www.facebook.com' if self.platform == 'facebook' else 'https://www.instagram.com'

    def _get_notifications_url(self):
        """Get notifications page URL."""
        if self.platform == 'facebook':
            return 'https://www.facebook.com/notifications'
        else:
            return 'https://www.instagram.com/accounts/activity/'

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

            self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            self.logger.info('Browser initialized successfully')
            return True

        except Exception as e:
            self.logger.error(f'Failed to initialize browser: {e}')
            return False

    def _login(self):
        """Log in to platform."""
        try:
            base_url = self._get_base_url()
            self.page.goto(base_url, wait_until='networkidle')

            # Check if already logged in
            if self.platform == 'facebook':
                # Check for feed or profile
                if 'feed' in self.page.url or 'profile' in self.page.url:
                    self.logger.info('Already logged in to Facebook')
                    return True
            else:
                # Instagram
                if 'feed' in self.page.url or 'explore' in self.page.url:
                    self.logger.info('Already logged in to Instagram')
                    return True

            # Manual login required
            self.logger.warning('Manual login required')
            self.logger.info(f'Please log in to {self.platform} within 90 seconds...')
            
            try:
                # Wait for navigation to logged-in page
                if self.platform == 'facebook':
                    self.page.wait_for_url('**/feed**', timeout=90000)
                else:
                    self.page.wait_for_url('**/feed/**', timeout=90000)
                
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
        Check for new notifications/messages.

        Returns:
            List of new notifications (dict with type, content, timestamp)
        """
        notifications = []

        try:
            # Initialize browser if needed
            if not self.browser:
                if not self._init_browser():
                    return []

            # Login if needed
            if not self.page:
                if not self._login():
                    return []

            # Navigate to notifications
            try:
                self.page.goto(self._get_notifications_url(), wait_until='networkidle')
                self.page.wait_for_timeout(5000)  # Wait for content to load

                if self.platform == 'facebook':
                    notifications = self._parse_facebook_notifications()
                else:
                    notifications = self._parse_instagram_notifications()

            except Exception as e:
                self.logger.error(f'Error parsing notifications: {e}')

        except Exception as e:
            self.logger.error(f'Check updates error: {e}')
            self._cleanup()

        return notifications

    def _parse_facebook_notifications(self) -> list:
        """Parse Facebook notifications."""
        notifications = []

        try:
            # Facebook notification selectors (may need updates)
            notification_selectors = [
                '[data-visualcompletion="css-img"]',
                '.rq0escxv.a9duxzls.g4tp4svg',
                '[role="article"]',
            ]

            for selector in notification_selectors:
                try:
                    elements = self.page.query_selector_all(selector)
                    self.logger.info(f'Found {len(elements)} elements with selector')

                    for elem in elements[:10]:  # Limit to 10 recent
                        try:
                            text = elem.inner_text()
                            
                            # Check for keywords
                            matched_keywords = [kw for kw in self.keywords if kw.lower() in text.lower()]
                            
                            if matched_keywords:
                                notifications.append({
                                    'platform': 'facebook',
                                    'type': 'notification',
                                    'text': text[:500],
                                    'keywords': matched_keywords,
                                    'timestamp': datetime.now()
                                })
                                self.logger.info(f"Facebook notification: {matched_keywords}")
                        except:
                            continue

                    if elements:
                        break
                except:
                    continue

        except Exception as e:
            self.logger.error(f'Facebook parse error: {e}')

        return notifications

    def _parse_instagram_notifications(self) -> list:
        """Parse Instagram notifications."""
        notifications = []

        try:
            # Instagram notification selectors
            notification_selectors = [
                'article',
                '[role="listitem"]',
                '.x1n2onr6.x1n2onr6',
            ]

            for selector in notification_selectors:
                try:
                    elements = self.page.query_selector_all(selector)
                    
                    for elem in elements[:10]:
                        try:
                            text = elem.inner_text()
                            
                            matched_keywords = [kw for kw in self.keywords if kw.lower() in text.lower()]
                            
                            if matched_keywords:
                                notifications.append({
                                    'platform': 'instagram',
                                    'type': 'notification',
                                    'text': text[:500],
                                    'keywords': matched_keywords,
                                    'timestamp': datetime.now()
                                })
                        except:
                            continue

                    if elements:
                        break
                except:
                    continue

        except Exception as e:
            self.logger.error(f'Instagram parse error: {e}')

        return notifications

    def create_action_file(self, item) -> Path:
        """
        Create action file for a notification.

        Args:
            item: Notification dict

        Returns:
            Path to created file
        """
        platform = item['platform']
        filename = self.generate_filename(f'{platform.upper()}_NOTIF', 'recent')
        filepath = self.needs_action / filename

        content = f'''---
type: {platform}_notification
platform: {platform}
received: {item['timestamp'].isoformat()}
keywords: {', '.join(item['keywords'])}
priority: medium
status: pending
---

# {platform.title()} Notification

## Content
{item['text']}

## Detected Keywords
{chr(10).join('- ' + kw for kw in item['keywords'])}

## Suggested Actions
- [ ] Review notification
- [ ] Determine if response needed
- [ ] Draft response (if needed)
- [ ] Execute response (requires approval)
- [ ] Mark as done

## Notes
<!-- Add context or notes here -->

---
*Created by {platform.title()} Watcher - AI Employee v0.1*
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
        """Main run loop."""
        self.logger.info(f'Starting {self.platform.title()} Watcher')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')

        try:
            while True:
                try:
                    items = self.check_for_updates()
                    for item in items:
                        try:
                            filepath = self.create_action_file(item)
                        except Exception as e:
                            self.logger.error(f'Error creating action file: {e}')
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                    self._cleanup()

                import time
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info(f'Stopping {self.platform.title()} Watcher...')
            self._cleanup()
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            self._cleanup()
            raise

    def demo_mode_create_sample(self) -> Path:
        """Create a sample notification file for testing."""
        filename = self.generate_filename(f'{self.platform.upper()}_DEMO', 'test')
        filepath = self.needs_action / filename

        content = f'''---
type: {self.platform}_notification
platform: {self.platform}
received: {datetime.now().isoformat()}
keywords: message, urgent
priority: medium
status: pending
---

# {self.platform.title()} Notification (DEMO)

## Content
This is a DEMO notification for testing the {self.platform.title()} Watcher.
Someone mentioned your business in a post with the message:
"Hey, I need help with your services urgently!"

## Detected Keywords
- message
- urgent

## Suggested Actions
- [ ] Review notification
- [ ] Draft response
- [ ] Get approval
- [ ] Send response

## Notes
This is a DEMO message for testing.
In production, this would be a real {self.platform} notification.

---
*Created by {self.platform.title()} Watcher (Demo Mode) - AI Employee v0.1*
'''

        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f'Created demo {self.platform} action file')
        return filepath


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Facebook/Instagram Watcher')
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
        help='Path to store browser session'
    )
    parser.add_argument(
        '--platform',
        choices=['facebook', 'instagram'],
        default='facebook',
        help='Platform to monitor'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Create demo notification file and exit'
    )

    args = parser.parse_args()

    # Resolve vault path
    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()

    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        sys.exit(1)

    watcher = FacebookInstagramWatcher(
        str(vault_path),
        args.interval,
        args.session_path,
        args.platform
    )

    if args.demo:
        watcher.demo_mode_create_sample()
        print(f'Demo file created in {vault_path}/Needs_Action/')
        return

    watcher.run()


if __name__ == '__main__':
    main()
