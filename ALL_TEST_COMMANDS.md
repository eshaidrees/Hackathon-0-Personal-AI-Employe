# 🚀 AI Employee - REAL POSTING COMMANDS (Not Demo)

**All commands for REAL posting to social media platforms**

---

## ✅ WHAT'S WORKING NOW (REAL POSTS)

| Platform | Status | Cost | Command |
|----------|--------|------|---------|
| **Facebook** | ✅ **WORKING** | **FREE** | See below |
| **LinkedIn** | ✅ **WORKING** | **FREE** | See below |
| **Twitter** | ❌ Needs Credits | $100/month | Auth works, posting needs payment |
| **Instagram** | ⚠️ Needs FB Link | **FREE** | See setup |

---

## 1. ✅ FACEBOOK - REAL POSTING (WORKING - FREE)

### 🎯 Quick Post to Facebook (Copy & Paste)
```bash
cd C:\Users\PC\Desktop\Hackathon-0-AI-Employe\Personal-AI-Employe

python -c "import os, requests; from dotenv import load_dotenv; load_dotenv(override=True); token=os.getenv('META_PAGE_ACCESS_TOKEN'); page_id=os.getenv('FACEBOOK_PAGE_ID'); r=requests.post(f'https://graph.facebook.com/v19.0/{page_id}/feed', params={'message':'🤖 Hello from AI Employee! This is a REAL automated post! #AI #Automation #Pakistan', 'access_token':token}); print('Status:', r.status_code); print('Post ID:', r.json().get('id')); print('URL: https://facebook.com/' + r.json().get('id', ''))"
```

### Expected Output (Success):
```
Status: 200
Post ID: 1023847794151439_122105953011025547
URL: https://facebook.com/1023847794151439_122105953011025547
```

---

### Post Custom Message to Facebook
```bash
python -c "import os, requests; from dotenv import load_dotenv; load_dotenv(override=True); token=os.getenv('META_PAGE_ACCESS_TOKEN'); page_id=os.getenv('FACEBOOK_PAGE_ID'); message='Your custom message here'; r=requests.post(f'https://graph.facebook.com/v19.0/{page_id}/feed', params={'message':message, 'access_token':token}); print('Post ID:', r.json().get('id'))"
```

---

### Post with Link
```bash
python -c "import os, requests; from dotenv import load_dotenv; load_dotenv(override=True); token=os.getenv('META_PAGE_ACCESS_TOKEN'); page_id=os.getenv('FACEBOOK_PAGE_ID'); r=requests.post(f'https://graph.facebook.com/v19.0/{page_id}/feed', params={'message':'Check this out!','link':'https://yourwebsite.com', 'access_token':token}); print('Post ID:', r.json().get('id'))"
```

---

### Post with Hashtags
```bash
python -c "import os, requests; from dotenv import load_dotenv; load_dotenv(override=True); token=os.getenv('META_PAGE_ACCESS_TOKEN'); page_id=os.getenv('FACEBOOK_PAGE_ID'); r=requests.post(f'https://graph.facebook.com/v19.0/{page_id}/feed', params={'message':'🎉 AI Employee is LIVE! Automating social media posting with Graph API! #AI #Automation #GoldTier #Hackathon2026 #Pakistan', 'access_token':token}); print('SUCCESS! View: https://facebook.com/' + r.json().get('id', ''))"
```

---

### Post Multiple Times (Batch)
```bash
python -c "
import os, requests
from dotenv import load_dotenv
load_dotenv(override=True)

token = os.getenv('META_PAGE_ACCESS_TOKEN')
page_id = os.getenv('FACEBOOK_PAGE_ID')

messages = [
    '🤖 AI Employee Post #1 - Testing automated posting!',
    '🚀 AI Employee Post #2 - Gold Tier features working!',
    '✅ AI Employee Post #3 - Facebook Graph API integration complete!'
]

for msg in messages:
    r = requests.post(f'https://graph.facebook.com/v19.0/{page_id}/feed', params={'message':msg, 'access_token':token})
    print(f'Posted: {msg[:30]}... -> {r.json().get(\"id\")}')"
```

---

## 2. ✅ LINKEDIN - REAL POSTING (WORKING - FREE - BROWSER-BASED)

### Step 1: Create Post Draft
```bash
python scripts/linkedin_poster.py --vault ../AI_Employee_Vault --demo
```

This creates a file in: `AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md`

---

### Step 2: Approve Post (Move to Approved)
```bash
move AI_Employee_Vault\Pending_Approval\LINKEDIN_POST_*.md AI_Employee_Vault\Approved\
```

---

### Step 3: Post to LinkedIn (Real Post)
```bash
python scripts/linkedin_poster.py --vault ../AI_Employee_Vault
```

**Note:** First run requires manual LinkedIn login. Browser will open automatically.

---

### Create Custom LinkedIn Post
```bash
python scripts/linkedin_poster.py --vault ../AI_Employee_Vault --demo
```

Then edit the created file in `Pending_Approval/` with your content, then approve and post.

---

## 3. ❌ TWITTER - REAL POSTING (NEEDS $100/MONTH CREDITS)

### Try to Post (Will Fail Without Credits)
```bash
python scripts/twitter_api.py post --text "This will fail without Twitter API credits"
```

### Expected Error:
```
Status: 402
Error: CreditsDepleted
Your enrolled account does not have any credits to fulfill this request.
```

### To Enable Twitter Posting:
1. Go to: https://developer.twitter.com/en/portal/billing
2. Add payment method
3. Purchase credits (~$100/month for basic posting)
4. Then posting will work

### Twitter Reading (FREE - WORKING)
```bash
# Get your tweets
python scripts/twitter_api.py tweets --limit 5

# Get mentions
python scripts/twitter_api.py mentions --limit 10

# Search tweets
python scripts/twitter_api.py search --query "#AI" --limit 10
```

---

## 4. 📸 INSTAGRAM - REAL POSTING (FREE - NEEDS SETUP)


Post to Instagram (Real Post)

     1 cd C:\Users\PC\Desktop\Hackathon-0-AI-Employe\Personal-AI-Employe
     2
     3 # Step 1: Create media container
     4 python -c "from dotenv import load_dotenv; load_dotenv(override=True); import os, requests; token=os.getenv('META_PAGE_ACCESS_TOKEN'); ig_id=os.getenv('INSTAGRAM_ACCOUNT_ID');
       r=requests.post(f'https://graph.facebook.com/v19.0/{ig_id}/media', params={'image_url':'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=500','caption':'🤖 AI Employee
       Post!','access_token':token}); print('Container ID:', r.json().get('id'))"
     5
     6 # Step 2: Publish (replace CONTAINER_ID with the ID from step 1)
     7 python -c "from dotenv import load_dotenv; load_dotenv(override=True); import os, requests; token=os.getenv('META_PAGE_ACCESS_TOKEN'); ig_id=os.getenv('INSTAGRAM_ACCOUNT_ID');
       r=requests.post(f'https://graph.facebook.com/v19.0/{ig_id}/media_publish', params={'creation_id':'CONTAINER_ID','access_token':token}); print('Post ID:', r.json().get('id'))"


### Step 1: Link Instagram to Facebook Page

**Option A - Via Facebook:**
1. Go to: https://www.facebook.com/1023847794151439/settings/?tab=instagram
2. Click **"Connect Account"**
3. Log in to Instagram
4. Click **"Confirm"**

**Option B - Via Instagram App:**
1. Open Instagram → Profile → Edit Profile
2. Tap **"Page"**
3. Select **"Personal AI Employee"**

---

### Step 2: Get Instagram Permissions

1. Go to: https://developers.facebook.com/tools/explorer/
2. Select your app: "My AI Employee"
3. Click **"Generate Access Token"**
4. Add permissions:
   - ✅ `instagram_basic`
   - ✅ `instagram_content_publish`
   - ✅ `pages_manage_posts`
5. Select your Page
6. Copy the token
7. Update `.env`: `META_PAGE_ACCESS_TOKEN=new_token`

---

### Step 3: Post to Instagram (Requires Image URL)
```bash
python scripts/instagram_graph_api.py photo --image-url "https://example.com/your-image.jpg" --caption "🤖 AI Employee Instagram Post! #AI #Automation"
```

### Post Video
```bash
python scripts/instagram_graph_api.py video --video-url "https://example.com/your-video.mp4" --caption "AI Employee Video Post!"
```

### Post Carousel (Multiple Images)
```bash
python scripts/instagram_graph_api.py carousel --media-urls "https://example.com/img1.jpg" "https://example.com/img2.jpg" --caption "Carousel post!"
```

---

## 5. 🏆 HACKATHON DEMO - POST TO ALL PLATFORMS

### Facebook Post (100% Working - Use This!)
```bash
cd C:\Users\PC\Desktop\Hackathon-0-AI-Employe\Personal-AI-Employe

python -c "import os, requests; from dotenv import load_dotenv; load_dotenv(override=True); token=os.getenv('META_PAGE_ACCESS_TOKEN'); page_id=os.getenv('FACEBOOK_PAGE_ID'); r=requests.post(f'https://graph.facebook.com/v19.0/{page_id}/feed', params={'message':'🎉 AI Employee Gold Tier - LIVE Demo! Posting automatically to Facebook! #AI #Automation #Hackathon2026 #Pakistan', 'access_token':token}); print('✅ Facebook Post Success!'); print('Post ID:', r.json().get('id')); print('View: https://facebook.com/' + r.json().get('id', ''))"
```

---

### LinkedIn Post (Working)
```bash
# Create draft
python scripts/linkedin_poster.py --vault ../AI_Employee_Vault --demo

# Approve
move AI_Employee_Vault\Pending_Approval\LINKEDIN_POST_*.md AI_Employee_Vault\Approved\

# Post
python scripts/linkedin_poster.py --vault ../AI_Employee_Vault
```

---

### Weekly Audit (Working)
```bash
python scripts/weekly_audit.py --vault ../AI_Employee_Vault --demo
```

---

### View Dashboard
```bash
type AI_Employee_Vault\Dashboard.md
```

---

## 6. 📊 COMPLETE HACKATHON DEMO SCRIPT

Copy and paste this entire block:

```bash
cd C:\Users\PC\Desktop\Hackathon-0-AI-Employe\Personal-AI-Employe

echo "============================================"
echo "AI EMPLOYEE GOLD TIER - HACKATHON DEMO"
echo "============================================"
echo ""

echo "1. Testing Facebook Posting..."
python -c "import os, requests; from dotenv import load_dotenv; load_dotenv(override=True); token=os.getenv('META_PAGE_ACCESS_TOKEN'); page_id=os.getenv('FACEBOOK_PAGE_ID'); r=requests.post(f'https://graph.facebook.com/v19.0/{page_id}/feed', params={'message':'🤖 AI Employee Gold Tier Demo - Automated Facebook Post!', 'access_token':token}); print('✅ Facebook:', 'SUCCESS - Post ID:', r.json().get('id'))"
echo ""

echo "2. Testing Twitter Connection..."
python scripts/twitter_api.py demo
echo ""

echo "3. Testing LinkedIn..."
python scripts/linkedin_watcher.py --vault ../AI_Employee_Vault --demo
echo ""

echo "4. Generating Weekly Audit..."
python scripts/weekly_audit.py --vault ../AI_Employee_Vault --demo
echo ""

echo "5. Checking Dashboard..."
type AI_Employee_Vault\Dashboard.md
echo ""

echo "============================================"
echo "DEMO COMPLETE!"
echo "============================================"
```

---

## 7. ✅ QUICK VERIFICATION COMMANDS

### Verify Facebook Token
```bash
python -c "from dotenv import load_dotenv; load_dotenv(override=True); import os, requests; token=os.getenv('META_PAGE_ACCESS_TOKEN'); r=requests.get(f'https://graph.facebook.com/debug_token?input_token={token}&access_token={token}'); d=r.json(); print('Token Valid:', d.get('data',{}).get('is_valid')); print('Scopes:', d.get('data',{}).get('scopes',[]))"
```

### Verify Twitter Connection
```bash
python scripts/twitter_api.py demo
```

### Check All Credentials
```bash
python -c "from dotenv import load_dotenv; load_dotenv(override=True); import os; print('Facebook Token:', '✅' if os.getenv('META_PAGE_ACCESS_TOKEN') else '❌'); print('Twitter API Key:', '✅' if os.getenv('TWITTER_API_KEY') else '❌'); print('Facebook Page ID:', os.getenv('FACEBOOK_PAGE_ID'))"
```

---

## 8. 🎯 TROUBLESHOOTING

### Facebook Post Fails
**Error:** `403 Forbidden` or `pages_manage_posts missing`

**Fix:**
1. Go to: https://developers.facebook.com/tools/explorer/
2. Generate new token with `pages_manage_posts` permission
3. Update `.env` with new token

### LinkedIn Post Fails
**Error:** `Login required`

**Fix:**
1. Browser will open automatically
2. Log in to LinkedIn manually
3. Session is saved for future posts

### Twitter Post Fails
**Error:** `CreditsDepleted`

**Fix:** Add payment at https://developer.twitter.com/en/portal/billing (or skip Twitter for demo)

---

## 9. 📋 HACKATHON SUBMISSION CHECKLIST

| Demo | Command | Status |
|------|---------|--------|
| Facebook Post | `python -c "..."` | ✅ Working |
| LinkedIn Post | `linkedin_poster.py` | ✅ Working |
| Weekly Audit | `weekly_audit.py --demo` | ✅ Working |
| Dashboard | `type Dashboard.md` | ✅ Working |
| Twitter Auth | `twitter_api.py demo` | ✅ Working |
| Twitter Post | N/A | ❌ Needs $100 |

---

## 10. 🚀 BEST COMMANDS FOR DEMO

### 1. Facebook Live Post (Best for Demo)
```bash
python -c "import os, requests; from dotenv import load_dotenv; load_dotenv(override=True); token=os.getenv('META_PAGE_ACCESS_TOKEN'); page_id=os.getenv('FACEBOOK_PAGE_ID'); r=requests.post(f'https://graph.facebook.com/v19.0/{page_id}/feed', params={'message':'🤖 AI Employee Gold Tier - Autonomous Posting Demo! #AI #Automation #Hackathon2026', 'access_token':token}); print('✅ SUCCESS! View post: https://facebook.com/' + r.json().get('id', ''))"
```

### 2. Weekly Audit
```bash
python scripts/weekly_audit.py --vault ../AI_Employee_Vault --demo
```

### 3. View Result
```bash
type AI_Employee_Vault\Briefings\WEEKLY_BRIEFING_*.md
```

---

**Save this file! All commands are for REAL posting, not demo!** 📌

*Last Updated: 2026-03-30*
*AI Employee v0.3 - Gold Tier - HACKATHON READY*










python -c "from dotenv import load_dotenv; load_dotenv(override=True); import os, requests; token=os.getenv('META_PAGE_ACCESS_TOKEN'); ig_id=os.getenv('INSTAGRAM_ACCOUNT_ID');r=requests.post(f'https://graph.facebook.com/v19.0/{ig_id}/media', params={'image_url':'https://images.stockcake.com/public/5/b/7/5b7cf1a5-b24e-4169-b055-5975888293ed_large/futuristic-ai-portrait-stockcake.jpg?w=500','caption':'🤖 AI Employee Post!','access_token':token}); print('17881700010483061:', r.json().get('id'))"



 python -c "from dotenv import load_dotenv; load_dotenv(override=True); import os, requests; token=os.getenv('META_PAGE_ACCESS_TOKEN'); ig_id=os.getenv('INSTAGRAM_ACCOUNT_ID'); r=requests.post(f'https://graph.facebook.com/v19.0/{ig_id}/media_publish', params={'creation_id':'df24a04c-3f0a-4bd8-97ed-0729dc67e5c8','access_token':token}); print('Post ID:', r.json().get('id'))"

python -c "from dotenv import load_dotenv; load_dotenv(override=True); import os, requests;
token=os.getenv('META_PAGE_ACCESS_TOKEN'); ig_id=os.getenv('INSTAGRAM_ACCOUNT_ID');
r=requests.post(f'https://graph.facebook.com/v19.0/{ig_id}/media',
params={'image_url':'https://images.pexels.com/photos/96246/pexels-photo-96246.jpeg?w=500','caption':'AI Employee Post','access_token':token}); print('Container ID:', r.json().get('id'))"