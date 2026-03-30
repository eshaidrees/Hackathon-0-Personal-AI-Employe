"""Debug Facebook Post"""
import os
import requests
from dotenv import load_dotenv
load_dotenv(override=True)

token = os.getenv('META_PAGE_ACCESS_TOKEN')
page_id = os.getenv('FACEBOOK_PAGE_ID')

print(f"Token: {token[:20]}...")
print(f"Page ID: {page_id}")

# Try to post
url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
params = {
    'message': '🤖 Test post from AI Employee! #AI #Automation',
    'access_token': token
}

print(f"\nPosting to: {url}")
print(f"Message: Test post")

response = requests.post(url, params=params)

print(f"\nStatus Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ SUCCESS!")
    print(f"Post ID: {data.get('id')}")
    print(f"URL: https://facebook.com/{data.get('id')}")
else:
    print(f"\n❌ FAILED!")
    try:
        error = response.json()
        print(f"Error: {error.get('error', {}).get('message')}")
        print(f"Error Code: {error.get('error', {}).get('code')}")
        print(f"Error Subcode: {error.get('error', {}).get('error_subcode')}")
    except:
        print(f"Raw error: {response.text}")
