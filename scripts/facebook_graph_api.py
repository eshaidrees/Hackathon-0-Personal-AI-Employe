"""
Facebook Graph API Integration - Official Meta API
Handles Facebook page management, posts, and notifications via Graph API
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


class FacebookGraphAPI:
    """
    Facebook Graph API Client for business operations.
    Uses official Meta Graph API v19.0+
    
    Setup Instructions:
    1. Go to https://developers.facebook.com/apps/
    2. Create a new app (Business type)
    3. Add Facebook Login product
    4. Get App ID and App Secret
    5. Generate Page Access Token
    """

    def __init__(self, app_id: str = None, app_secret: str = None,
                 page_access_token: str = None, page_id: str = None,
                 api_version: str = 'v19.0'):
        """
        Initialize Facebook Graph API client.

        Args:
            app_id: Facebook App ID from developers.facebook.com
            app_secret: Facebook App Secret
            page_access_token: Page Access Token with required permissions
            page_id: Facebook Page ID to manage
            api_version: Graph API version (default: v19.0)
        """
        self.app_id = app_id or os.getenv('META_APP_ID', '')
        self.app_secret = app_secret or os.getenv('META_APP_SECRET', '')
        self.page_access_token = page_access_token or os.getenv('META_PAGE_ACCESS_TOKEN', '')
        self.page_id = page_id or os.getenv('FACEBOOK_PAGE_ID', '')
        self.api_version = api_version
        self.base_url = f'https://graph.facebook.com/{api_version}'

        import logging
        self.logger = logging.getLogger(self.__class__.__name__)

        # Permissions needed:
        # - pages_manage_posts
        # - pages_read_engagement
        # - pages_read_user_content
        # - pages_manage_metadata

    def _make_request(self, endpoint: str, method: str = 'GET',
                      params: dict = None, data: dict = None) -> dict:
        """
        Make Graph API request.

        Args:
            endpoint: API endpoint (e.g., '/me/posts')
            method: HTTP method
            params: URL parameters
            data: Request body data

        Returns:
            API response as dict
        """
        url = f'{self.base_url}{endpoint}'

        # Add access token to params
        if params is None:
            params = {}
        params['access_token'] = self.page_access_token

        try:
            if method == 'GET':
                response = requests.get(url, params=params, timeout=30)
            elif method == 'POST':
                # For Facebook, send as form data not JSON
                response = requests.post(url, data=params, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, params=params, timeout=30)
            else:
                raise ValueError(f'Unsupported method: {method}')

            response.raise_for_status()
            result = response.json()

            # Check for API errors
            if 'error' in result:
                self.logger.error(f'Graph API Error: {result["error"]}')
                return None

            return result

        except requests.exceptions.RequestException as e:
            self.logger.error(f'HTTP Error: {e}')
            return None

    def get_page_info(self) -> dict:
        """
        Get Facebook Page information.

        Returns:
            Page info dict with name, followers, etc.
        """
        if not self.page_access_token:
            self.logger.error('Page access token not configured')
            return None

        result = self._make_request(f'/{self.page_id}', params={
            'fields': 'id,name,username,followers_count,likes,about,website'
        })

        return result

    def create_post(self, message: str, link: str = None,
                    photo_url: str = None, scheduled_time: str = None,
                    published: bool = True) -> dict:
        """
        Create a post on Facebook Page.

        Args:
            message: Post message text
            link: Optional link to share
            photo_url: Optional photo URL to attach
            scheduled_time: Optional ISO 8601 datetime for scheduling
            published: True for immediate publish, False for draft

        Returns:
            Post creation result with post_id
        """
        if not self.page_access_token:
            self.logger.error('Page access token not configured')
            return {'error': 'Page access token not configured'}

        # Use params for Facebook API (access_token added automatically by _make_request)
        params = {
            'message': message
        }

        if link:
            params['link'] = link

        if photo_url:
            params['attached_media'] = json.dumps([{'media_url': photo_url}])

        if scheduled_time:
            params['scheduled_publish_time'] = scheduled_time

        # Make POST request - use data= for POST body
        result = self._make_request(f'/{self.page_id}/feed', method='POST', params=params)

        if result and 'id' in result:
            self.logger.info(f'Post created: {result["id"]}')
            return {
                'success': True,
                'post_id': result['id'],
                'permalink_url': f'https://facebook.com/{result["id"]}'
            }

        return {'success': False, 'error': 'Failed to create post'}

    def create_photo_post(self, photo_url: str, message: str = None,
                          published: bool = True) -> dict:
        """
        Create a photo post on Facebook Page.

        Args:
            photo_url: URL of the photo to post
            message: Optional caption text
            published: True for immediate publish

        Returns:
            Post creation result
        """
        data = {
            'url': photo_url
        }

        if message:
            data['message'] = message

        result = self._make_request(f'/{self.page_id}/photos', method='POST', data=data)

        if result and 'id' in result:
            self.logger.info(f'Photo post created: {result["id"]}')
            return {
                'success': True,
                'post_id': result['id'],
                'permalink_url': f'https://facebook.com/{result["id"]}'
            }

        return {'success': False, 'error': 'Failed to create photo post'}

    def get_posts(self, limit: int = 10, since: str = None,
                  until: str = None) -> list:
        """
        Get recent posts from Facebook Page.

        Args:
            limit: Maximum number of posts to retrieve
            since: ISO 8601 date for earliest post
            until: ISO 8601 date for latest post

        Returns:
            List of posts
        """
        params = {
            'fields': 'id,message,created_time,updated_time,permalink_url,shares,reactions.summary(true),comments.summary(true)',
            'limit': limit
        }

        if since:
            params['since'] = since

        if until:
            params['until'] = until

        result = self._make_request(f'/{self.page_id}/feed', params=params)

        return result.get('data', []) if result else []

    def get_insights(self, metrics: list = None,
                     period: str = 'day') -> dict:
        """
        Get Facebook Page insights/analytics.

        Args:
            metrics: List of metrics to retrieve
            period: Time period (day, week, month, lifetime)

        Returns:
            Insights data dict
        """
        if metrics is None:
            metrics = [
                'page_impressions',
                'page_reach',
                'page_engaged_users',
                'page_post_engagements',
                'page_likes',
                'page_follows'
            ]

        params = {
            'metric': ','.join(metrics),
            'period': period
        }

        result = self._make_request(f'/{self.page_id}/insights', params=params)

        return result.get('data', []) if result else []

    def get_notifications(self, limit: int = 25) -> list:
        """
        Get recent notifications for the page.

        Args:
            limit: Maximum notifications to retrieve

        Returns:
            List of notifications
        """
        params = {
            'fields': 'id,from,message,created_time,type,unread',
            'limit': limit
        }

        result = self._make_request(f'/{self.page_id}/notifications', params=params)

        return result.get('data', []) if result else []

    def get_comments(self, post_id: str, limit: int = 50) -> list:
        """
        Get comments on a post.

        Args:
            post_id: Facebook post ID
            limit: Maximum comments to retrieve

        Returns:
            List of comments
        """
        params = {
            'fields': 'id,from,message,created_time,like_count,comment_count',
            'limit': limit,
            'order': 'chronological'
        }

        result = self._make_request(f'/{post_id}/comments', params=params)

        return result.get('data', []) if result else []

    def reply_to_comment(self, comment_id: str, message: str) -> dict:
        """
        Reply to a comment on a post.

        Args:
            comment_id: Facebook comment ID
            message: Reply message

        Returns:
            Reply creation result
        """
        data = {
            'message': message,
            'comment_id': comment_id
        }

        result = self._make_request('/me/conversations', method='POST', data=data)

        if result and 'id' in result:
            self.logger.info(f'Reply created: {result["id"]}')
            return {'success': True, 'comment_id': result['id']}

        return {'success': False, 'error': 'Failed to reply to comment'}

    def delete_post(self, post_id: str) -> dict:
        """
        Delete a post from Facebook Page.

        Args:
            post_id: Facebook post ID to delete

        Returns:
            Deletion result
        """
        result = self._make_request(f'/{post_id}', method='DELETE')

        if result is True or (result and result.get('success')):
            self.logger.info(f'Post deleted: {post_id}')
            return {'success': True}

        return {'success': False, 'error': 'Failed to delete post'}

    def get_long_lived_token(self, short_lived_token: str = None) -> dict:
        """
        Exchange short-lived token for long-lived token (60 days).

        Args:
            short_lived_token: Short-lived user token (from login)

        Returns:
            Token exchange result with long-lived token
        """
        token = short_lived_token or self.page_access_token

        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'fb_exchange_token': token
        }

        result = self._make_request('/oauth/access_token', params=params)

        if result and 'access_token' in result:
            self.logger.info('Long-lived token obtained')
            return {
                'success': True,
                'access_token': result['access_token'],
                'expires_in': result.get('expires_in', 5184000)  # 60 days
            }

        return {'success': False, 'error': 'Failed to exchange token'}

    def verify_token(self) -> dict:
        """
        Verify the current access token.

        Returns:
            Token info dict
        """
        result = self._make_request('/me', params={
            'fields': 'id,name'
        })

        if result and 'id' in result:
            return {
                'valid': True,
                'app_id': self.app_id,
                'user_id': result['id'],
                'name': result['name']
            }

        return {'valid': False, 'error': 'Token verification failed'}


def main():
    """CLI entry point for testing."""
    import argparse

    parser = argparse.ArgumentParser(description='Facebook Graph API Client')
    parser.add_argument('action', choices=[
        'info', 'post', 'photo', 'posts', 'insights',
        'notifications', 'verify', 'token', 'demo'
    ], help='Action to perform')
    parser.add_argument('--message', help='Post message')
    parser.add_argument('--link', help='Link to share')
    parser.add_argument('--app-id', help='Facebook App ID')
    parser.add_argument('--app-secret', help='Facebook App Secret')
    parser.add_argument('--token', help='Page Access Token')
    parser.add_argument('--page-id', help='Facebook Page ID')
    parser.add_argument('--photo-url', help='Photo URL for photo post')
    parser.add_argument('--post-id', help='Post ID for operations')
    parser.add_argument('--limit', type=int, default=10, help='Result limit')
    parser.add_argument('--demo', action='store_true', help='Demo mode')

    args = parser.parse_args()

    # Override env vars if provided
    if args.app_id:
        os.environ['META_APP_ID'] = args.app_id
    if args.app_secret:
        os.environ['META_APP_SECRET'] = args.app_secret
    if args.token:
        os.environ['META_PAGE_ACCESS_TOKEN'] = args.token
    if args.page_id:
        os.environ['FACEBOOK_PAGE_ID'] = args.page_id

    fb = FacebookGraphAPI()

    if args.demo or args.action == 'demo':
        print('Facebook Graph API - Demo Mode')
        print('=' * 50)
        print(f'App ID: {fb.app_id[:8]}...' if fb.app_id else 'App ID: Not configured')
        print(f'Page ID: {fb.page_id}' if fb.page_id else 'Page ID: Not configured')
        print(f'Token configured: {"Yes" if fb.page_access_token else "No"}')
        print()

        # Test token verification
        print('1. Testing token verification...')
        token_info = fb.verify_token()
        if token_info.get('valid'):
            print(f'   ✓ Token valid for: {token_info.get("name")}')
        else:
            print('   ✗ Token not configured or invalid')
            print('   Setup: Configure META_PAGE_ACCESS_TOKEN in .env')

        print()
        print('2. Available Actions:')
        print('   - info: Get page information')
        print('   - post: Create text post')
        print('   - photo: Create photo post')
        print('   - posts: Get recent posts')
        print('   - insights: Get page insights')
        print('   - notifications: Get notifications')
        print()
        print('Setup Instructions:')
        print('1. Go to https://developers.facebook.com/apps/')
        print('2. Create a Business app')
        print('3. Add Facebook Login product')
        print('4. Get App ID and App Secret')
        print('5. Generate Page Access Token with permissions:')
        print('   - pages_manage_posts')
        print('   - pages_read_engagement')
        print('   - pages_read_user_content')
        print('6. Add to .env file')
        return

    if args.action == 'verify':
        result = fb.verify_token()
        print(f'Token Valid: {result.get("valid")}')
        print(json.dumps(result, indent=2))

    elif args.action == 'info':
        info = fb.get_page_info()
        if info:
            print(f'Page: {info.get("name")}')
            print(f'Followers: {info.get("followers_count", "N/A")}')
            print(f'Likes: {info.get("likes", "N/A")}')
            print(f'Website: {info.get("website", "N/A")}')
        else:
            print('Failed to get page info')

    elif args.action == 'post':
        if not args.message:
            print('Error: --message required')
            sys.exit(1)
        result = fb.create_post(args.message, link=args.link)
        print(f'Post Result: {json.dumps(result, indent=2)}')

    elif args.action == 'photo':
        if not args.photo_url:
            print('Error: --photo-url required')
            sys.exit(1)
        result = fb.create_photo_post(args.photo_url, message=args.message)
        print(f'Photo Post Result: {json.dumps(result, indent=2)}')

    elif args.action == 'posts':
        posts = fb.get_posts(limit=args.limit)
        print(f'Recent Posts ({len(posts)}):')
        for post in posts[:5]:
            print(f'  - {post.get("created_time", "N/A")}: {post.get("message", "(no text)")[:50]}...')

    elif args.action == 'insights':
        insights = fb.get_insights()
        print('Page Insights:')
        for metric in insights:
            if metric.get('values'):
                print(f'  {metric["name"]}: {metric["values"][0].get("value", "N/A")}')

    elif args.action == 'notifications':
        notifications = fb.get_notifications(limit=args.limit)
        print(f'Recent Notifications ({len(notifications)}):')
        for notif in notifications[:10]:
            print(f'  - {notif.get("created_time", "N/A")}: {notif.get("message", "(no message)")[:50]}...')


if __name__ == '__main__':
    main()
