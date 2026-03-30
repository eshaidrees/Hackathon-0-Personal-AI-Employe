# Ralph Wiggum Loop Skill

## Purpose
Autonomous multi-step task completion using the Ralph Wiggum pattern. Keeps Claude Code working until tasks are complete by intercepting exit attempts and re-injecting prompts.

## Capabilities
- Keep Claude Code working autonomously
- Configurable completion criteria
- Automatic iteration with context
- Blocked task detection
- State persistence across iterations
- Task statistics and tracking
- Automatic cleanup of old states

## Files
- `scripts/ralph_wiggum_loop.py` - Main Ralph Wiggum loop implementation

## Usage

### Run Autonomous Task
```bash
# Run task with default settings
python scripts/ralph_wiggum_loop.py \
  --vault ../AI_Employee_Vault \
  --task-id process_invoices \
  --prompt "Process all pending invoices and send them" \
  --max-iterations 10
```

### Demo Mode
```bash
# Test the Ralph Wiggum loop
python scripts/ralph_wiggum_loop.py \
  --vault ../AI_Employee_Vault \
  --task-id demo_task \
  --prompt "This is a demo task" \
  --demo
```

## Completion Criteria

The loop checks for task completion using these criteria:

### File Movement
```json
{
  "file_moved_to_done": "invoice_123.md"
}
```
Task complete when file is moved to `Done/` folder.

### File Content
```json
{
  "file_contains": {
    "path": "Plans/PLAN_*.md",
    "text": "status: completed"
  }
}
```
Task complete when file contains specific text.

### Folder Empty
```json
{
  "folder_empty": "Needs_Action"
}
```
Task complete when folder is empty.

### Output Promise
```json
{
  "output_promise": "TASK_COMPLETE"
}
```
Task complete when Claude outputs the promise string.

### Plan Status
```json
{
  "plan_status": "PLAN_invoice_123.md"
}
```
Task complete when plan is marked completed.

## Python API

```python
from ralph_wiggum_loop import RalphWiggumLoop

# Initialize
loop = RalphWiggumLoop(
    vault_path='../AI_Employee_Vault',
    max_iterations=10
)

# Define completion criteria
completion_criteria = {
    'file_moved_to_done': 'invoice_123.md',
    'output_promise': 'TASK_COMPLETE'
}

# Run loop
final_state = loop.run_loop(
    task_id='process_invoices',
    prompt='Process all pending invoices',
    completion_criteria=completion_criteria,
    on_iteration=lambda state: print(f"Iteration {state['iteration']}")
)

# Check result
if final_state['status'] == 'completed':
    print(f"Task completed: {final_state['completion_reason']}")
elif final_state['status'] == 'failed':
    print(f"Task failed: {final_state['failure_reason']}")
elif final_state['status'] == 'blocked':
    print(f"Task blocked: {final_state['blocked_reason']}")
```

## Task State Format

```json
{
  "task_id": "process_invoices",
  "created": "2026-03-14T10:30:00",
  "updated": "2026-03-14T10:35:00",
  "prompt": "Process all pending invoices",
  "iteration": 3,
  "status": "in_progress",
  "completion_criteria": {
    "file_moved_to_done": "invoice_123.md"
  },
  "attempts": [
    {
      "iteration": 1,
      "output": "Searching for invoices..."
    },
    {
      "iteration": 2,
      "output": "Found 3 invoices to process"
    }
  ],
  "last_output": "Processing invoice 3 of 3",
  "blocked_reason": null
}
```

## Configuration

### Environment Variables
```bash
# Claude Code command
CLAUDE_COMMAND=claude

# Maximum iterations
MAX_CLAUDE_ITERATIONS=10

# Dry run mode
DRY_RUN=true

# Vault path
VAULT_PATH=/path/to/AI_Employee_Vault
```

## Workflow

```
1. User creates task with prompt
   ↓
2. Ralph Wiggum Loop creates state file
   ↓
3. Claude Code runs with prompt
   ↓
4. Claude produces output
   ↓
5. Loop checks completion criteria
   ↓
6. If complete → Task done
   ↓
7. If blocked → Report blocking reason
   ↓
8. If not complete → Generate next prompt
   ↓
9. Loop back to step 3
   ↓
10. Max iterations → Task failed
```

## Enhanced Prompt Building

Each iteration, Claude receives context:

```
You are in an autonomous loop (Ralph Wiggum pattern) working on task: {task_id}

ORIGINAL PROMPT:
{original_prompt}

CURRENT ITERATION: {iteration}/{max_iterations}

PREVIOUS OUTPUT:
{last_output}

INSTRUCTIONS:
1. Review the previous output
2. Check if the task is complete based on completion criteria
3. If not complete, take the next action
4. If complete, output "TASK_COMPLETE" and explain what was done
5. If blocked (need approval, waiting for external), explain what's blocking

COMPLETION CRITERIA:
{completion_criteria}

Remember: Keep working until the task is fully complete. Don't give up early!
```

## Blocked Task Detection

Tasks are blocked when:

### Pending Approval
```
Blocked: Waiting for approval: ODOO_APPROVAL_create_invoice_20260314.md
```

### External Input Required
```
Blocked: Waiting for external: EMAIL_response_needed.md
```

### File in Needs_Action
```
Blocked: File requires attention: Needs_Action/WHATSAPP_urgent.md
```

## Statistics

```bash
# Get loop statistics
python scripts/ralph_wiggum_loop.py \
  --vault ../AI_Employee_Vault \
  --task-id stats \
  --prompt "Show statistics"
```

### Statistics Output
```
Loop Statistics:
  Total Tasks: 15
  Completed: 12
  Failed: 2
  Blocked: 1
  In Progress: 0
  Average Iterations: 3.5
```

## State File Management

### Location
```
AI_Employee_Vault/
└── Logs/
    └── ralph_state/
        ├── process_invoices.json
        ├── send_replies.json
        └── demo_task.json
```

### Cleanup Old States
```python
from ralph_wiggum_loop import RalphWiggumLoop

loop = RalphWiggumLoop(vault_path='../AI_Employee_Vault')
removed = loop.cleanup_old_states(days=30)
print(f'Cleaned up {removed} old state files')
```

## Example Tasks

### Process Emails
```bash
python scripts/ralph_wiggum_loop.py \
  --vault ../AI_Employee_Vault \
  --task-id process_emails \
  --prompt "Read all emails in Needs_Action, draft responses, and move to Done" \
  --max-iterations 10 \
  --completion-criteria '{"folder_empty": "Needs_Action"}'
```

### Create Social Posts
```bash
python scripts/ralph_wiggum_loop.py \
  --vault ../AI_Employee_Vault \
  --task-id create_posts \
  --prompt "Create LinkedIn posts for this week's business updates" \
  --max-iterations 5
```

### Generate Invoices
```bash
python scripts/ralph_wiggum_loop.py \
  --vault ../AI_Employee_Vault \
  --task-id generate_invoices \
  --prompt "Generate invoices for all unpaid clients" \
  --completion-criteria '{"output_promise": "TASK_COMPLETE"}'
```

## Troubleshooting

### Max Iterations Reached
- Task may be too complex
- Increase `--max-iterations`
- Break task into smaller subtasks
- Review completion criteria

### Task Blocked
- Check for pending approvals
- Review `blocked_reason` in state file
- Move approval files to Approved/
- Provide required external input

### Claude Not Found
- Verify `CLAUDE_COMMAND` in `.env`
- Check Claude Code is installed
- Ensure PATH includes Claude

### State File Corrupted
- Delete corrupted state file
- Restart task with new task_id
- Check disk space and permissions

---

*Skill Version: 1.0*
*AI Employee v0.3 - Gold Tier*
