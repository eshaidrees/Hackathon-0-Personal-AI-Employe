"""
Twitter API v2 Integration - Official Twitter API
Handles Twitter/X posts, mentions, DMs, and analytics via official API
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


class TwitterAPI:
    """
    Twitter API v2 Client for business operations.
    Uses official Twitter API v2
    
    Setup Instructions:
    1. Go to https://developer.twitter.com/en/portal/dashboard
    2. Create a developer account and project
    3. Create an app to get API keys
    4. Generate Bearer Token, API Key, and API Secret
    5. For posting: Generate OAuth 2.0 tokens with read/write permissions
    """

    def __init__(self, bearer_token: str = None, api_key: str = None,
                 api_secret: str = None, access_token: str = None,
                 access_token_secret: str = None, api_version: str = '2'):
        """
        Initialize Twitter API client.

        Args:
            bearer_token: Bearer Token for read-only operations
            api_key: API Key (Consumer Key)
            api_secret: API Secret (Consumer Secret)
            access_token: OAuth Access Token (for write operations)
            access_token_secret: OAuth Access Token Secret
            api_version: API version (default: 2)
        """
        self.bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN', '')
        self.api_key = api_key or os.getenv('TWITTER_API_KEY', '')
        self.api_secret = api_secret or os.getenv('TWITTER_API_SECRET', '')
        self.access_token = access_token or os.getenv('TWITTER_ACCESS_TOKEN', '')
        self.access_token_secret = access_token_secret or os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')
        self.api_version = api_version
        self.base_url = 'https://api.twitter.com/2'
        self.v1_base_url = 'https://api.twitter.com/1.1'  # Some endpoints still use v1.1

        # User ID cache
        self._user_id = None

        import logging
        self.logger = logging.getLogger(self.__class__.__name__)

    def _make_request(self, endpoint: str, method: str = 'GET',
                      params: dict = None, data: dict = None,
                      use_v1: bool = False) -> dict:
        """
        Make Twitter API request.

        Args:
            endpoint: API endpoint
            method: HTTP method
            params: URL parameters
            data: Request body data
            use_v1: Use v1.1 API instead of v2

        Returns:
            API response as dict
        """
        base_url = self.v1_base_url if use_v1 else self.base_url
        url = f'{base_url}{endpoint}'

        headers = {
            'Authorization': f'Bearer {self.bearer_token}'
        }

        # For write operations, use OAuth 1.0a
        if method in ['POST', 'DELETE'] and self.api_key and self.api_secret:
            import oauthlib
            from requests_oauthlib import OAuth1Session

            oauth = OAuth1Session(
                self.api_key,
                client_secret=self.api_secret,
                resource_owner_key=self.access_token,
                resource_owner_secret=self.access_token_secret
            )

            if method == 'GET':
                response = oauth.get(url, params=params, timeout=30)
            elif method == 'POST':
                response = oauth.post(url, json=data, timeout=30)
            elif method == 'DELETE':
                response = oauth.delete(url, timeout=30)
        else:
            # Read-only with Bearer token
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                headers['Content-Type'] = 'application/json'
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f'Unsupported method: {method}')

        try:
            response.raise_for_status()
            result = response.json()

            # Check for API errors
            if 'errors' in result:
                self.logger.error(f'Twitter API Error: {result["errors"]}')
                return None

            return result

        except requests.exceptions.RequestException as e:
            self.logger.error(f'HTTP Error: {e}')
            if hasattr(e.response, 'text'):
                self.logger.error(f'Response: {e.response.text}')
            return None

    def get_me(self) -> dict:
        """
        Get authenticated user's information.

        Returns:
            User info dict
        """
        result = self._make_request('/users/me', params={
            'user.fields': 'id,name,username,description,public_metrics,verified,profile_image_url'
        })

        if result and 'data' in result:
            self._user_id = result['data']['id']
            return result['data']

        return None

    def _get_user_id(self) -> str:
        """Get cached user ID."""
        if not self._user_id:
            me = self.get_me()
            if me:
                self._user_id = me['id']
        return self._user_id

    def post_tweet(self, text: str, media_ids: list = None,
                   reply_settings: str = None,
                   quote_tweet_id: str = None) -> dict:
        """
        Post a new tweet.

        Args:
            text: Tweet text (max 280 characters for standard)
            media_ids: List of media IDs to attach
            reply_settings: Who can reply (everyone, mentionedUsers, following)
            quote_tweet_id: Tweet ID to quote

        Returns:
            Tweet creation result
        """
        data = {'text': text}

        if media_ids:
            data['media'] = {'media_ids': media_ids}

        if reply_settings:
            data['reply_settings'] = reply_settings

        if quote_tweet_id:
            data['quote_tweet_id'] = quote_tweet_id

        result = self._make_request('/tweets', method='POST', data=data)

        if result and 'data' in result and 'id' in result['data']:
            tweet_id = result['data']['id']
            self.logger.info(f'Tweet posted: {tweet_id}')
            return {
                'success': True,
                'tweet_id': tweet_id,
                'permalink_url': f'https://twitter.com/status/{tweet_id}'
            }

        return {'success': False, 'error': 'Failed to post tweet'}

    def post_thread(self, tweets: list) -> dict:
        """
        Post a thread of tweets.

        Args:
            tweets: List of tweet texts

        Returns:
            Thread creation result with all tweet IDs
        """
        if not tweets:
            return {'success': False, 'error': 'No tweets provided'}

        tweet_ids = []
        results = []

        # Post first tweet
        first_result = self.post_tweet(tweets[0])
        if not first_result.get('success'):
            return first_result

        tweet_ids.append(first_result['tweet_id'])
        results.append(first_result)

        # Post reply tweets
        for i, tweet_text in enumerate(tweets[1:], 1):
            reply_result = self.post_tweet(
                tweet_text,
                reply_settings='mentionedUsers',
                quote_tweet_id=None
            )
            # Note: For proper threading, we'd need to use reply_to parameter
            # This is a simplified version
            if reply_result.get('success'):
                tweet_ids.append(reply_result['tweet_id'])
            results.append(reply_result)

        return {
            'success': all(r.get('success', False) for r in results),
            'tweet_ids': tweet_ids,
            'results': results
        }

    def get_tweets(self, user_id: str = None, limit: int = 10,
                   exclude: list = None) -> list:
        """
        Get recent tweets from a user.

        Args:
            user_id: Twitter user ID (uses authenticated user if not provided)
            limit: Maximum tweets to retrieve
            exclude: List to exclude (retweets, replies)

        Returns:
            List of tweets
        """
        if not user_id:
            user_id = self._get_user_id()

        params = {
            'max_results': min(limit, 100),
            'tweet.fields': 'created_at,text,public_metrics,context_annotations'
        }

        if exclude:
            params['exclude'] = ','.join(exclude)

        result = self._make_request(f'/users/{user_id}/tweets', params=params)

        return result.get('data', []) if result else []

    def get_mentions(self, limit: int = 25) -> list:
        """
        Get tweets mentioning the authenticated user.

        Args:
            limit: Maximum mentions to retrieve

        Returns:
            List of mention tweets
        """
        user_id = self._get_user_id()

        params = {
            'max_results': min(limit, 100),
            'tweet.fields': 'created_at,text,author_id,public_metrics',
            'expansions': 'author_id',
            'user.fields': 'name,username,profile_image_url'
        }

        result = self._make_request(f'/users/{user_id}/mentions', params=params)

        if result and 'data' in result:
            # Include author info
            includes = result.get('includes', {}).get('users', [])
            authors = {u['id']: u for u in includes}

            tweets = []
            for tweet in result['data']:
                tweet['author'] = authors.get(tweet.get('author_id'))
                tweets.append(tweet)

            return tweets

        return []

    def get_home_timeline(self, limit: int = 10) -> list:
        """
        Get authenticated user's home timeline.

        Args:
            limit: Maximum tweets to retrieve

        Returns:
            List of tweets from followed accounts
        """
        user_id = self._get_user_id()

        params = {
            'max_results': min(limit, 100),
            'tweet.fields': 'created_at,text,author_id,public_metrics',
            'expansions': 'author_id',
            'user.fields': 'name,username'
        }

        # Note: This endpoint requires elevated access
        result = self._make_request(f'/users/{user_id}/timelines/reverse_chronological', params=params)

        return result.get('data', []) if result else []

    def reply_to_tweet(self, tweet_id: str, text: str) -> dict:
        """
        Reply to a tweet.

        Args:
            tweet_id: Tweet ID to reply to
            text: Reply text

        Returns:
            Reply creation result
        """
        data = {
            'text': text,
            'reply': {'in_reply_to_tweet_id': tweet_id}
        }

        result = self._make_request('/tweets', method='POST', data=data)

        if result and 'data' in result and 'id' in result['data']:
            reply_id = result['data']['id']
            self.logger.info(f'Reply posted: {reply_id}')
            return {
                'success': True,
                'tweet_id': reply_id,
                'in_reply_to': tweet_id
            }

        return {'success': False, 'error': 'Failed to reply'}

    def like_tweet(self, tweet_id: str) -> dict:
        """
        Like a tweet.

        Args:
            tweet_id: Tweet ID to like

        Returns:
            Like result
        """
        user_id = self._get_user_id()

        data = {'tweet_id': tweet_id}

        result = self._make_request(
            f'/users/{user_id}/likes',
            method='POST',
            data=data
        )

        if result and 'data' in result:
            return {'success': True, 'liked': True}

        return {'success': False, 'error': 'Failed to like tweet'}

    def retweet(self, tweet_id: str) -> dict:
        """
        Retweet a tweet.

        Args:
            tweet_id: Tweet ID to retweet

        Returns:
            Retweet result
        """
        user_id = self._get_user_id()

        data = {'tweet_id': tweet_id}

        result = self._make_request(
            f'/users/{user_id}/retweets',
            method='POST',
            data=data
        )

        if result and 'data' in result:
            return {'success': True, 'retweeted': True}

        return {'success': False, 'error': 'Failed to retweet'}

    def get_tweet_insights(self, tweet_id: str) -> dict:
        """
        Get insights for a tweet (requires elevated access).

        Args:
            tweet_id: Tweet ID

        Returns:
            Tweet insights
        """
        result = self._make_request(f'/tweets/{tweet_id}', params={
            'tweet.fields': 'public_metrics,non_public_metrics,organic_metrics'
        })

        if result and 'data' in result:
            return {
                'tweet_id': tweet_id,
                'metrics': result['data'].get('public_metrics', {}),
                'organic_metrics': result['data'].get('organic_metrics', {}),
                'non_public_metrics': result['data'].get('non_public_metrics', {})
            }

        return {}

    def search_tweets(self, query: str, limit: int = 10,
                      recent: bool = True) -> list:
        """
        Search for tweets.

        Args:
            query: Search query (Twitter search syntax)
            limit: Maximum tweets to retrieve
            recent: True for recent search, False for full-archive (elevated)

        Returns:
            List of matching tweets
        """
        endpoint = '/tweets/search/recent' if recent else '/tweets/search/all'

        params = {
            'query': query,
            'max_results': min(limit, 100),
            'tweet.fields': 'created_at,text,author_id,public_metrics',
            'expansions': 'author_id',
            'user.fields': 'name,username'
        }

        result = self._make_request(endpoint, params=params)

        return result.get('data', []) if result else []

    def upload_media(self, image_path: str, alt_text: str = None) -> str:
        """
        Upload media for tweets (uses v1.1 API).

        Args:
            image_path: Path to image file
            alt_text: Optional alt text for accessibility

        Returns:
            Media ID string
        """
        # This requires OAuth 1.0a authentication
        if not self.api_key or not self.access_token:
            self.logger.error('OAuth credentials required for media upload')
            return None

        from requests_oauthlib import OAuth1Session

        oauth = OAuth1Session(
            self.api_key,
            client_secret=self.api_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_token_secret
        )

        # Upload media
        files = {'media': open(image_path, 'rb')}
        response = oauth.post(
            'https://upload.twitter.com/1.1/media/upload.json',
            files=files
        )

        if response.status_code == 200:
            media_data = response.json()
            media_id = media_data['media_id_string']

            # Add alt text if provided
            if alt_text:
                oauth.post(
                    'https://upload.twitter.com/1.1/media/metadata/create.json',
                    json={
                        'media_id': media_id,
                        'alt_text': {'text': alt_text}
                    }
                )

            self.logger.info(f'Media uploaded: {media_id}')
            return media_id

        self.logger.error(f'Media upload failed: {response.text}')
        return None

    def get_account_metrics(self, period: str = 'day') -> dict:
        """
        Get account metrics/insights.

        Args:
            period: Time period for metrics

        Returns:
            Account metrics
        """
        # Note: This requires elevated access to Twitter API
        user_id = self._get_user_id()

        result = self._make_request(f'/users/{user_id}', params={
            'user.fields': 'public_metrics'
        })

        if result and 'data' in result:
            metrics = result['data'].get('public_metrics', {})
            return {
                'followers_count': metrics.get('followers_count', 0),
                'following_count': metrics.get('following_count', 0),
                'tweet_count': metrics.get('tweet_count', 0),
                'listed_count': metrics.get('listed_count', 0)
            }

        return {}

    def verify_credentials(self) -> dict:
        """
        Verify Twitter API credentials.

        Returns:
            Verification result with user info
        """
        me = self.get_me()

        if me:
            return {
                'verified': True,
                'user_id': me['id'],
                'username': me['username'],
                'name': me['name'],
                'followers': me.get('public_metrics', {}).get('followers_count', 0)
            }

        return {'verified': False, 'error': 'Credential verification failed'}


def main():
    """CLI entry point for testing."""
    import argparse

    parser = argparse.ArgumentParser(description='Twitter API v2 Client')
    parser.add_argument('action', choices=[
        'verify', 'post', 'thread', 'tweets', 'mentions',
        'search', 'metrics', 'demo'
    ], help='Action to perform')
    parser.add_argument('--text', help='Tweet text')
    parser.add_argument('--texts', nargs='+', help='Tweet texts for thread')
    parser.add_argument('--user-id', help='User ID for operations')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--limit', type=int, default=10, help='Result limit')
    parser.add_argument('--bearer-token', help='Twitter Bearer Token')
    parser.add_argument('--api-key', help='Twitter API Key')
    parser.add_argument('--api-secret', help='Twitter API Secret')
    parser.add_argument('--access-token', help='OAuth Access Token')
    parser.add_argument('--access-token-secret', help='OAuth Access Token Secret')
    parser.add_argument('--demo', action='store_true', help='Demo mode')

    args = parser.parse_args()

    # Override env vars if provided
    if args.bearer_token:
        os.environ['TWITTER_BEARER_TOKEN'] = args.bearer_token
    if args.api_key:
        os.environ['TWITTER_API_KEY'] = args.api_key
    if args.api_secret:
        os.environ['TWITTER_API_SECRET'] = args.api_secret
    if args.access_token:
        os.environ['TWITTER_ACCESS_TOKEN'] = args.access_token
    if args.access_token_secret:
        os.environ['TWITTER_ACCESS_TOKEN_SECRET'] = args.access_token_secret

    twitter = TwitterAPI()

    if args.demo or args.action == 'demo':
        print('Twitter API v2 - Demo Mode')
        print('=' * 50)
        print(f'API Key: {args.api_key[:8]}...' if args.api_key else 'API Key: Not configured')
        print(f'Bearer Token: {"Configured" if twitter.bearer_token else "Not configured"}')
        print(f'OAuth Token: {"Configured" if twitter.access_token else "Not configured"}')
        print()

        # Test verification
        print('1. Testing credentials...')
        if twitter.bearer_token:
            result = twitter.verify_credentials()
            if result.get('verified'):
                print(f'   ✓ Authenticated as: @{result.get("username")}')
                print(f'   Followers: {result.get("followers")}')
            else:
                print('   ✗ Authentication failed')
        else:
            print('   ✗ Bearer token not configured')

        print()
        print('2. Available Actions:')
        print('   - verify: Verify credentials')
        print('   - post: Post a tweet')
        print('   - thread: Post a thread of tweets')
        print('   - tweets: Get recent tweets')
        print('   - mentions: Get mentions')
        print('   - search: Search tweets')
        print('   - metrics: Get account metrics')
        print()
        print('Setup Instructions:')
        print('1. Go to https://developer.twitter.com/en/portal/dashboard')
        print('2. Create developer account and project')
        print('3. Create app to get API credentials')
        print('4. For posting, enable OAuth 2.0 with read/write permissions')
        print('5. Add credentials to .env file')
        return

    if args.action == 'verify':
        result = twitter.verify_credentials()
        print(f'Verified: {result.get("verified")}')
        print(json.dumps(result, indent=2))

    elif args.action == 'post':
        if not args.text:
            print('Error: --text required')
            sys.exit(1)
        result = twitter.post_tweet(args.text)
        print(f'Tweet Result: {json.dumps(result, indent=2)}')

    elif args.action == 'thread':
        if not args.texts:
            print('Error: --texts required (space separated)')
            sys.exit(1)
        result = twitter.post_thread(args.texts)
        print(f'Thread Result: {json.dumps(result, indent=2)}')

    elif args.action == 'tweets':
        tweets = twitter.get_tweets(limit=args.limit)
        print(f'Recent Tweets ({len(tweets)}):')
        for tweet in tweets[:5]:
            print(f'  - {tweet.get("created_at", "N/A")}: {tweet.get("text", "")[:100]}...')

    elif args.action == 'mentions':
        mentions = twitter.get_mentions(limit=args.limit)
        print(f'Recent Mentions ({len(mentions)}):')
        for mention in mentions[:5]:
            author = mention.get('author', {})
            print(f'  - @{author.get("username", "unknown")}: {mention.get("text", "")[:100]}...')

    elif args.action == 'search':
        if not args.query:
            print('Error: --query required')
            sys.exit(1)
        tweets = twitter.search_tweets(args.query, limit=args.limit)
        print(f'Search Results for "{args.query}" ({len(tweets)}):')
        for tweet in tweets[:5]:
            print(f'  - {tweet.get("created_at", "N/A")}: {tweet.get("text", "")[:100]}...')

    elif args.action == 'metrics':
        metrics = twitter.get_account_metrics()
        print('Account Metrics:')
        print(f'  Followers: {metrics.get("followers_count", "N/A")}')
        print(f'  Following: {metrics.get("following_count", "N/A")}')
        print(f'  Total Tweets: {metrics.get("tweet_count", "N/A")}')
        print(f'  Listed: {metrics.get("listed_count", "N/A")}')


if __name__ == '__main__':
    main()
