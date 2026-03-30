"""
Instagram Graph API Integration - Official Meta API
Handles Instagram Business account management, posts, and insights via Graph API
More reliable and ToS-compliant than browser automation
"""
import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class InstagramGraphAPI:
    """
    Instagram Graph API Client for Business accounts.
    Uses official Meta Graph API v19.0+
    
    Requirements:
    - Instagram Business Account (not personal or creator)
    - Facebook Page linked to Instagram Business account
    - Facebook App with Instagram Graph API product
    
    Setup Instructions:
    1. Convert Instagram to Business Account (in Instagram app)
    2. Link Instagram to Facebook Page
    3. Go to https://developers.facebook.com/apps/
    4. Create/Select app and add Instagram Graph API product
    5. Get App ID and App Secret
    6. Generate Page Access Token with Instagram permissions
    """

    def __init__(self, app_id: str = None, app_secret: str = None,
                 page_access_token: str = None, page_id: str = None,
                 instagram_account_id: str = None,
                 api_version: str = 'v19.0'):
        """
        Initialize Instagram Graph API client.

        Args:
            app_id: Facebook App ID from developers.facebook.com
            app_secret: Facebook App Secret
            page_access_token: Page Access Token with Instagram permissions
            page_id: Facebook Page ID linked to Instagram
            instagram_account_id: Instagram Business Account ID
            api_version: Graph API version (default: v19.0)
        """
        self.app_id = app_id or os.getenv('META_APP_ID', '')
        self.app_secret = app_secret or os.getenv('META_APP_SECRET', '')
        self.page_access_token = page_access_token or os.getenv('META_PAGE_ACCESS_TOKEN', '')
        self.page_id = page_id or os.getenv('FACEBOOK_PAGE_ID', '')
        self.instagram_account_id = instagram_account_id or os.getenv('INSTAGRAM_ACCOUNT_ID', '')
        self.api_version = api_version
        self.base_url = f'https://graph.facebook.com/{api_version}'

        import logging
        self.logger = logging.getLogger(self.__class__.__name__)

        # Required permissions:
        # - instagram_basic
        # - instagram_content_publish
        # - instagram_manage_comments
        # - instagram_manage_insights
        # - pages_read_engagement

    def _make_request(self, endpoint: str, method: str = 'GET',
                      params: dict = None, data: dict = None) -> dict:
        """
        Make Graph API request.

        Args:
            endpoint: API endpoint
            method: HTTP method
            params: URL parameters
            data: Request body data

        Returns:
            API response as dict
        """
        url = f'{self.base_url}{endpoint}'

        if params is None:
            params = {}
        params['access_token'] = self.page_access_token

        try:
            if method == 'GET':
                response = requests.get(url, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, params=params, json=data, timeout=30)
            else:
                raise ValueError(f'Unsupported method: {method}')

            response.raise_for_status()
            result = response.json()

            if 'error' in result:
                self.logger.error(f'Graph API Error: {result["error"]}')
                return None

            return result

        except requests.exceptions.RequestException as e:
            self.logger.error(f'HTTP Error: {e}')
            return None

    def get_account_info(self) -> dict:
        """
        Get Instagram Business Account information.

        Returns:
            Account info dict
        """
        if not self.instagram_account_id:
            # Try to discover account from connected page
            self.instagram_account_id = self._discover_account()
            if not self.instagram_account_id:
                self.logger.error('Instagram account ID not configured')
                return None

        result = self._make_request(f'/{self.instagram_account_id}', params={
            'fields': 'id,username,name,biography,website,followers_count,follows_count,media_count,profile_picture_url'
        })

        return result

    def _discover_account(self) -> str:
        """Discover Instagram Business Account ID from connected Facebook Page."""
        result = self._make_request(f'/{self.page_id}', params={
            'fields': 'instagram_business_account'
        })

        if result and 'instagram_business_account' in result:
            account_id = result['instagram_business_account'].get('id')
            self.logger.info(f'Discovered Instagram Account: {account_id}')
            return account_id

        return None

    def create_photo_post(self, image_url: str, caption: str = None,
                          is_carousel: bool = False) -> dict:
        """
        Create a photo post on Instagram.

        Args:
            image_url: Public URL of the image to post
            caption: Post caption text
            is_carousel: True if part of carousel album

        Returns:
            Container creation result
        """
        if not self.instagram_account_id:
            self.instagram_account_id = self._discover_account()

        # Step 1: Create media container
        data = {
            'image_url': image_url,
            'caption': caption or '',
            'is_carousel_item': is_carousel
        }

        result = self._make_request(
            f'/{self.instagram_account_id}/media',
            method='POST',
            data=data
        )

        if result and 'id' in result:
            container_id = result['id']
            self.logger.info(f'Container created: {container_id}')

            # Step 2: Publish the container
            publish_result = self._publish_media(container_id)
            return publish_result

        return {'success': False, 'error': 'Failed to create container'}

    def create_video_post(self, video_url: str, caption: str = None,
                          thumbnail_url: str = None) -> dict:
        """
        Create a video post on Instagram.

        Args:
            video_url: Public URL of the video to post
            caption: Post caption text
            thumbnail_url: Optional thumbnail URL

        Returns:
            Post creation result
        """
        if not self.instagram_account_id:
            self.instagram_account_id = self._discover_account()

        # Step 1: Create video container
        data = {
            'video_url': video_url,
            'caption': caption or ''
        }

        if thumbnail_url:
            data['thumbnail_url'] = thumbnail_url

        result = self._make_request(
            f'/{self.instagram_account_id}/media',
            method='POST',
            data=data
        )

        if result and 'id' in result:
            container_id = result['id']
            self.logger.info(f'Video container created: {container_id}')

            # Step 2: Publish
            return self._publish_media(container_id)

        return {'success': False, 'error': 'Failed to create video container'}

    def create_carousel_post(self, media_urls: list, caption: str = None) -> dict:
        """
        Create a carousel post (multiple images/videos).

        Args:
            media_urls: List of image/video URLs (2-10 items)
            caption: Post caption text

        Returns:
            Post creation result
        """
        if not self.instagram_account_id:
            self.instagram_account_id = self._discover_account()

        if len(media_urls) < 2 or len(media_urls) > 10:
            return {'success': False, 'error': 'Carousel requires 2-10 media items'}

        # Step 1: Create child containers for each media
        children_ids = []
        for url in media_urls:
            is_video = url.endswith('.mp4') or 'video' in url.lower()

            data = {
                'is_carousel_item': True
            }

            if is_video:
                data['video_url'] = url
            else:
                data['image_url'] = url

            result = self._make_request(
                f'/{self.instagram_account_id}/media',
                method='POST',
                data=data
            )

            if result and 'id' in result:
                children_ids.append(result['id'])
            else:
                return {'success': False, 'error': f'Failed to create container for {url}'}

        # Step 2: Create carousel container with children
        carousel_data = {
            'media_type': 'CAROUSEL',
            'children': ','.join(children_ids),
            'caption': caption or ''
        }

        result = self._make_request(
            f'/{self.instagram_account_id}/media',
            method='POST',
            data=carousel_data
        )

        if result and 'id' in result:
            return self._publish_media(result['id'])

        return {'success': False, 'error': 'Failed to create carousel'}

    def _publish_media(self, container_id: str) -> dict:
        """
        Publish a media container.

        Args:
            container_id: Media container ID from creation step

        Returns:
            Publication result
        """
        publish_result = self._make_request(
            f'/{self.instagram_account_id}/media_publish',
            method='POST',
            data={'creation_id': container_id}
        )

        if publish_result and 'id' in publish_result:
            post_id = publish_result['id']
            self.logger.info(f'Post published: {post_id}')
            return {
                'success': True,
                'post_id': post_id,
                'permalink_url': f'https://instagram.com/p/{post_id}'
            }

        return {'success': False, 'error': 'Failed to publish media'}

    def get_posts(self, limit: int = 10) -> list:
        """
        Get recent media posts from Instagram.

        Args:
            limit: Maximum posts to retrieve

        Returns:
            List of posts
        """
        if not self.instagram_account_id:
            self.instagram_account_id = self._discover_account()

        result = self._make_request(f'/{self.instagram_account_id}/media', params={
            'fields': 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count',
            'limit': limit
        })

        return result.get('data', []) if result else []

    def get_insights(self, metrics: list = None,
                     period: str = 'day') -> dict:
        """
        Get Instagram account insights/analytics.

        Args:
            metrics: List of metrics to retrieve
            period: Time period (day, week, month, lifetime)

        Returns:
            Insights data
        """
        if metrics is None:
            metrics = [
                'impressions',
                'reach',
                'profile_views',
                'follower_count',
                'email_contacts',
                'phone_call_clicks',
                'text_message_clicks',
                'get_directions_clicks',
                'website_clicks'
            ]

        if not self.instagram_account_id:
            self.instagram_account_id = self._discover_account()

        result = self._make_request(f'/{self.instagram_account_id}/insights', params={
            'metric': ','.join(metrics),
            'period': period
        })

        return result.get('data', []) if result else []

    def get_post_insights(self, post_id: str,
                          metrics: list = None) -> dict:
        """
        Get insights for a specific post.

        Args:
            post_id: Instagram post ID
            metrics: Metrics to retrieve

        Returns:
            Post insights data
        """
        if metrics is None:
            metrics = ['impressions', 'reach', 'saved', 'likes', 'comments', 'engagement']

        result = self._make_request(f'/{post_id}/insights', params={
            'metric': ','.join(metrics)
        })

        return result.get('data', []) if result else []

    def get_comments(self, post_id: str, limit: int = 50) -> list:
        """
        Get comments on a post.

        Args:
            post_id: Instagram post ID
            limit: Maximum comments

        Returns:
            List of comments
        """
        result = self._make_request(f'/{post_id}/comments', params={
            'fields': 'id,from,text,timestamp,like_count',
            'limit': limit
        })

        return result.get('data', []) if result else []

    def reply_to_comment(self, comment_id: str, message: str) -> dict:
        """
        Reply to a comment on a post.

        Args:
            comment_id: Instagram comment ID
            message: Reply message

        Returns:
            Reply creation result
        """
        data = {'message': message}

        result = self._make_request(
            f'/{comment_id}/comments',
            method='POST',
            data=data
        )

        if result and 'id' in result:
            self.logger.info(f'Reply created: {result["id"]}')
            return {'success': True, 'comment_id': result['id']}

        return {'success': False, 'error': 'Failed to reply'}

    def hide_comment(self, comment_id: str) -> dict:
        """
        Hide a comment (spam/inappropriate).

        Args:
            comment_id: Comment ID to hide

        Returns:
            Hide result
        """
        result = self._make_request(
            f'/{comment_id}/hide',
            method='POST',
            data={'hide': True}
        )

        if result is True or (result and result.get('success')):
            self.logger.info(f'Comment hidden: {comment_id}')
            return {'success': True}

        return {'success': False, 'error': 'Failed to hide comment'}

    def get_stories(self) -> list:
        """
        Get active stories.

        Returns:
            List of stories
        """
        if not self.instagram_account_id:
            self.instagram_account_id = self._discover_account()

        result = self._make_request(f'/{self.instagram_account_id}/stories', params={
            'fields': 'id,media_type,media_url,permalink,timestamp,expiring_at'
        })

        return result.get('data', []) if result else []

    def verify_account(self) -> dict:
        """
        Verify the Instagram Business account connection.

        Returns:
            Verification result
        """
        info = self.get_account_info()

        if info and 'id' in info:
            return {
                'verified': True,
                'account_id': info['id'],
                'username': info.get('username', 'N/A'),
                'name': info.get('name', 'N/A'),
                'followers': info.get('followers_count', 'N/A')
            }

        return {'verified': False, 'error': 'Account verification failed'}


def main():
    """CLI entry point for testing."""
    import argparse

    parser = argparse.ArgumentParser(description='Instagram Graph API Client')
    parser.add_argument('action', choices=[
        'info', 'photo', 'video', 'carousel', 'posts',
        'insights', 'verify', 'demo'
    ], help='Action to perform')
    parser.add_argument('--caption', help='Post caption')
    parser.add_argument('--image-url', help='Image URL for photo post')
    parser.add_argument('--video-url', help='Video URL for video post')
    parser.add_argument('--media-urls', nargs='+', help='Media URLs for carousel')
    parser.add_argument('--post-id', help='Post ID for operations')
    parser.add_argument('--limit', type=int, default=10, help='Result limit')
    parser.add_argument('--account-id', help='Instagram Account ID')
    parser.add_argument('--demo', action='store_true', help='Demo mode')

    args = parser.parse_args()

    if args.account_id:
        os.environ['INSTAGRAM_ACCOUNT_ID'] = args.account_id

    ig = InstagramGraphAPI()

    if args.demo or args.action == 'demo':
        print('Instagram Graph API - Demo Mode')
        print('=' * 50)
        print(f'App ID: {ig.app_id[:8]}...' if ig.app_id else 'App ID: Not configured')
        print(f'Page ID: {ig.page_id}' if ig.page_id else 'Page ID: Not configured')
        print(f'IG Account ID: {ig.instagram_account_id}' if ig.instagram_account_id else 'IG Account ID: Not configured')
        print(f'Token configured: {"Yes" if ig.page_access_token else "No"}')
        print()

        # Test verification
        print('1. Testing account verification...')
        if ig.page_access_token:
            result = ig.verify_account()
            if result.get('verified'):
                print(f'   ✓ Connected to: @{result.get("username")}')
                print(f'   Followers: {result.get("followers")}')
            else:
                print('   ✗ Account not connected or invalid token')
        else:
            print('   ✗ Token not configured')

        print()
        print('2. Available Actions:')
        print('   - info: Get account information')
        print('   - photo: Create photo post')
        print('   - video: Create video post')
        print('   - carousel: Create carousel post (2-10 images)')
        print('   - posts: Get recent posts')
        print('   - insights: Get account insights')
        print()
        print('Setup Instructions:')
        print('1. Convert Instagram to Business Account')
        print('2. Link to Facebook Page')
        print('3. Go to https://developers.facebook.com/apps/')
        print('4. Add Instagram Graph API product')
        print('5. Get Page Access Token with permissions:')
        print('   - instagram_basic')
        print('   - instagram_content_publish')
        print('   - instagram_manage_insights')
        print('6. Add INSTAGRAM_ACCOUNT_ID to .env')
        return

    if args.action == 'verify':
        result = ig.verify_account()
        print(f'Verified: {result.get("verified")}')
        print(json.dumps(result, indent=2))

    elif args.action == 'info':
        info = ig.get_account_info()
        if info:
            print(f'Username: @{info.get("username")}')
            print(f'Name: {info.get("name")}')
            print(f'Followers: {info.get("followers_count")}')
            print(f'Following: {info.get("follows_count")}')
            print(f'Posts: {info.get("media_count")}')
            print(f'Bio: {info.get("biography")}')
            print(f'Website: {info.get("website")}')
        else:
            print('Failed to get account info')

    elif args.action == 'photo':
        if not args.image_url:
            print('Error: --image-url required')
            sys.exit(1)
        result = ig.create_photo_post(args.image_url, caption=args.caption)
        print(f'Photo Post Result: {json.dumps(result, indent=2)}')

    elif args.action == 'video':
        if not args.video_url:
            print('Error: --video-url required')
            sys.exit(1)
        result = ig.create_video_post(args.video_url, caption=args.caption)
        print(f'Video Post Result: {json.dumps(result, indent=2)}')

    elif args.action == 'carousel':
        if not args.media_urls or len(args.media_urls) < 2:
            print('Error: --media-urls requires 2-10 URLs')
            sys.exit(1)
        result = ig.create_carousel_post(args.media_urls, caption=args.caption)
        print(f'Carousel Result: {json.dumps(result, indent=2)}')

    elif args.action == 'posts':
        posts = ig.get_posts(limit=args.limit)
        print(f'Recent Posts ({len(posts)}):')
        for post in posts[:5]:
            print(f'  - {post.get("timestamp", "N/A")}: {post.get("caption", "(no caption)")[:50]}...')
            print(f'    Type: {post.get("media_type")}, Likes: {post.get("like_count", "N/A")}')

    elif args.action == 'insights':
        insights = ig.get_insights()
        print('Account Insights:')
        for metric in insights:
            if metric.get('values'):
                print(f'  {metric["name"]}: {metric["values"][0].get("value", "N/A")}')


if __name__ == '__main__':
    main()
