"""
Twitter (X) Poster - Create and post tweets
Uses Playwright for browser automation
Requires human approval before posting
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TwitterPoster:
    """
    Twitter Poster for business content.
    Creates draft tweets, handles approval workflow, and posts via Playwright.
    """

    def __init__(self, vault_path: str, session_path: str = None):
        """
        Initialize Twitter Poster.

        Args:
            vault_path: Path to the Obsidian vault root
            session_path: Path to store browser session
        """
        self.vault_path = Path(vault_path).resolve()
        self.session_path = Path(session_path) if session_path else Path('./twitter_post_session')
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Folder paths
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'

        # Ensure folders exist
        for folder in [self.pending_approval, self.approved, self.done]:
            folder.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.email = os.getenv('TWITTER_EMAIL', '')
        self.username = os.getenv('TWITTER_USERNAME', '')
        self.approval_required = os.getenv('POST_APPROVAL_REQUIRED', 'true').lower() == 'true'

        # Browser state
        self.browser = None
        self.page = None

        import logging
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_post_draft(self, content: str, hashtags: list = None,
                          category: str = 'business_update',
                          thread: bool = False) -> Path:
        """
        Create a tweet draft file for approval.

        Args:
            content: Tweet content text (max 280 chars for single tweet)
            hashtags: List of hashtags
            category: Post category
            thread: True if this is a thread

        Returns:
            Path to created draft file
        """
        post_id = f"TWITTER_POST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filename = f"{post_id}.md"
        filepath = self.pending_approval / filename

        hashtags = hashtags or ['#Business', '#Innovation']
        hashtags_str = ' '.join(hashtags)

        # Check character count
        char_count = len(content)

        content_md = f'''---
type: twitter_post_draft
post_id: {post_id}
platform: twitter
created: {datetime.now().isoformat()}
category: {category}
status: pending_approval
approval_required: {str(self.approval_required).lower()}
is_thread: {str(thread).lower()}
character_count: {char_count}
---

# Twitter Post Draft: {post_id}

## Content
{content}

## Hashtags
{hashtags_str}

## Character Count
{char_count} / 280

## Instructions
1. Review the tweet content
2. Ensure it meets Twitter character limit
3. Move to /Approved/ to publish
4. Move to /Rejected/ to discard

---
*Created by Twitter Poster - AI Employee v0.1*
'''

        filepath.write_text(content_md, encoding='utf-8')
        self.logger.info(f'Created tweet draft: {filepath.name}')
        return filepath

    def check_approved_posts(self) -> list:
        """Check for approved posts ready to publish."""
        if not self.approved.exists():
            return []

        approved_files = []
        for f in self.approved.iterdir():
            if f.suffix == '.md':
                content = f.read_text()
                if 'twitter_post' in content.lower():
                    approved_files.append(f)

        return approved_files

    def _init_browser(self):
        """Initialize Playwright browser."""
        try:
            from playwright.sync_api import sync_playwright

            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch_persistent_context(
                str(self.session_path),
                headless=False,  # Visible for debugging
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

            self.logger.info('Browser initialized')
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

            # Manual login
            self.logger.warning('Manual login may be required')
            self.logger.info('Please log in within 90 seconds...')
            
            try:
                self.page.wait_for_url('**/home**', timeout=90000)
                self.logger.info('Login detected!')
                return True
            except:
                self.logger.error('Login timeout')
                return False

        except Exception as e:
            self.logger.error(f'Login error: {e}')
            return False

    def post_content(self, filepath: Path) -> bool:
        """
        Post content to Twitter.

        Args:
            filepath: Path to approved post file

        Returns:
            True if successful
        """
        content = filepath.read_text(encoding='utf-8')
        post_text = self._extract_content(content)
        post_id = self._extract_post_id(content)

        self.logger.info(f'Posting Twitter content: {post_id}')

        try:
            if not self.browser:
                if not self._init_browser():
                    return False

            if not self._login():
                return False

            return self._post_tweet(post_text, post_id)

        except Exception as e:
            self.logger.error(f'Post error: {e}')
            return False

    def _post_tweet(self, content: str, post_id: str) -> bool:
        """Post a tweet."""
        try:
            self.logger.info('Navigating to Twitter...')
            self.page.goto('https://twitter.com', wait_until='networkidle')
            self.page.wait_for_timeout(5000)

            # Click "Post" or "What is happening?!"
            self.logger.info('Opening tweet composer...')
            composer_selectors = [
                '[data-testid="tweetButton-inline"]',
                '[aria-label="What is happening?!"]',
                '[data-testid="Drafts"]',
            ]

            clicked = False
            for selector in composer_selectors:
                try:
                    btn = self.page.locator(selector).first
                    btn.wait_for(state='visible', timeout=10000)
                    btn.click()
                    self.page.wait_for_timeout(3000)
                    clicked = True
                    break
                except:
                    continue

            if not clicked:
                # Try the main composer button
                try:
                    btn = self.page.get_by_role("button", name="Post").first
                    btn.wait_for(state='visible', timeout=10000)
                    btn.click()
                    self.page.wait_for_timeout(3000)
                    clicked = True
                except:
                    pass

            if not clicked:
                self.logger.error('Could not open tweet composer')
                return False

            # Find composer textarea and type content
            self.logger.info('Entering tweet content...')
            composer = self.page.locator('[data-testid="tweetTextarea_0"]').first
            composer.wait_for(state='visible', timeout=10000)
            composer.click()

            # Type with human-like delays
            import random
            words = content.split(' ')
            for word in words:
                self.page.keyboard.type(word + ' ', delay=random.randint(30, 100))
                if random.random() < 0.1:
                    self.page.wait_for_timeout(random.randint(200, 500))

            self.page.wait_for_timeout(2000)

            # Click Post button
            self.logger.info('Clicking Post...')
            post_btn = self.page.locator('[data-testid="tweetButton"]').first
            post_btn.wait_for(state='enabled', timeout=10000)
            post_btn.click()
            self.page.wait_for_timeout(5000)

            self.logger.info(f'Tweet published: {post_id}')
            
            # Screenshot
            screenshot_path = self.done / f'{post_id}_success.png'
            self.page.screenshot(path=str(screenshot_path))

            return True

        except Exception as e:
            self.logger.error(f'Twitter post error: {e}')
            return False

    def _extract_content(self, text: str) -> str:
        """Extract tweet content from markdown."""
        lines = text.split('\n')
        content_lines = []
        in_content = False

        for line in lines:
            if line.startswith('## Content'):
                in_content = True
                continue
            elif line.startswith('## ') and in_content:
                break
            elif in_content and line.strip():
                content_lines.append(line)

        return '\n'.join(content_lines).strip()

    def _extract_post_id(self, text: str) -> str:
        """Extract post ID."""
        for line in text.split('\n'):
            if line.startswith('post_id:'):
                return line.split(':')[1].strip()
        return 'UNKNOWN'

    def _cleanup(self):
        """Clean up browser resources."""
        try:
            if self.browser:
                self.browser.close()
                self.browser = None
                self.page = None
        except Exception as e:
            self.logger.error(f'Cleanup error: {e}')

    def demo_mode_create_sample(self) -> Path:
        """Create a sample tweet draft."""
        content = """Excited to announce our new AI-powered services! 
We're helping businesses automate their workflows and save time.

#AI #Automation #Business"""
        
        return self.create_post_draft(
            content=content,
            category='demo'
        )


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Twitter (X) Poster')
    parser.add_argument(
        '--vault',
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Create demo tweet draft'
    )

    args = parser.parse_args()

    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()

    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        sys.exit(1)

    poster = TwitterPoster(str(vault_path))

    if args.demo:
        filepath = poster.demo_mode_create_sample()
        print(f'Demo tweet created: {filepath}')
        return

    # Check for approved posts
    approved = poster.check_approved_posts()
    if approved:
        for post in approved:
            print(f'Posting: {post.name}')
            success = poster.post_content(post)
            if success:
                # Move to Done
                dest = poster.done / post.name
                post.rename(dest)
                print(f'Posted successfully: {dest.name}')
    else:
        print('No approved posts to publish')


if __name__ == '__main__':
    main()
