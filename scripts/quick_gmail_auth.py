"""
Quick Gmail OAuth2 Authentication - Simplified Version
Handles common authentication issues automatically
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def authenticate():
    """Simple Gmail authentication with better error handling."""
    
    credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
    token_path = os.getenv('GMAIL_TOKEN_PATH', 'token.json')
    
    # Check credentials file
    if not Path(credentials_path).exists():
        print(f"ERROR: credentials.json not found at {credentials_path}")
        print("\nDownload from Google Cloud Console:")
        print("1. Go to: https://console.cloud.google.com/apis/credentials")
        print("2. Click + CREATE CREDENTIALS → OAuth client ID")
        print("3. Application type: Desktop app")
        print("4. Download and save as credentials.json")
        sys.exit(1)
    
    print("=" * 60)
    print("GMAIL AUTHENTICATION")
    print("=" * 60)
    
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        import pickle
        
        # Gmail API scopes
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify',
        ]
        
        creds = None
        
        # Load existing token
        if Path(token_path).exists():
            try:
                with open(token_path, 'rb') as f:
                    creds = pickle.load(f)
                print(f"✓ Found existing token: {token_path}")
            except Exception as e:
                print(f"Warning: Could not load token: {e}")
                creds = None
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("⏳ Refreshing expired token...")
                try:
                    creds.refresh(Request())
                    print("✓ Token refreshed!")
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    print("\n→ Will request new authentication")
                    creds = None
            
            if not creds:
                print("\n📱 Opening browser for authentication...")
                print("\nIMPORTANT:")
                print("- Select your Google account: esha35319@gmail.com")
                print("- Grant all permissions when prompted")
                print("- If you see 'Access blocked', see troubleshooting below")
                print("\n" + "-" * 60)
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(
                    port=0,
                    open_browser=True,
                    prompt='consent'  # Force consent screen
                )
                
                if creds:
                    print("✓ Authentication successful!")
        
        # Save token
        with open(token_path, 'wb') as f:
            pickle.dump(creds, f)
        print(f"✓ Token saved to: {token_path}")
        
        # Test connection
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        
        print("\n" + "=" * 60)
        print("AUTHENTICATION COMPLETE ✓")
        print("=" * 60)
        print(f"Email: {profile['emailAddress']}")
        print(f"Name: {profile['name']}")
        print(f"Token file: {token_path}")
        print("\nYou can now run Gmail Watcher!")
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"\nERROR: Missing required packages: {e}")
        print("\nInstall with:")
        print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        sys.exit(1)
        
    except Exception as e:
        error_msg = str(e)
        print(f"\nERROR: Authentication failed: {e}")
        
        if 'access_denied' in error_msg.lower() or '403' in error_msg:
            print("\n" + "=" * 60)
            print("TROUBLESHOOTING: Access Denied (Error 403)")
            print("=" * 60)
            print("\nYour Google Cloud OAuth consent screen needs configuration:")
            print("\n1. Go to: https://console.cloud.google.com/apis/credentials/consent")
            print("2. Select your project from the dropdown at the top")
            print("3. If not configured, click CREATE or GET STARTED:")
            print("   - User Type: External")
            print("   - App name: AI Employee")
            print("   - User support email: esha35319@gmail.com")
            print("   - Developer contact: esha35319@gmail.com")
            print("4. Click SAVE AND CONTINUE (3 times, skip Scopes)")
            print("5. On 'Test users' page, click + ADD USERS")
            print("6. Add: esha35319@gmail.com")
            print("7. Click ADD → SAVE")
            print("8. Wait 2-3 minutes, then run this script again")
            print("\nAlternative: Create a new Google Cloud project")
            print("  → https://console.cloud.google.com/projectcreate")
            print("=" * 60)
        
        sys.exit(1)


if __name__ == '__main__':
    authenticate()
