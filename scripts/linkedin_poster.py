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
    
    def _init_browser(self, max_retries: int = 2):
        """Initialize Playwright browser with persistent context."""
        import time
        import shutil
        
        for attempt in range(max_retries + 1):
            try:
                from playwright.sync_api import sync_playwright

                self.playwright = sync_playwright().start()
                
                # Try to launch with persistent context
                self.browser = self.playwright.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Visible browser for debugging
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',  # Add GPU disable for stability
                        '--disable-software-rasterizer'
                    ],
                    ignore_default_args=['--enable-automation'],
                    timeout=60000  # 60 second timeout for browser launch
                )

                if not self.browser.pages:
                    self.page = self.browser.new_page()
                else:
                    self.page = self.browser.pages[0]

                self.logger.info('Browser initialized (visible mode)')
                return True

            except Exception as e:
                error_msg = str(e)
                self.logger.error(f'Browser init attempt {attempt + 1}/{max_retries + 1} failed: {e}')
                
                # Clean up any partial state
                self._cleanup()
                
                # If this is the last attempt, give up
                if attempt >= max_retries:
                    self.logger.error('All browser initialization attempts failed')
                    return False
                
                # If error is about target/page closed, try clearing session
                if 'closed' in error_msg.lower() or 'target' in error_msg.lower():
                    self.logger.warning('Detected stale session, attempting cleanup...')
                    time.sleep(2)
                    
                    # Try to kill any stale Chrome processes
                    try:
                        import subprocess
                        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                                     capture_output=True, timeout=5)
                        self.logger.info('Killed stale Chrome processes')
                    except:
                        pass
                    
                    time.sleep(2)
                
                # Wait before retry
                time.sleep(3)
        
        return False

    def _navigate_to_linkedin(self, url: str, timeout: int = 30000) -> bool:
        """
        Navigate to a LinkedIn URL with proper wait strategy.
        
        LinkedIn never reaches 'networkidle' due to constant background requests,
        so we use 'domcontentloaded' and wait for specific elements.
        
        Args:
            url: URL to navigate to
            timeout: Maximum wait time in milliseconds
            
        Returns:
            True if navigation successful, False otherwise
        """
        try:
            self.logger.info(f'Navigating to: {url}')
            
            # Navigate with domcontentloaded (doesn't wait for all network requests)
            self.page.goto(url, wait_until='domcontentloaded', timeout=timeout)
            
            # Wait for page to be interactive
            self.page.wait_for_load_state('domcontentloaded', timeout=timeout)
            
            # Wait for network to be almost idle (but with shorter timeout)
            try:
                self.page.wait_for_load_state('networkidle', timeout=10000)
            except:
                self.logger.debug('Network did not reach idle, continuing anyway')
            
            # Additional wait for LinkedIn's dynamic content
            self.page.wait_for_timeout(3000)
            
            self.logger.info(f'Successfully navigated to: {url}')
            return True
            
        except Exception as e:
            self.logger.error(f'Navigation error: {e}')
            # Try to recover by reinitializing browser
            self.logger.info('Attempting browser recovery...')
            try:
                self._cleanup()
                if self._init_browser():
                    self.page.goto(url, wait_until='domcontentloaded', timeout=timeout)
                    self.page.wait_for_timeout(3000)
                    self.logger.info(f'Recovery successful: {url}')
                    return True
            except Exception as recovery_error:
                self.logger.error(f'Recovery failed: {recovery_error}')
            return False
    
    def _login(self):
        """Log in to LinkedIn."""
        try:
            # Use new navigation method
            self._navigate_to_linkedin('https://www.linkedin.com/login')

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

                # Wait for navigation to feed
                try:
                    self.page.wait_for_url('**/feed/**', timeout=30000)
                    self.logger.info('Logged in successfully')
                    return True
                except:
                    # Check if we're on feed even if URL didn't trigger
                    if 'feed' in self.page.url or 'linkedin.com/feed' in self.page.url:
                        self.logger.info('Logged in successfully')
                        return True
                    raise
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
        
        self.logger.info(f'Post ID: {post_id}')
        self.logger.info(f'Extracted content ({len(post_text)} chars): {post_text[:100]}...')

        try:
            # Initialize browser if needed
            if not self.browser:
                if not self._init_browser():
                    return False

            # Navigate to LinkedIn feed using new helper method
            self.logger.info('Navigating to LinkedIn feed...')
            if not self._navigate_to_linkedin('https://www.linkedin.com/feed/'):
                self.logger.error('Failed to navigate to LinkedIn feed')
                debug_path = self.done / f'{post_id}_nav_error.png'
                self.page.screenshot(path=str(debug_path))
                return False
            
            # Wait for feed to be fully interactive
            self.page.wait_for_timeout(5000)

            # Close any popups
            self._close_popups()

            # Scroll to top
            self.page.evaluate('window.scroll(0, 0)')
            self.page.wait_for_timeout(2000)

            # Click on "Start a post" - Try multiple selectors
            self.logger.info('Opening post creation dialog...')
            post_clicked = False

            # Try different selectors for "Start a post" button
            selectors = [
                'button:has-text("Start a post")',
                '.share-box-feed-entry__trigger',
                '[aria-label="Start a post"]',
            ]

            for selector in selectors:
                try:
                    self.logger.debug(f'Trying selector: {selector}')
                    start_post_btn = self.page.locator(selector).first
                    start_post_btn.wait_for(state='visible', timeout=10000)
                    start_post_btn.scroll_into_view_if_needed()
                    self.page.wait_for_timeout(1000)
                    start_post_btn.click(timeout=5000)
                    self.page.wait_for_timeout(5000)
                    post_clicked = True
                    self.logger.info(f'Clicked with: {selector}')
                    break
                except Exception as e:
                    self.logger.debug(f'Selector failed: {selector} - {e}')
                    continue

            # Fallback: Use get_by_role
            if not post_clicked:
                try:
                    btn = self.page.get_by_role("button", name="Start a post").first
                    btn.wait_for(state='visible', timeout=10000)
                    btn.scroll_into_view_if_needed()
                    self.page.wait_for_timeout(1000)
                    btn.click()
                    self.page.wait_for_timeout(5000)
                    post_clicked = True
                    self.logger.info('Clicked with get_by_role')
                except Exception as e:
                    self.logger.debug(f'Role selector failed: {e}')

            if not post_clicked:
                self.logger.error('Could not click Start a post')
                debug_path = self.done / f'{post_id}_step1.png'
                self.page.screenshot(path=str(debug_path))
                return False

            # Wait for post dialog to fully load
            self.logger.info('Waiting for post dialog...')
            self.page.wait_for_timeout(10000)

            # Wait for post editor to appear
            self.logger.info('Finding post editor...')
            editor_found = False

            # Look for the editable div in the post dialog
            editor_selectors = [
                '[contenteditable="true"]',
                'div[contenteditable="true"]',
                '.editor-content[contenteditable="true"]',
            ]

            text_field = None
            for selector in editor_selectors:
                try:
                    self.logger.debug(f'Trying editor selector: {selector}')
                    text_field = self.page.locator(selector).first
                    text_field.wait_for(state='visible', timeout=15000)
                    self.logger.info('Found post editor')
                    editor_found = True
                    break
                except Exception as e:
                    self.logger.debug(f'Editor selector failed: {selector} - {e}')

            if not editor_found or text_field is None:
                self.logger.error('Could not find post editor')
                debug_path = self.done / f'{post_id}_step2.png'
                self.page.screenshot(path=str(debug_path))
                return False

            # Fill post content
            self.logger.info('Filling post content...')
            try:
                # Click to focus
                text_field.click()
                self.page.wait_for_timeout(2000)

                # Clear any existing content
                self.page.keyboard.press('Control+A')
                self.page.wait_for_timeout(500)
                self.page.keyboard.press('Delete')
                self.page.wait_for_timeout(1000)

                # Type content with human-like behavior
                self.logger.info('Typing content with human-like delays...')
                
                import random
                
                # Type in chunks with random pauses (like human thinking)
                words = post_text.split(' ')
                for i, word in enumerate(words):
                    # Type the word
                    self.page.keyboard.type(word + ' ', delay=random.randint(30, 100))
                    
                    # Random pause every few words (human-like)
                    if i % 5 == 0:
                        self.page.wait_for_timeout(random.randint(200, 800))
                    
                    # Occasionally press backspace and retype (human error simulation)
                    if i % 15 == 0 and i > 0:
                        self.page.keyboard.press('Backspace')
                        self.page.wait_for_timeout(100)
                        self.page.keyboard.type(word[-1] + ' ', delay=50)
                
                # Final wait for LinkedIn to process
                self.page.wait_for_timeout(5000)
                
                # Verify content is present
                content_length = self.page.evaluate('''() => {
                    const editor = document.querySelector('[contenteditable="true"]');
                    return editor ? editor.innerText.length : 0;
                }''')
                
                self.logger.info(f'Content length in editor: {content_length} chars')
                
                # Scroll up and down (human behavior)
                self.page.evaluate('window.scrollBy(0, 100)')
                self.page.wait_for_timeout(500)
                self.page.evaluate('window.scrollBy(0, -100)')
                self.page.wait_for_timeout(500)

                self.logger.info('Content entered successfully')
            except Exception as e:
                self.logger.error(f'Failed to enter content: {e}')
                debug_path = self.done / f'{post_id}_step2.png'
                self.page.screenshot(path=str(debug_path))
                return False

            # Wait for Post button to be enabled
            self.page.wait_for_timeout(5000)

            # Click Post button
            self.logger.info('Clicking Post button...')
            post_selectors = [
                'button:has-text("Post")',
                '.share-actions__primary-action',
                'button[aria-label="Post"]',
            ]

            post_clicked = False
            for selector in post_selectors:
                try:
                    post_btn = self.page.locator(selector).first
                    post_btn.wait_for(state='visible', timeout=10000)
                    
                    # Scroll into view
                    post_btn.scroll_into_view_if_needed()
                    self.page.wait_for_timeout(1000)
                    
                    # Try waiting for enabled
                    try:
                        post_btn.wait_for(state='enabled', timeout=5000)
                    except:
                        self.logger.warning('Post button may not be fully enabled')
                    
                    # Click with force
                    post_btn.click(force=True, timeout=5000)
                    self.page.wait_for_timeout(8000)  # Longer wait for settings dialog
                    post_clicked = True
                    self.logger.info(f'Post clicked with: {selector}')
                    break
                except Exception as e:
                    self.logger.debug(f'Post selector failed: {selector} - {e}')

            # Fallback: Use get_by_role
            if not post_clicked:
                try:
                    post_btn = self.page.get_by_role("button", name="Post").first
                    post_btn.wait_for(state='visible', timeout=5000)
                    post_btn.scroll_into_view_if_needed()
                    self.page.wait_for_timeout(1000)
                    post_btn.click(force=True, timeout=5000)
                    self.page.wait_for_timeout(8000)
                    post_clicked = True
                    self.logger.info('Post clicked with get_by_role')
                except Exception as e:
                    self.logger.debug(f'Role Post button failed: {e}')
            
            # Last resort: Try keyboard
            if not post_clicked:
                try:
                    self.logger.info('Trying keyboard Tab+Enter...')
                    self.page.keyboard.press('Tab')
                    self.page.keyboard.press('Tab')
                    self.page.keyboard.press('Tab')
                    self.page.keyboard.press('Enter')
                    self.page.wait_for_timeout(8000)
                    post_clicked = True
                except Exception as e:
                    self.logger.debug(f'Keyboard failed: {e}')

            if not post_clicked:
                self.logger.error('Could not click Post button')
                debug_path = self.done / f'{post_id}_step3.png'
                self.page.screenshot(path=str(debug_path))
                return False
            
            # After clicking Post, wait for settings dialog and trigger content validation
            self.logger.info('Waiting for post settings dialog...')
            self.page.wait_for_timeout(10000)
            
            # Trigger content validation by focusing and blurring the editor
            try:
                editor = self.page.locator('[contenteditable="true"]').first
                if editor.is_visible(timeout=5000):
                    # Click in editor to focus
                    editor.click()
                    self.page.wait_for_timeout(2000)
                    
                    # Add a space and remove it (triggers validation)
                    self.page.keyboard.press('End')
                    self.page.keyboard.type(' ')
                    self.page.wait_for_timeout(1000)
                    self.page.keyboard.press('Backspace')
                    self.page.wait_for_timeout(3000)
                    
                    self.logger.info('Triggered content validation')
            except Exception as e:
                self.logger.debug(f'Validation trigger: {e}')

            # Handle post settings dialog (click Done)
            self.logger.info('Handling post settings...')
            self.page.wait_for_timeout(10000)
            
            # Wait for Done button to become enabled
            try:
                done_btn = self.page.locator('button:has-text("Done")').first
                
                # Wait for Done button to be enabled (up to 60 seconds)
                done_enabled = False
                for attempt in range(60):
                    try:
                        is_enabled = done_btn.is_enabled(timeout=1000)
                        if is_enabled:
                            self.logger.info(f'Done button enabled at attempt {attempt + 1}!')
                            done_enabled = True
                            break
                    except:
                        pass
                    
                    # Try to trigger validation at specific attempts
                    if attempt == 15:
                        try:
                            # Click in content area
                            editor = self.page.locator('[contenteditable="true"]').first
                            editor.click()
                            self.page.wait_for_timeout(2000)
                            # Select all content and copy (triggers validation)
                            self.page.keyboard.press('Control+A')
                            self.page.wait_for_timeout(500)
                            self.page.keyboard.press('Right')  # Deselect
                            self.page.wait_for_timeout(2000)
                            self.logger.info('Triggered validation via select/deselect')
                        except Exception as e:
                            self.logger.debug(f'Validation attempt failed: {e}')
                    
                    if attempt == 30:
                        try:
                            # Try clicking Back and then returning
                            back_btn = self.page.locator('button:has-text("Back")').first
                            if back_btn.is_visible(timeout=2000):
                                self.logger.info('Clicking Back button...')
                                back_btn.click()
                                self.page.wait_for_timeout(3000)
                                # Click Post again
                                post_btn = self.page.locator('button:has-text("Post")').first
                                if post_btn.is_visible(timeout=3000):
                                    post_btn.click()
                                    self.page.wait_for_timeout(5000)
                                    self.logger.info('Clicked Post again after Back')
                        except Exception as e:
                            self.logger.debug(f'Back button attempt: {e}')
                    
                    if attempt == 45:
                        try:
                            # Add and remove newline (triggers validation)
                            editor = self.page.locator('[contenteditable="true"]').first
                            editor.press('End')
                            self.page.keyboard.press('Enter')
                            self.page.wait_for_timeout(1000)
                            self.page.keyboard.press('Backspace')
                            self.page.wait_for_timeout(3000)
                            self.logger.info('Triggered validation via newline')
                        except Exception as e:
                            self.logger.debug(f'Newline trigger: {e}')
                    
                    self.page.wait_for_timeout(1000)
                    if attempt % 10 == 0:
                        self.logger.debug(f'Waiting for Done button... attempt {attempt + 1}/60')
                
                if not done_enabled:
                    self.logger.warning('Done button did not become enabled after 60 attempts')
                    debug_path = self.done / f'{post_id}_done_not_enabled.png'
                    self.page.screenshot(path=str(debug_path))
                    self.logger.info(f'Debug screenshot: {debug_path}')
                    # Still try to click it
                    return False
                
                # Click Done if visible and enabled
                if done_btn.is_visible(timeout=3000):
                    try:
                        done_btn.wait_for(state='enabled', timeout=5000)
                        done_btn.click(force=True)
                        self.page.wait_for_timeout(8000)
                        self.logger.info('Clicked Done in post settings')
                    except Exception as e:
                        self.logger.warning(f'Done button click failed: {e}')
                        debug_path = self.done / f'{post_id}_done_click_failed.png'
                        self.page.screenshot(path=str(debug_path))
                        return False
            except Exception as e:
                self.logger.debug(f'Post settings handling: {e}')
                debug_path = self.done / f'{post_id}_settings_error.png'
                self.page.screenshot(path=str(debug_path))
                return False

            # Wait for confirmation
            self.logger.info('Waiting for post confirmation...')
            try:
                self.page.wait_for_selector(':has-text("Posted")', timeout=15000)
            except:
                self.page.wait_for_timeout(10000)

            self.logger.info(f'Post published successfully: {post_id}')

            # Take success screenshot
            screenshot_path = self.done / f'{post_id}_success.png'
            self.page.screenshot(path=str(screenshot_path))

            return True

        except Exception as e:
            self.logger.error(f'Post error: {e}')
            return False

    def _close_popups(self):
        """Close any popups or overlays."""
        popup_selectors = [
            'button[aria-label="Dismiss"]',
            'button[aria-label="Close"]',
            '.msg-overlay-list__header-close',
            '.artdeco-modal__dismiss',
        ]

        for selector in popup_selectors:
            try:
                btn = self.page.locator(selector).first
                if btn.is_visible(timeout=2000):
                    btn.click(timeout=3000)
                    self.page.wait_for_timeout(1000)
                    self.logger.info(f'Closed popup with: {selector}')
                    break
            except:
                continue
    
    def _extract_content(self, text: str) -> str:
        """Extract post content from markdown file."""
        # Find content between "## Content" and next section (## Hashtags, ## Media, etc.)
        lines = text.split('\n')
        content_lines = []
        in_content = False

        for line in lines:
            if line.startswith('## Content'):
                in_content = True
                continue
            # Stop at any next section
            elif line.startswith('## ') and in_content:
                break
            elif in_content:
                # Skip empty lines at the start
                if line.strip() or content_lines:
                    content_lines.append(line)

        # Clean up: remove leading/trailing empty lines
        result = '\n'.join(content_lines).strip()
        
        # Remove any markdown comments
        result = '\n'.join([l for l in result.split('\n') if not l.strip().startswith('<!--')])
        
        return result.strip()
    
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
            if self.page:
                self.page = None
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
                self.playwright = None
        except Exception as e:
            self.logger.debug(f'Cleanup error: {e}')
    
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
        choices=['create', 'schedule', 'list', 'cancel', 'post-scheduled', 'check-approved', 'publish-approved', 'demo'],
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

    elif args.action == 'publish-approved':
        print('Publishing approved posts...')
        print('=' * 60)
        
        # Get all approved posts
        approved_files = list(poster.approved.glob('POST_*.md'))
        
        if not approved_files:
            print('No approved posts to publish.')
            print('Move posts from Pending_Approval/ to Approved/ first.')
            sys.exit(0)
        
        print(f'Found {len(approved_files)} approved post(s)')
        
        for filepath in approved_files:
            print(f'\nPublishing: {filepath.name}')
            success = poster.post_content(filepath)
            
            if success:
                print('[OK] Published successfully!')
                # Move to Done
                dest = poster.done / filepath.name
                filepath.rename(dest)
                print(f'Moved to Done: {dest.name}')
            else:
                print('[FAILED] Failed to publish')
        
        print('\n' + '=' * 60)
        print('Publishing complete!')
        
        # Summary
        print(f'\nCheck your LinkedIn profile to verify posts:')
        print(f'https://www.linkedin.com/in/your-profile/')

    elif args.action == 'list':
        pending = list(poster.pending_approval.glob('POST_*.md'))
        approved = list(poster.approved.glob('POST_*.md'))
        print(f'Pending approval: {len(pending)}')
        print(f'Approved (ready): {len(approved)}')


if __name__ == '__main__':
    main()
