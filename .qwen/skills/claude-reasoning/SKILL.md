---
name: claude-reasoning
description: |
  Claude Code reasoning loop that creates Plan.md files for complex tasks.
  Implements structured thinking: Read → Think → Plan → Execute → Review.
  Integrates with Company_Handbook.md for decision rules.
---

# Claude Reasoning Loop

Structured reasoning workflow for Claude Code agent.

## Overview

The reasoning loop transforms Claude Code from a chatbot into an autonomous agent:

1. **Read**: Gather information from vault folders
2. **Think**: Analyze situation using Company_Handbook rules
3. **Plan**: Create structured Plan.md with checkboxes
4. **Execute**: Take actions or request approval
5. **Review**: Verify completion and update Dashboard

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Action Files   │────▶│  Claude Code     │────▶│  Plan Files     │
│  Needs_Action/  │     │  (Reasoning)     │     │  Plans/         │
└─────────────────┘     └──────────────────┘     └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Company Handbook│
                       │  (Rules)         │
                       └──────────────────┘
```

## Plan.md Format

```markdown
---
created: 2026-02-28T10:00:00Z
source: EMAIL_DEMO001_20260228_005312.md
status: in_progress
priority: normal
estimated_steps: 5
completed_steps: 2
---

# Plan: Respond to Client Invoice Request

## Objective
Generate and send January invoice to client who requested via email.

## Context
- Client: John Doe (john@example.com)
- Request: January 2026 invoice
- Urgency: Normal
- Relationship: Existing client (auto-approve email)

## Steps
- [x] Read incoming email content
- [x] Identify client and request type
- [x] Check Company_Handbook for invoice rules
- [ ] Generate invoice PDF
- [ ] Create email draft
- [ ] Send email (auto-approved for existing client)
- [ ] Log action
- [ ] Move to Done

## Analysis
Client is requesting standard invoice. Per Company_Handbook:
- Invoice generation: Auto-approve
- Email to existing client: Auto-approve
- Payment tracking: Log to Accounting folder

## Actions Required
1. Generate invoice using Business_Goals rates
2. Send via email
3. Update Dashboard revenue

## Blockers
None

## Notes
- Client has been invoiced before
- Standard rate: $150/hour
- January hours: 10 hours = $1,500

---
*Created by Claude Code - AI Employee v0.1*
```

## Reasoning Process

### Step 1: Read

```python
# Orchestrator triggers Claude with context
prompt = """
You are processing action items for the AI Employee system.

Current folders to check:
- /Needs_Action/ (items requiring processing)
- /Pending_Approval/ (awaiting decisions)

Read all files and determine next actions.
"""
```

### Step 2: Think

Claude analyzes using Company_Handbook rules:

```markdown
# Company_Handbook.md Rules Applied

## Email Rules
- Known contact + no attachment → Auto-send OK
- New contact → Require approval
- Bulk email (>5) → Require approval

## Financial Rules
- Payment <$50 → Auto-categorize
- Payment >$100 → Require approval
- Invoice generation → Auto-approve

## Current Situation
- Sender: john@example.com (known contact)
- Request: Invoice (standard operation)
- Decision: Auto-approve email send
```

### Step 3: Plan

Create structured Plan.md:

```python
def create_plan(source_file: Path, objective: str, steps: list) -> Path:
    """Create Plan.md file."""
    plans_folder = Path('Plans')
    filename = f"PLAN_{source_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = plans_folder / filename
    
    steps_md = '\n'.join(f'- [ ] {step}' for step in steps)
    
    content = f"""---
created: {datetime.now().isoformat()}
source: {source_file.name}
status: analyzing
---

# Plan: {objective}

## Steps
{steps_md}

## Analysis
<!-- Claude fills this in -->

## Actions Required
<!-- Claude fills this in -->
"""
    
    filepath.write_text(content)
    return filepath
```

### Step 4: Execute

Claude executes based on approval rules:

```python
# Auto-approved action
if action_type == 'email' and recipient in known_contacts:
    send_email(recipient, subject, body)
    update_plan_status(filepath, 'completed')

# Requires approval
elif requires_approval(action_type, details):
    create_approval_request(action_type, details)
    update_plan_status(filepath, 'pending_approval')
```

### Step 5: Review

Verify completion:

```python
def review_completion(plan_file: Path) -> dict:
    """Review plan completion status."""
    content = plan_file.read_text()
    
    # Count checkboxes
    total = len(re.findall(r'\[- [ x]\]', content))
    completed = len(re.findall(r'\[- [x]\]', content))
    
    return {
        'total_steps': total,
        'completed_steps': completed,
        'percent_complete': (completed / total * 100) if total > 0 else 0,
        'status': 'complete' if completed == total else 'in_progress'
    }
```

## Integration with Orchestrator

```python
class Orchestrator:
    def trigger_claude_reasoning(self, action_file: Path):
        """Trigger Claude reasoning loop."""
        plan_file = self.create_plan_template(action_file)
        
        prompt = f"""
Process this action item following the reasoning loop:

1. READ: Review the action file content
2. THINK: Apply Company_Handbook rules
3. PLAN: Update the plan file with steps
4. EXECUTE: Take action or create approval request
5. REVIEW: Verify and update status

Action File: {action_file.name}
Plan File: {plan_file.name}

Company Handbook: {self.vault_path / 'Company_Handbook.md'}
"""
        
        # Run Claude Code
        result = self.run_claude(prompt)
        
        # Update plan with Claude's output
        self.update_plan(plan_file, result)
```

## Ralph Wiggum Loop (Persistence)

For multi-step tasks that require iteration:

```bash
# Ralph Wiggum pattern keeps Claude working until complete
/ralph-loop "Process all files in /Needs_Action" \
  --completion-check "Move to Done when complete" \
  --max-iterations 10
```

### How It Works

1. Claude processes action file
2. Claude tries to exit
3. Stop hook checks: Is file in Done?
4. If NO → Re-inject prompt with previous output
5. Repeat until file moved to Done or max iterations

## Example: Complete Workflow

### Input: WhatsApp Invoice Request

```
Needs_Action/WHATSAPP_client_20260228_100000.md
```

### Claude Output: Plan Created

```
Plans/PLAN_WHATSAPP_client_20260228_100000.md
```

### Plan Content (Claude Generated)

```markdown
# Plan: Process Invoice Request

## Objective
Generate and send invoice for client who requested via WhatsApp.

## Steps
- [x] Read WhatsApp message
- [x] Identify client: John Doe
- [x] Check invoice rate: $1,500/month
- [ ] Generate invoice PDF
- [ ] Create approval request (new client)
- [ ] Wait for approval
- [ ] Send email
- [ ] Log transaction

## Analysis
Client is new (first invoice). Per Company_Handbook:
- Invoice generation: Auto-approve
- Email to new client: Require approval

## Actions Required
1. Generate invoice PDF
2. Create approval request for email send
3. Execute after approval
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Plan not created | Check Claude Code installation |
| Steps not updating | Ensure file write permissions |
| Loop not terminating | Check completion criteria |
| Approval not triggered | Review Company_Handbook thresholds |

## Best Practices

1. **Clear Objectives**: One sentence describing goal
2. **Actionable Steps**: Each step should be doable
3. **Progress Tracking**: Update checkboxes as completed
4. **Blockers Noted**: Document what's preventing progress
5. **Status Current**: Keep status field updated

---
*Claude Reasoning Loop v0.1 - Silver Tier Skill*
