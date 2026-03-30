"""
Social Media MCP Server - Unified API Integration
Unified Model Context Protocol server for Facebook, Instagram, and Twitter
Uses official APIs instead of browser automation for reliability and ToS compliance
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import API clients
try:
    from facebook_graph_api import FacebookGraphAPI
except ImportError:
    FacebookGraphAPI = None

try:
    from instagram_graph_api import InstagramGraphAPI
except ImportError:
    InstagramGraphAPI = None

try:
    from twitter_api import TwitterAPI
except ImportError:
    TwitterAPI = None


class SocialMediaMCP:
    """
    Unified Social Media MCP for managing multiple platforms.
    Supports Facebook, Instagram, and Twitter via official APIs.
    """

    def __init__(self):
        """Initialize social media MCP clients."""
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        
        # Initialize clients
        self.facebook = FacebookGraphAPI() if FacebookGraphAPI else None
        self.instagram = InstagramGraphAPI() if InstagramGraphAPI else None
        self.twitter = TwitterAPI() if TwitterAPI else None

        import logging
        self.logger = logging.getLogger(self.__class__.__name__)

    def post_to_platform(self, platform: str, content: str,
                         media_url: str = None, **kwargs) -> dict:
        """
        Post content to a social media platform.

        Args:
            platform: Platform name (facebook, instagram, twitter)
            content: Post content text
            media_url: Optional media URL (image/video)
            **kwargs: Platform-specific options

        Returns:
            Post result dict
        """
        if self.dry_run:
            self.logger.info(f'[DRY RUN] Would post to {platform}: {content[:50]}...')
            return {
                'success': True,
                'platform': platform,
                'status': 'dry_run',
                'content': content[:100]
            }

        if platform.lower() == 'facebook':
            return self._post_to_facebook(content, media_url, **kwargs)
        elif platform.lower() == 'instagram':
            return self._post_to_instagram(content, media_url, **kwargs)
        elif platform.lower() == 'twitter':
            return self._post_to_twitter(content, **kwargs)
        else:
            return {'success': False, 'error': f'Unknown platform: {platform}'}

    def _post_to_facebook(self, content: str, media_url: str = None,
                          link: str = None, **kwargs) -> dict:
        """Post to Facebook."""
        if not self.facebook:
            return {'success': False, 'error': 'Facebook client not available'}

        if media_url:
            return self.facebook.create_photo_post(media_url, message=content)
        else:
            return self.facebook.create_post(content, link=link)

    def _post_to_instagram(self, content: str, media_url: str = None,
                           media_type: str = 'image', **kwargs) -> dict:
        """Post to Instagram."""
        if not self.instagram:
            return {'success': False, 'error': 'Instagram client not available'}

        if not media_url:
            return {'success': False, 'error': 'Instagram requires media (image/video)'}

        if media_type == 'video':
            return self.instagram.create_video_post(media_url, caption=content)
        else:
            return self.instagram.create_photo_post(media_url, caption=content)

    def _post_to_twitter(self, content: str, **kwargs) -> dict:
        """Post to Twitter."""
        if not self.twitter:
            return {'success': False, 'error': 'Twitter client not available'}

        # Check character limit
        if len(content) > 280:
            # Auto-thread long content
            tweets = self._split_into_tweets(content)
            return self.twitter.post_thread(tweets)
        else:
            return self.twitter.post_tweet(content)

    def _split_into_tweets(self, text: str) -> list:
        """Split long text into tweet thread."""
        tweets = []
        words = text.split(' ')
        current_tweet = ''

        for word in words:
            if len(current_tweet) + len(word) + 1 <= 280:
                current_tweet += ' ' + word if current_tweet else word
            else:
                if current_tweet:
                    tweets.append(current_tweet)
                current_tweet = word

        if current_tweet:
            tweets.append(current_tweet)

        return tweets

    def get_notifications(self, platform: str, limit: int = 10) -> list:
        """
        Get notifications from a platform.

        Args:
            platform: Platform name
            limit: Maximum notifications

        Returns:
            List of notifications
        """
        if platform.lower() == 'facebook':
            return self.facebook.get_notifications(limit) if self.facebook else []
        elif platform.lower() == 'twitter':
            return self.twitter.get_mentions(limit) if self.twitter else []
        # Instagram doesn't have direct notifications API
        return []

    def get_insights(self, platform: str, period: str = 'day') -> dict:
        """
        Get platform insights/analytics.

        Args:
            platform: Platform name
            period: Time period

        Returns:
            Insights dict
        """
        if platform.lower() == 'facebook':
            return {'insights': self.facebook.get_insights(period=period)} if self.facebook else {}
        elif platform.lower() == 'instagram':
            return {'insights': self.instagram.get_insights(period=period)} if self.instagram else {}
        elif platform.lower() == 'twitter':
            return self.twitter.get_account_metrics() if self.twitter else {}
        return {}

    def get_recent_posts(self, platform: str, limit: int = 5) -> list:
        """
        Get recent posts from a platform.

        Args:
            platform: Platform name
            limit: Maximum posts

        Returns:
            List of posts
        """
        if platform.lower() == 'facebook':
            return self.facebook.get_posts(limit) if self.facebook else []
        elif platform.lower() == 'instagram':
            return self.instagram.get_posts(limit) if self.instagram else []
        elif platform.lower() == 'twitter':
            return self.twitter.get_tweets(limit=limit) if self.twitter else []
        return []

    def verify_all_connections(self) -> dict:
        """
        Verify connections to all platforms.

        Returns:
            Verification results for each platform
        """
        results = {}

        if self.facebook:
            results['facebook'] = self.facebook.verify_token()
        else:
            results['facebook'] = {'valid': False, 'error': 'Client not available'}

        if self.instagram:
            results['instagram'] = self.instagram.verify_account()
        else:
            results['instagram'] = {'verified': False, 'error': 'Client not available'}

        if self.twitter:
            results['twitter'] = self.twitter.verify_credentials()
        else:
            results['twitter'] = {'verified': False, 'error': 'Client not available'}

        return results

    def create_approval_request(self, platform: str, content: str,
                                vault_path: str) -> Path:
        """
        Create approval request file for social media post.

        Args:
            platform: Platform name
            content: Post content
            vault_path: Path to Obsidian vault

        Returns:
            Path to approval file
        """
        vault = Path(vault_path)
        pending = vault / 'Pending_Approval'
        pending.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"SOCIAL_APPROVAL_{platform.upper()}_{timestamp}.md"
        filepath = pending / filename

        content_md = f'''---
type: approval_request
action: social_media_post
platform: {platform}
created: {datetime.now().isoformat()}
status: pending
---

# Social Media Post Approval Request

## Platform
{platform.title()}

## Content
```
{content}
```

## To Approve
Move this file to /Approved/ folder.

## To Reject
Move this file to /Rejected/ folder.

---
*Created by Social Media MCP - AI Employee v0.3*
'''

        filepath.write_text(content_md, encoding='utf-8')
        self.logger.info(f'Approval request created: {filepath.name}')
        return filepath


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Social Media MCP Server')
    parser.add_argument('action', choices=[
        'verify', 'post', 'notifications', 'insights', 'posts', 'demo'
    ], help='Action to perform')
    parser.add_argument('--platform', choices=['facebook', 'instagram', 'twitter'],
                        help='Platform name')
    parser.add_argument('--content', help='Post content')
    parser.add_argument('--media-url', help='Media URL for post')
    parser.add_argument('--limit', type=int, default=10, help='Result limit')
    parser.add_argument('--vault', default='../AI_Employee_Vault', help='Vault path')
    parser.add_argument('--demo', action='store_true', help='Demo mode')

    args = parser.parse_args()

    mcp = SocialMediaMCP()

    if args.demo or args.action == 'demo':
        print('Social Media MCP - Demo Mode')
        print('=' * 60)
        print()
        print('Supported Platforms:')
        print('  - Facebook (Graph API)')
        print('  - Instagram (Graph API)')
        print('  - Twitter/X (API v2)')
        print()

        # Verify connections
        print('Connection Status:')
        results = mcp.verify_all_connections()
        for platform, result in results.items():
            status = '✓' if (result.get('valid') or result.get('verified')) else '✗'
            name = result.get('username') or result.get('name') or 'Not configured'
            print(f'  {status} {platform.title()}: {name}')
        print()

        print('Available Actions:')
        print('  verify   - Check all platform connections')
        print('  post     - Post to platform')
        print('  posts    - Get recent posts')
        print('  notifications - Get notifications/mentions')
        print('  insights - Get platform analytics')
        print()
        print('Example Commands:')
        print('  python scripts/social_media_mcp.py post --platform twitter --content "Hello World"')
        print('  python scripts/social_media_mcp.py posts --platform facebook --limit 5')
        print('  python scripts/social_media_mcp.py insights --platform instagram')
        return

    if args.action == 'verify':
        results = mcp.verify_all_connections()
        print('Platform Connections:')
        print(json.dumps(results, indent=2))

    elif args.action == 'post':
        if not args.platform:
            print('Error: --platform required')
            sys.exit(1)
        if not args.content:
            print('Error: --content required')
            sys.exit(1)

        result = mcp.post_to_platform(
            args.platform,
            args.content,
            media_url=args.media_url
        )
        print(f'Post Result: {json.dumps(result, indent=2)}')

    elif args.action == 'posts':
        if not args.platform:
            print('Error: --platform required')
            sys.exit(1)

        posts = mcp.get_recent_posts(args.platform, args.limit)
        print(f'{args.platform.title()} Posts ({len(posts)}):')
        for post in posts[:5]:
            text = post.get('message') or post.get('caption') or post.get('text', 'N/A')
            print(f'  - {text[:80]}...')

    elif args.action == 'notifications':
        if not args.platform:
            print('Error: --platform required')
            sys.exit(1)

        notifications = mcp.get_notifications(args.platform, args.limit)
        print(f'{args.platform.title()} Notifications ({len(notifications)}):')
        for notif in notifications[:5]:
            msg = notif.get('message') or notif.get('text', 'N/A')
            print(f'  - {msg[:80]}...')

    elif args.action == 'insights':
        if not args.platform:
            print('Error: --platform required')
            sys.exit(1)

        insights = mcp.get_insights(args.platform)
        print(f'{args.platform.title()} Insights:')
        print(json.dumps(insights, indent=2))


if __name__ == '__main__':
    main()
