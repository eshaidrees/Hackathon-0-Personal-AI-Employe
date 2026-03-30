# Twitter (X) Automation Skill

## Purpose
Monitor and post to Twitter/X using **official Twitter API v2** (recommended) or browser automation (Playwright fallback). Handles mentions, DMs, engagement, and business content posting.

## Capabilities
- Monitor Twitter notifications and mentions (API v2)
- Post tweets and threads (API v2)
- Filter by keywords (mention, message, DM, urgent, question)
- Create draft tweets for human approval
- Auto-post after approval
- Get tweet insights and account metrics

## Files
- `scripts/twitter_api.py` - Twitter API v2 client (Recommended)
- `scripts/twitter_watcher.py` - Browser automation fallback
- `scripts/twitter_poster.py` - Browser automation fallback
- `scripts/social_media_mcp.py` - Unified MCP server

## Usage

### Using Official Twitter API v2 (Recommended)

```bash
# Twitter API demo
python scripts/twitter_api.py demo

# Post a tweet
python scripts/twitter_api.py post --text "Hello from Twitter API v2!"

# Post a thread
python scripts/twitter_api.py thread --texts "First tweet" "Second tweet" "Third tweet"

# Get recent tweets
python scripts/twitter_api.py tweets --limit 10

# Get mentions
python scripts/twitter_api.py mentions --limit 25

# Search tweets
python scripts/twitter_api.py search --query "#AI" --limit 10

# Get account metrics
python scripts/twitter_api.py metrics
```

### Using Unified Social Media MCP

```bash
# Demo
python scripts/social_media_mcp.py demo

# Post to Twitter
python scripts/social_media_mcp.py post --platform twitter --content "Hello World!"

# Get recent posts
python scripts/social_media_mcp.py posts --platform twitter --limit 5

# Get notifications (mentions)
python scripts/social_media_mcp.py notifications --platform twitter --limit 10
```

### Using Browser Automation (Fallback)

```bash
# Twitter watcher (notifications)
python scripts/twitter_watcher.py --vault ../AI_Employee_Vault --interval 300

# Twitter poster
python scripts/twitter_poster.py --vault ../AI_Employee_Vault --demo
```

## Configuration

### Environment Variables (Official API v2 - Recommended)
```bash
# Twitter Developer Account
# Get from: https://developer.twitter.com/en/portal/dashboard
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Note: For posting, you need OAuth 2.0 with read/write permissions
```

### Environment Variables (Browser Automation - Fallback)
```bash
# Twitter credentials
TWITTER_EMAIL=your@email.com
TWITTER_USERNAME=your_handle
TWITTER_PASSWORD=your_password
TWITTER_SESSION_PATH=./twitter_session

# Keywords for filtering
TWITTER_KEYWORDS=mention,message,DM,urgent,question

# Approval required for posts
TWITTER_POST_APPROVAL_REQUIRED=true
```

## First-Time Setup

### Step 1: Run Watcher
```bash
python scripts/twitter_watcher.py --vault ../AI_Employee_Vault
```

### Step 2: Manual Login
- Browser will open automatically
- Log in to Twitter/X manually
- Wait for redirect to timeline/home page
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
1. Claude generates tweet content
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
type: twitter_notification
platform: twitter
notification_type: mention
received: 2026-03-14T10:30:00
keywords: mention, question
priority: high
status: pending
---

# Twitter Notification

## Notification Type
Mention

## Content
@YourBusiness Hey, I have a question about your services.
Can you help me with pricing for enterprise plans?

## Detected Keywords
- mention
- question

## Suggested Actions
- [ ] Review mention
- [ ] Draft response with pricing info
- [ ] Get approval
- [ ] Send response
```

### Tweet Draft
```markdown
---
type: twitter_post_draft
post_id: TWITTER_POST_20260314_103000
platform: twitter
created: 2026-03-14T10:30:00
category: business_update
status: pending_approval
is_thread: false
character_count: 145
---

# Twitter Post Draft

## Content
Excited to announce our new AI-powered services!
We're helping businesses automate their workflows and save time.

## Hashtags
#AI #Automation #Business

## Character Count
145 / 280

## Instructions
1. Review the tweet content
2. Ensure it meets Twitter character limit
3. Move to /Approved/ to publish
4. Move to /Rejected/ to discard
```

## Notification Types

| Type | Description | Priority |
|------|-------------|----------|
| mention | Someone mentioned your account | High |
| message | Direct message received | High |
| like | Someone liked your tweet | Low |
| repost | Someone reposted your content | Low |
| follow | New follower | Low |

## Error Handling

- Login failures trigger manual login requirement
- Session expiry detected and reported
- Network errors trigger retry logic
- Posting failures create error quarantine files
- Character limit violations reported

## Audit Logging

All actions logged via audit_logger.py:
- Notification detected
- Tweet created
- Tweet approved
- Tweet published
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

### Tweet Not Publishing
- Check if file is in Approved/ folder
- Verify session is still valid
- Check character count (must be ≤ 280)
- Review browser console for errors

### Composer Not Opening
- Twitter UI may have changed
- Check for manual intervention required
- Review error logs for details

---

*Skill Version: 1.0*
*AI Employee v0.3 - Gold Tier*
