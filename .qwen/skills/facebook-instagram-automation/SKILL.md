# Facebook/Instagram Automation Skill

## Purpose
Monitor and post to Facebook and Instagram using **official Meta Graph API** (recommended) or browser automation (Playwright fallback). Handles notifications, messages, and business content posting.

## Capabilities
- Monitor Facebook notifications and mentions (Graph API)
- Monitor Instagram engagement (Graph API)
- Filter by keywords (message, comment, share, mention, urgent)
- Create draft posts for human approval
- Auto-post after approval
- Get platform insights/analytics

## Files
- `scripts/facebook_graph_api.py` - Facebook Graph API client (Recommended)
- `scripts/instagram_graph_api.py` - Instagram Graph API client (Recommended)
- `scripts/facebook_instagram_watcher.py` - Browser automation fallback
- `scripts/facebook_instagram_poster.py` - Browser automation fallback
- `scripts/social_media_mcp.py` - Unified MCP server

## Usage

### Using Official APIs (Recommended)

```bash
# Facebook Graph API
python scripts/facebook_graph_api.py demo
python scripts/facebook_graph_api.py post --message "Hello from API!"
python scripts/facebook_graph_api.py insights

# Instagram Graph API
python scripts/instagram_graph_api.py demo
python scripts/instagram_graph_api.py photo --image-url https://example.com/image.jpg --caption "New post!"
python scripts/instagram_graph_api.py insights

# Unified Social Media MCP
python scripts/social_media_mcp.py demo
python scripts/social_media_mcp.py post --platform facebook --content "Hello World!"
python scripts/social_media_mcp.py posts --platform instagram --limit 5
```

### Using Browser Automation (Fallback)

```bash
# Facebook watcher (notifications)
python scripts/facebook_instagram_watcher.py --platform facebook --vault ../AI_Employee_Vault --interval 300

# Facebook poster
python scripts/facebook_instagram_poster.py --platform facebook --vault ../AI_Employee_Vault --demo
```

## Configuration

### Environment Variables (Official API - Recommended)
```bash
# Meta Developer App
# Get from: https://developers.facebook.com/apps/
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_PAGE_ACCESS_TOKEN=your_page_access_token
FACEBOOK_PAGE_ID=your_page_id

# Instagram Business Account
INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id
```

### Environment Variables (Browser Automation - Fallback)
```bash
# Facebook credentials
FACEBOOK_EMAIL=your@email.com
FACEBOOK_PASSWORD=your_password
FACEBOOK_SESSION_PATH=./facebook_session

# Instagram credentials
INSTAGRAM_EMAIL=your@email.com
INSTAGRAM_PASSWORD=your_password
INSTAGRAM_SESSION_PATH=./instagram_session

# Keywords for filtering
SOCIAL_KEYWORDS=message,comment,share,mention,urgent

# Approval required for posts
SOCIAL_POST_APPROVAL_REQUIRED=true
```

## First-Time Setup

### Step 1: Run Watcher
```bash
python scripts/facebook_instagram_watcher.py --platform facebook --vault ../AI_Employee_Vault
```

### Step 2: Manual Login
- Browser will open automatically
- Log in to Facebook/Instagram manually
- Wait for redirect to feed/home page
- Session is saved for future runs

### Step 3: Verify Session
- Subsequent runs will use saved session
- No manual login required unless session expires

## Workflow

### Notification Monitoring
```
1. Watcher runs every 5 minutes
2. Opens browser with saved session
3. Navigates to notifications page
4. Parses notifications for keywords
5. Creates action file in Needs_Action/
6. Claude Code processes and suggests response
7. Human approves response
8. Response sent (if applicable)
```

### Content Posting
```
1. Claude generates post content
2. Creates draft in Pending_Approval/
3. Human reviews and moves to Approved/
4. Poster publishes via Playwright
5. Screenshot saved to Done/
6. Task marked complete
```

## Action File Format

### Notification
```markdown
---
type: facebook_notification
platform: facebook
received: 2026-03-14T10:30:00
keywords: message, urgent
priority: high
status: pending
---

# Facebook Notification

## Content
Someone mentioned your business: "Need help with services urgently!"

## Detected Keywords
- message
- urgent

## Suggested Actions
- [ ] Review notification
- [ ] Draft response
- [ ] Get approval
- [ ] Send response
```

### Post Draft
```markdown
---
type: facebook_post_draft
post_id: FACEBOOK_POST_20260314_103000
platform: facebook
created: 2026-03-14T10:30:00
category: business_update
status: pending_approval
---

# Facebook Post Draft

## Content
Excited to announce our new AI-powered services!

## Hashtags
#AI #Business #Innovation

## Instructions
1. Review the post content
2. Move to /Approved/ to publish
3. Move to /Rejected/ to discard
```

## Error Handling

- Login failures trigger manual login requirement
- Session expiry detected and reported
- Network errors trigger retry logic
- Posting failures create error quarantine files

## Audit Logging

All actions logged via audit_logger.py:
- Notification detected
- Post created
- Post approved
- Post published
- Errors and retries

## Troubleshooting

### Login Timeout
- First run requires manual login
- Wait for browser to open (up to 90 seconds)
- Complete login before timeout

### No Notifications Found
- Check keyword filters in environment
- Verify account has notifications
- Try increasing check interval

### Post Not Publishing
- Check if file is in Approved/ folder
- Verify session is still valid
- Review browser console for errors

### Instagram Post Requires Image
- Instagram requires images for posts
- Current implementation handles caption only
- Full image upload requires additional implementation

---

*Skill Version: 1.0*
*AI Employee v0.3 - Gold Tier*
