"""
Twitter (X) Watcher - Monitors Twitter notifications and mentions
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


class TwitterWatcher(BaseWatcher):
    """
    Twitter (X) Watcher using Playwright.
    Monitors notifications, mentions, DMs, and engagement.

    NOTE: Be aware of Twitter's terms of service regarding automation.
    First run requires manual login for session capture.
    """

    def __init__(self, vault_path: str, check_interval: int = 300, 
                 session_path: str = None):
        """
        Initialize Twitter Watcher.

        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 300 = 5 min)
            session_path: Path to store browser session
        """
        super().__init__(vault_path, check_interval)

        self.session_path = Path(session_path) if session_path else Path('./twitter_session')
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.email = os.getenv('TWITTER_EMAIL', '')
        self.username = os.getenv('TWITTER_USERNAME', '')
        self.password = os.getenv('TWITTER_PASSWORD', '')
        
        # Keywords for filtering important notifications
        keywords_str = os.getenv('TWITTER_KEYWORDS', 'mention,message,DM,urgent,question')
        self.keywords = [k.strip().lower() for k in keywords_str.split(',')]

        # Browser state
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

            self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            self.logger.info('Browser initialized successfully')
            return True

        except Exception as e:
            self.logger.error(f'Failed to initialize browser: {e}')
            return False

    def _login(self):
        """Log in to Twitter."""
        try:
            self.page.goto('https://twitter.com/login', wait_until='networkidle')

            # Check if already logged in
            if 'home' in self.page.url or 'timeline' in self.page.url:
                self.logger.info('Already logged in to Twitter')
                return True

            # Manual login required
            self.logger.warning('Manual login required')
            self.logger.info('Please log in to Twitter within 90 seconds...')
            
            try:
                self.page.wait_for_url('**/home**', timeout=90000)
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
        Check for new notifications/mentions.

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
                self.page.goto('https://twitter.com/notifications', wait_until='networkidle')
                self.page.wait_for_timeout(8000)  # Wait for content to load

                notifications = self._parse_notifications()

            except Exception as e:
                self.logger.error(f'Error parsing notifications: {e}')

        except Exception as e:
            self.logger.error(f'Check updates error: {e}')
            self._cleanup()

        return notifications

    def _parse_notifications(self) -> list:
        """Parse Twitter notifications."""
        notifications = []

        try:
            # Twitter notification selectors (may need updates based on UI changes)
            notification_selectors = [
                '[data-testid="notification"]',
                'article[role="article"]',
                '[data-testid="primaryColumn"] article',
            ]

            for selector in notification_selectors:
                try:
                    elements = self.page.query_selector_all(selector)
                    self.logger.info(f'Found {len(elements)} notification elements')

                    for elem in elements[:15]:  # Limit to 15 recent
                        try:
                            text = elem.inner_text()
                            
                            # Check for keywords
                            matched_keywords = [kw for kw in self.keywords if kw.lower() in text.lower()]
                            
                            # Determine notification type
                            notif_type = 'unknown'
                            if 'mentioned you' in text.lower() or '@' in text:
                                notif_type = 'mention'
                            elif 'liked your' in text.lower():
                                notif_type = 'like'
                            elif 'reposted' in text.lower():
                                notif_type = 'repost'
                            elif 'followed you' in text.lower():
                                notif_type = 'follow'
                            elif 'message' in text.lower() or 'DM' in text.lower():
                                notif_type = 'message'

                            if matched_keywords or notif_type in ['mention', 'message']:
                                notifications.append({
                                    'platform': 'twitter',
                                    'type': notif_type,
                                    'text': text[:500],
                                    'keywords': matched_keywords,
                                    'timestamp': datetime.now()
                                })
                                self.logger.info(f"Twitter {notif_type}: {matched_keywords}")
                        except:
                            continue

                    if elements:
                        break
                except:
                    continue

        except Exception as e:
            self.logger.error(f'Twitter parse error: {e}')

        return notifications

    def create_action_file(self, item) -> Path:
        """
        Create action file for a notification.

        Args:
            item: Notification dict

        Returns:
            Path to created file
        """
        filename = self.generate_filename('TWITTER_NOTIF', item['type'])
        filepath = self.needs_action / filename

        content = f'''---
type: twitter_notification
platform: twitter
notification_type: {item['type']}
received: {item['timestamp'].isoformat()}
keywords: {', '.join(item['keywords'])}
priority: {"high" if item['type'] in ['mention', 'message'] else "medium"}
status: pending
---

# Twitter Notification

## Notification Type
{item['type'].title()}

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
*Created by Twitter Watcher - AI Employee v0.1*
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
        self.logger.info('Starting Twitter Watcher')
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
            self.logger.info('Stopping Twitter Watcher...')
            self._cleanup()
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            self._cleanup()
            raise

    def demo_mode_create_sample(self) -> Path:
        """Create a sample notification file for testing."""
        filename = self.generate_filename('TWITTER_DEMO', 'mention')
        filepath = self.needs_action / filename

        content = f'''---
type: twitter_notification
platform: twitter
notification_type: mention
received: {datetime.now().isoformat()}
keywords: mention, question
priority: high
status: pending
---

# Twitter Notification (DEMO)

## Notification Type
Mention

## Content
@YourBusiness Hey, I have a question about your services. 
Can you help me with pricing for enterprise plans?

## Detected Keywords
- mention
- question

## Suggested Actions
- [ ] Review mention
- [ ] Draft response with pricing info
- [ ] Get approval
- [ ] Send response

## Notes
This is a DEMO message for testing.
In production, this would be a real Twitter mention.

---
*Created by Twitter Watcher (Demo Mode) - AI Employee v0.1*
'''

        filepath.write_text(content, encoding='utf-8')
        self.logger.info('Created demo Twitter action file')
        return filepath


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Twitter (X) Watcher')
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

    watcher = TwitterWatcher(str(vault_path), args.interval, args.session_path)

    if args.demo:
        watcher.demo_mode_create_sample()
        print(f'Demo file created in {vault_path}/Needs_Action/')
        return

    watcher.run()


if __name__ == '__main__':
    main()
