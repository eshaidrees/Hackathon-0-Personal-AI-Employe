"""
Gmail OAuth2 Authentication Script
Authenticates with Gmail API and saves token for reuse
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def authenticate_gmail(credentials_path: str = None, token_path: str = None):
    """
    Authenticate with Gmail API using OAuth2.
    
    Args:
        credentials_path: Path to credentials.json from Google Cloud Console
        token_path: Path to save/load token.json
    """
    credentials_path = credentials_path or os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
    token_path = token_path or os.getenv('GMAIL_TOKEN_PATH', 'token.json')
    
    # Check if credentials file exists
    if not Path(credentials_path).exists():
        print(f"Error: Credentials file not found at {credentials_path}")
        print("\nTo get credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download credentials.json")
        print("6. Place it in the project directory")
        sys.exit(1)
    
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        import pickle
        
        # Gmail API scopes
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/gmail.compose'
        ]
        
        creds = None
        
        # Load existing token
        if Path(token_path).exists():
            try:
                with open(token_path, 'rb') as f:
                    creds = pickle.load(f)
                print(f"✓ Loaded existing token from {token_path}")
            except Exception as e:
                print(f"Warning: Could not load token: {e}")
                creds = None
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing expired token...")
                try:
                    creds.refresh(Request())
                    print("✓ Token refreshed successfully")
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                print("\n" + "="*60)
                print("GMAIL API AUTHENTICATION")
                print("="*60)
                print("\nOpening browser for OAuth2 authentication...")
                print("\nSteps:")
                print("1. Select your Google account")
                print("2. Grant permissions to the application")
                print("3. You will be redirected to a success page")
                print("\n" + "="*60 + "\n")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0, open_browser=True)
                
                if creds:
                    print("✓ Authentication successful!")
        
        # Save the credentials for the next run
        with open(token_path, 'wb') as f:
            pickle.dump(creds, f)
        print(f"✓ Token saved to {token_path}")
        
        # Print account info
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        
        print("\n" + "="*60)
        print("AUTHENTICATION COMPLETE")
        print("="*60)
        print(f"Email: {profile['emailAddress']}")
        print(f"Name: {profile['name']}")
        print("\nToken file: {token_path}")
        print("\nYou can now use Gmail Watcher with full API access!")
        print("="*60 + "\n")
        
        return True
        
    except ImportError:
        print("\nError: Gmail API libraries not installed")
        print("\nInstall required packages:")
        print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib\n")
        sys.exit(1)
        
    except Exception as e:
        print(f"\nAuthentication error: {e}")
        sys.exit(1)


def test_gmail_api(token_path: str = None):
    """Test Gmail API connection."""
    token_path = token_path or os.getenv('GMAIL_TOKEN_PATH', 'token.json')
    credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
    
    if not Path(token_path).exists():
        print("No token found. Please run authentication first.")
        return False
    
    try:
        import pickle
        from googleapiclient.discovery import build
        
        with open(token_path, 'rb') as f:
            creds = pickle.load(f)
        
        service = build('gmail', 'v1', credentials=creds)
        
        # Get profile
        profile = service.users().getProfile(userId='me').execute()
        
        # Get unread count
        results = service.users().messages().list(
            userId='me', q='is:unread', maxResults=1
        ).execute()
        unread_count = len(results.get('messages', []))
        
        print("\n" + "="*60)
        print("GMAIL API TEST - SUCCESS")
        print("="*60)
        print(f"Email: {profile['emailAddress']}")
        print(f"Name: {profile['name']}")
        print(f"Total Messages: {profile['messagesTotal']}")
        print(f"Threads: {profile['threadsTotal']}")
        print(f"Unread Messages: {unread_count}")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"Gmail API test failed: {e}")
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Gmail OAuth2 Authentication')
    parser.add_argument('--credentials', default='credentials.json',
                       help='Path to credentials.json')
    parser.add_argument('--token', default='token.json',
                       help='Path to save/load token.json')
    parser.add_argument('--test', action='store_true',
                       help='Test Gmail API connection')
    
    args = parser.parse_args()
    
    if args.test:
        test_gmail_api(args.token)
    else:
        authenticate_gmail(args.credentials, args.token)


if __name__ == '__main__':
    main()
