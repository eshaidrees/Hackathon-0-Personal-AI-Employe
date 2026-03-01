---
name: linkedin-poster
description: |
  LinkedIn automation using Playwright MCP. Create, schedule, and post content
  to LinkedIn for business lead generation. Supports text posts, articles, and
  engagement tracking. Requires human approval before posting.
---

# LinkedIn Poster

Automate LinkedIn content posting for business lead generation using Playwright browser automation.

## Prerequisites

```bash
# Install Playwright (if not already installed)
pip install playwright
playwright install

# Install python-dotenv for configuration
pip install python-dotenv
```

## Quick Reference

### Basic Usage

```bash
# Create a LinkedIn post draft (requires approval)
python scripts/linkedin_poster.py --action create --content "Excited to announce..."

# Schedule a post for later
python scripts/linkedin_poster.py --action schedule --content "Post content..." --time "2026-03-01T09:00:00"

# Post with image
python scripts/linkedin_poster.py --action create --content "Post content..." --image ./image.png

# List scheduled posts
python scripts/linkedin_poster.py --action list

# Cancel a scheduled post
python scripts/linkedin_poster.py --action cancel --id POST_001
```

### Configuration

```bash
# Add to .env file
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password
LINKEDIN_SESSION_PATH=./linkedin_session
POST_APPROVAL_REQUIRED=true
```

## Workflow

1. **Content Creation**: AI generates post content based on business goals
2. **Draft File**: Creates draft post in `/Pending_Approval/` folder
3. **Human Review**: User reviews and approves content
4. **Browser Automation**: Playwright logs in and posts content
5. **Confirmation**: Screenshot and confirmation logged

## Post Templates

### Business Update Template

```markdown
---
type: linkedin_post
category: business_update
created: 2026-02-28T10:00:00Z
status: draft
approval_required: true
---

# LinkedIn Post Draft

## Content
🚀 Excited to share that we've reached a new milestone! 

[Post content here]

## Hashtags
#Business #Growth #Innovation #AI

## Media
- [ ] No media
- [ ] Image: [path]
- [ ] Document: [path]

## Posting Schedule
- [ ] Post immediately (after approval)
- [ ] Schedule for: [datetime]

## Approval
Move to /Approved/ to post
Move to /Rejected/ to cancel

---
*Created by LinkedIn Poster - AI Employee v0.1*
```

### Lead Generation Template

```markdown
---
type: linkedin_post
category: lead_generation
created: 2026-02-28T10:00:00Z
status: draft
approval_required: true
target_audience: business_owners
---

# LinkedIn Post Draft: Lead Generation

## Hook
Are you still doing [manual task] manually in 2026?

## Problem
[Describe pain point]

## Solution
[Introduce your service/product]

## Call to Action
DM me for a free consultation!

## Hashtags
#Automation #AI #BusinessEfficiency

---
*Created by LinkedIn Poster - AI Employee v0.1*
```

## Content Guidelines

### Post Structure
1. **Hook** (first 150 characters - critical for engagement)
2. **Value** (main content, 300-1300 characters)
3. **CTA** (clear call to action)
4. **Hashtags** (3-5 relevant hashtags)

### Best Practices
- ✅ Post during business hours (9 AM - 5 PM)
- ✅ Use line breaks for readability
- ✅ Include relevant hashtags
- ✅ Add media when possible (2x engagement)
- ✅ Engage with comments within 2 hours

### What to Avoid
- ❌ Overly promotional language
- ❌ Too many hashtags (>5)
- ❌ Controversial topics
- ❌ Posting without approval

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Content Ideas  │────▶│  LinkedIn Poster │────▶│ Pending_Approval│
│  (AI Generated) │     │  (Draft Creator) │     │ /POST_*.md      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                       │
                                                       ▼
                                                ┌──────────────────┐
                                                │  Human Approval  │
                                                └────────┬─────────┘
                                                         │
                        ┌────────────────────────────────┘
                        ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Confirmation   │◀────│  Playwright      │◀────│  Approved/      │
│  & Screenshot   │     │  Browser Bot     │     │  (Trigger)      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Action Files

### Draft Post File

```markdown
---
type: linkedin_post_draft
post_id: POST_20260228_001
created: 2026-02-28T10:00:00Z
scheduled_for: null
status: pending_approval
---

# LinkedIn Post Draft: POST_20260228_001

## Content
🚀 Just completed an amazing AI automation project!

We helped a client reduce manual data entry by 90% using
custom AI agents. The results?
- 20 hours saved per week
- Zero errors in data processing
- Team can focus on strategic work

Ready to transform your business? Let's talk!

## Hashtags
#AI #Automation #BusinessEfficiency #DigitalTransformation

## To Approve
1. Review content above
2. Move this file to /Approved/ to post
3. Move to /Rejected/ to cancel

---
*Created by LinkedIn Poster - AI Employee v0.1*
```

## MCP Integration

For direct LinkedIn API integration (alternative to browser automation):

```javascript
// mcp.json configuration
{
  "servers": [
    {
      "name": "linkedin",
      "command": "node",
      "args": ["/path/to/linkedin-mcp/index.js"],
      "env": {
        "LINKEDIN_ACCESS_TOKEN": "your_token"
      }
    }
  ]
}
```

## Scheduling

### Cron Schedule (Linux/Mac)

```bash
# Post every weekday at 9 AM
0 9 * * 1-5 cd /path/to/project && python scripts/linkedin_poster.py --action post-scheduled

# Check for approved posts every hour
0 * * * * cd /path/to/project && python scripts/linkedin_poster.py --action check-approved
```

### Task Scheduler (Windows)

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "python" -Argument "scripts/linkedin_poster.py --action post-scheduled"
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
Register-ScheduledTask -TaskName "LinkedIn Daily Post" -Action $action -Trigger $trigger
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login fails | Check credentials, 2FA may be enabled |
| Post fails to publish | Session expired, re-authenticate |
| Content truncated | Keep posts under 3000 characters |
| Image upload fails | Check file size (<5MB), format (PNG/JPG) |

## Security Notes

- **Credentials**: Never store LinkedIn password in plain text
- **Session Files**: Store in secure location, never commit
- **Rate Limiting**: Max 3-5 posts per day to avoid restrictions
- **Approval Required**: Always require human approval before posting

## Demo Mode

Test without connecting to LinkedIn:

```bash
python scripts/linkedin_poster.py --action create --demo
```

Creates sample draft file:
```
AI_Employee_Vault/Pending_Approval/POST_DEMO_20260228_100000.md
```

## Example: Business Update Post

**AI Generated Content:**
```
🎉 Milestone Alert!

We just helped another client achieve 10x ROI through AI automation.

Their challenge: Manual invoice processing taking 15 hours/week
Our solution: Custom AI agent with 99% accuracy
Result: 15 hours saved weekly, zero processing errors

Ready to automate your business? DM for a free consultation!

#AI #Automation #BusinessGrowth #Innovation
```

**Approval Flow:**
1. File created: `Pending_Approval/POST_20260228_001.md`
2. Human reviews content
3. File moved to `Approved/`
4. Poster executes via Playwright
5. Confirmation logged to `Done/`

## Next Steps

After post is approved and published:
1. Monitor engagement (likes, comments, shares)
2. Respond to comments within 2 hours
3. Track lead generation metrics
4. Report results in weekly CEO briefing

---
*LinkedIn Poster v0.1 - Silver Tier Skill*
