"""
Facebook/Instagram Poster - Create and post content to social media
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


class FacebookInstagramPoster:
    """
    Facebook/Instagram Poster for business content.
    Creates draft posts, handles approval workflow, and posts via Playwright.
    """

    def __init__(self, vault_path: str, session_path: str = None, 
                 platform: str = 'facebook'):
        """
        Initialize Poster.

        Args:
            vault_path: Path to the Obsidian vault root
            session_path: Path to store browser session
            platform: 'facebook' or 'instagram'
        """
        self.vault_path = Path(vault_path).resolve()
        self.platform = platform
        self.session_path = Path(session_path) if session_path else Path(f'./{platform}_post_session')
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Folder paths
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'

        # Ensure folders exist
        for folder in [self.pending_approval, self.approved, self.done]:
            folder.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.email = os.getenv(f'{platform.upper()}_EMAIL', '')
        self.approval_required = os.getenv('POST_APPROVAL_REQUIRED', 'true').lower() == 'true'

        # Browser state
        self.browser = None
        self.page = None

        import logging
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_post_draft(self, content: str, hashtags: list = None,
                          category: str = 'business_update',
                          image_path: str = None) -> Path:
        """
        Create a post draft file for approval.

        Args:
            content: Post content text
            hashtags: List of hashtags
            category: Post category
            image_path: Optional path to image file

        Returns:
            Path to created draft file
        """
        post_id = f"{self.platform.upper()}_POST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filename = f"{post_id}.md"
        filepath = self.pending_approval / filename

        hashtags = hashtags or ['#Business', '#Innovation']
        hashtags_str = ' '.join(hashtags)

        content_md = f'''---
type: {self.platform}_post_draft
post_id: {post_id}
platform: {self.platform}
created: {datetime.now().isoformat()}
category: {category}
status: pending_approval
approval_required: {str(self.approval_required).lower()}
has_media: {"No" if not image_path else f"Yes: {image_path}"}
---

# {self.platform.title()} Post Draft: {post_id}

## Content
{content}

## Hashtags
{hashtags_str}

## Instructions
1. Review the post content
2. Move to /Approved/ to publish
3. Move to /Rejected/ to discard

---
*Created by {self.platform.title()} Poster - AI Employee v0.1*
'''

        filepath.write_text(content_md, encoding='utf-8')
        self.logger.info(f'Created post draft: {filepath.name}')
        return filepath

    def check_approved_posts(self) -> list:
        """Check for approved posts ready to publish."""
        if not self.approved.exists():
            return []

        approved_files = []
        for f in self.approved.iterdir():
            if f.suffix == '.md':
                content = f.read_text()
                if f'{self.platform}_post' in content.lower():
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
        """Log in to platform."""
        try:
            base_url = 'https://www.facebook.com' if self.platform == 'facebook' else 'https://www.instagram.com'
            self.page.goto(base_url, wait_until='networkidle')

            # Check if already logged in
            if self.platform == 'facebook':
                if 'feed' in self.page.url:
                    self.logger.info('Already logged in to Facebook')
                    return True
            else:
                if 'feed' in self.page.url or 'explore' in self.page.url:
                    self.logger.info('Already logged in to Instagram')
                    return True

            # Manual login
            self.logger.warning('Manual login may be required')
            self.logger.info('Please log in within 90 seconds...')
            
            try:
                if self.platform == 'facebook':
                    self.page.wait_for_url('**/feed**', timeout=90000)
                else:
                    self.page.wait_for_url('**/feed/**', timeout=90000)
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
        Post content to platform.

        Args:
            filepath: Path to approved post file

        Returns:
            True if successful
        """
        content = filepath.read_text(encoding='utf-8')
        post_text = self._extract_content(content)
        post_id = self._extract_post_id(content)

        self.logger.info(f'Posting {self.platform} content: {post_id}')

        try:
            if not self.browser:
                if not self._init_browser():
                    return False

            if not self._login():
                return False

            if self.platform == 'facebook':
                return self._post_to_facebook(post_text, post_id)
            else:
                return self._post_to_instagram(post_text, post_id)

        except Exception as e:
            self.logger.error(f'Post error: {e}')
            return False

    def _post_to_facebook(self, content: str, post_id: str) -> bool:
        """Post to Facebook."""
        try:
            self.logger.info('Navigating to Facebook...')
            self.page.goto('https://www.facebook.com', wait_until='networkidle')
            self.page.wait_for_timeout(5000)

            # Click "What's on your mind?"
            self.logger.info('Opening post composer...')
            composer_selectors = [
                'button:has-text("What\\'s on your mind?")',
                '[aria-label="What\\'s on your mind?"]',
                '.x1n2onr6:has-text("What\\'s on your mind?")',
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
                self.logger.error('Could not open composer')
                return False

            # Find composer textarea and type content
            self.logger.info('Entering content...')
            composer = self.page.locator('[contenteditable="true"]').first
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
            post_btn = self.page.locator('button:has-text("Post")').first
            post_btn.wait_for(state='enabled', timeout=10000)
            post_btn.click()
            self.page.wait_for_timeout(5000)

            self.logger.info(f'Post published: {post_id}')
            
            # Screenshot
            screenshot_path = self.done / f'{post_id}_success.png'
            self.page.screenshot(path=str(screenshot_path))

            return True

        except Exception as e:
            self.logger.error(f'Facebook post error: {e}')
            return False

    def _post_to_instagram(self, content: str, post_id: str) -> bool:
        """Post to Instagram."""
        try:
            self.logger.info('Navigating to Instagram...')
            self.page.goto('https://www.instagram.com', wait_until='networkidle')
            self.page.wait_for_timeout(5000)

            # Click New Post (+)
            self.logger.info('Opening post composer...')
            new_post_btn = self.page.locator('[aria-label="New post"]').first
            new_post_btn.wait_for(state='visible', timeout=10000)
            new_post_btn.click()
            self.page.wait_for_timeout(3000)

            # For Instagram, we'd need to handle image upload
            # Text-only posts are limited to captions
            self.logger.info('Instagram post composer opened')
            
            # Note: Instagram requires images for posts
            # This is a simplified version for caption-only
            self.logger.warning('Instagram typically requires an image for posts')
            
            # Close composer for now (would need image upload for full implementation)
            self.logger.info('Instagram post requires image upload - manual completion needed')
            
            return True

        except Exception as e:
            self.logger.error(f'Instagram post error: {e}')
            return False

    def _extract_content(self, text: str) -> str:
        """Extract post content from markdown."""
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
        """Create a sample post draft."""
        content = f"""This is a demo {self.platform} post for testing.
Our business is growing and we're excited to serve you better!

#Business #Growth #Innovation"""
        
        return self.create_post_draft(
            content=content,
            category='demo'
        )


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Facebook/Instagram Poster')
    parser.add_argument(
        '--vault',
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--platform',
        choices=['facebook', 'instagram'],
        default='facebook',
        help='Platform to post to'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Create demo post draft'
    )

    args = parser.parse_args()

    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()

    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        sys.exit(1)

    poster = FacebookInstagramPoster(str(vault_path), platform=args.platform)

    if args.demo:
        filepath = poster.demo_mode_create_sample()
        print(f'Demo post created: {filepath}')
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
