"""
LinkedIn Poster - Create and post content to LinkedIn
Uses Playwright for browser automation
Requires human approval before posting
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()


class LinkedInPoster:
    """
    LinkedIn Poster for business content.
    Creates draft posts, handles approval workflow, and posts via Playwright.
    """
    
    def __init__(self, vault_path: str, session_path: str = None):
        """
        Initialize LinkedIn Poster.
        
        Args:
            vault_path: Path to the Obsidian vault root
            session_path: Path to store browser session (default: ./linkedin_session)
        """
        self.vault_path = Path(vault_path).resolve()
        self.session_path = Path(session_path) if session_path else Path('./linkedin_session')
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Folder paths
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        
        # Ensure folders exist
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        self.approved.mkdir(parents=True, exist_ok=True)
        self.done.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.email = os.getenv('LINKEDIN_EMAIL', '')
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
        Create a LinkedIn post draft file for approval.
        
        Args:
            content: Post content text
            hashtags: List of hashtags
            category: Post category (business_update, lead_generation, etc.)
            image_path: Optional path to image file
            
        Returns:
            Path to created draft file
        """
        post_id = f"POST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filename = f"{post_id}.md"
        filepath = self.pending_approval / filename
        
        hashtags = hashtags or ['#Business', '#Innovation']
        hashtags_str = ' '.join(hashtags)
        
        has_media = "No" if not image_path else f"Yes: {image_path}"
        
        content_md = f'''---
type: linkedin_post_draft
post_id: {post_id}
created: {datetime.now().isoformat()}
category: {category}
status: pending_approval
approval_required: {str(self.approval_required).lower()}
has_media: {has_media}
---

# LinkedIn Post Draft: {post_id}

## Content
{content}

## Hashtags
{hashtags_str}

## Media
{has_media}

## Posting Schedule
- [ ] Post immediately (after approval)
- [ ] Schedule for: [datetime]

## To Approve
1. Review content above
2. Move this file to /Approved/ to post
3. Move to /Rejected/ to cancel

## Notes
<!-- Add any notes or context here -->

---
*Created by LinkedIn Poster - AI Employee v0.1*
'''
        
        filepath.write_text(content_md, encoding='utf-8')
        self.logger.info(f'Created post draft: {filepath.name}')
        return filepath
    
    def check_approved_posts(self) -> list:
        """
        Check for approved posts ready to publish.
        
        Returns:
            List of approved post files
        """
        if not self.approved.exists():
            return []
        
        approved_files = []
        for f in self.approved.iterdir():
            if f.suffix == '.md' and 'linkedin_post' in f.read_text():
                approved_files.append(f)
        
        return approved_files
    
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
            if 'feed' in self.page.url:
                self.logger.info('Already logged in')
                return True
            
            # Fill login form
            if self.email:
                self.page.fill('#username', self.email)
            
            password = os.getenv('LINKEDIN_PASSWORD', '')
            if password:
                self.page.fill('#password', password)
                self.page.click('button[type="submit"]')
                
                # Wait for navigation
                self.page.wait_for_url('**/feed/**', timeout=30000)
                self.logger.info('Logged in successfully')
                return True
            else:
                self.logger.warning('No credentials provided - manual login required')
                self.logger.info('Please log in manually within 60 seconds...')
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
    
    def post_content(self, filepath: Path) -> bool:
        """
        Post content to LinkedIn.
        
        Args:
            filepath: Path to approved post file
            
        Returns:
            True if successful, False otherwise
        """
        content = filepath.read_text(encoding='utf-8')
        
        # Parse post content
        post_text = self._extract_content(content)
        post_id = self._extract_post_id(content)
        
        try:
            # Initialize browser if needed
            if not self.browser:
                if not self._init_browser():
                    return False
            
            # Login if needed
            if 'feed' not in self.page.url:
                if not self._login():
                    return False
            
            # Navigate to post creation
            self.logger.info('Creating post...')
            self.page.goto('https://www.linkedin.com/feed/', wait_until='networkidle')
            
            # Click on "Start a post"
            try:
                start_post_btn = self.page.locator('button:has-text("Start a post")').first
                start_post_btn.click(timeout=5000)
            except:
                # Try alternative selector
                start_post_btn = self.page.locator('[aria-label="Start a post"]').first
                start_post_btn.click(timeout=5000)
            
            # Wait for post dialog
            self.page.wait_for_selector('[contenteditable="true"]', timeout=5000)
            
            # Fill post content
            text_field = self.page.locator('[contenteditable="true"]').first
            text_field.fill(post_text)
            
            # TODO: Add image upload support
            
            # Click Post button
            post_btn = self.page.locator('button:has-text("Post")').first
            post_btn.click(timeout=5000)
            
            # Wait for confirmation
            self.page.wait_for_selector(':has-text("Posted")', timeout=10000)
            
            self.logger.info(f'Post published successfully: {post_id}')
            
            # Take screenshot
            screenshot_path = self.done / f'{post_id}_screenshot.png'
            self.page.screenshot(path=str(screenshot_path))
            
            return True
            
        except Exception as e:
            self.logger.error(f'Post error: {e}')
            return False
    
    def _extract_content(self, text: str) -> str:
        """Extract post content from markdown file."""
        # Find content between "## Content" and "## Hashtags"
        lines = text.split('\n')
        content_lines = []
        in_content = False
        
        for line in lines:
            if line.startswith('## Content'):
                in_content = True
                continue
            elif line.startswith('## Hashtags'):
                break
            elif in_content and line.strip():
                content_lines.append(line)
        
        return '\n'.join(content_lines).strip()
    
    def _extract_post_id(self, text: str) -> str:
        """Extract post ID from markdown file."""
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
        except:
            pass
    
    def create_demo_post(self) -> Path:
        """
        Create a demo post for testing.
        
        Returns:
            Path to created demo file
        """
        content = """🚀 Excited to share some amazing news!

We just helped a client achieve 10x ROI through AI automation.

Their challenge: Manual invoice processing taking 15 hours/week
Our solution: Custom AI agent with 99% accuracy  
Result: 15 hours saved weekly, zero processing errors

Ready to transform your business? Let's connect!

#AI #Automation #BusinessEfficiency #DigitalTransformation #Innovation"""
        
        return self.create_post_draft(
            content=content,
            hashtags=['#AI', '#Automation', '#BusinessEfficiency', '#DigitalTransformation', '#Innovation'],
            category='lead_generation'
        )


def main():
    """
    Main entry point for LinkedIn Poster.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Poster for AI Employee')
    parser.add_argument(
        '--vault', 
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--action',
        choices=['create', 'schedule', 'list', 'cancel', 'post-scheduled', 'check-approved', 'demo'],
        default='demo',
        help='Action to perform'
    )
    parser.add_argument(
        '--content',
        default='',
        help='Post content'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Create demo post'
    )
    
    args = parser.parse_args()
    
    # Resolve vault path
    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()
    
    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        sys.exit(1)
    
    poster = LinkedInPoster(str(vault_path))
    
    if args.demo or args.action == 'demo':
        filepath = poster.create_demo_post()
        print(f'Demo post created: {filepath}')
        print(f'Location: {vault_path}/Pending_Approval/')
        print('\nTo approve: Move file to /Approved/')
        print('To cancel: Move file to /Rejected/')
    
    elif args.action == 'create':
        if not args.content:
            print('Error: --content required for create action')
            sys.exit(1)
        filepath = poster.create_post_draft(args.content)
        print(f'Post draft created: {filepath}')
    
    elif args.action == 'check-approved':
        approved = poster.check_approved_posts()
        if approved:
            print(f'Found {len(approved)} approved post(s) ready to publish')
            for f in approved:
                print(f'  - {f.name}')
        else:
            print('No approved posts waiting')
    
    elif args.action == 'list':
        pending = list(poster.pending_approval.glob('POST_*.md'))
        approved = list(poster.approved.glob('POST_*.md'))
        print(f'Pending approval: {len(pending)}')
        print(f'Approved (ready): {len(approved)}')


if __name__ == '__main__':
    main()
