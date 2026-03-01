---
name: task-scheduler
description: |
  Task scheduling via cron (Linux/Mac) or Task Scheduler (Windows).
  Automates daily briefings, periodic checks, and scheduled operations.
  Integrates with orchestrator for time-based triggers.
---

# Task Scheduler

Schedule automated tasks using system schedulers.

## Overview

The Task Scheduler enables time-based automation:
- Daily CEO Briefings at 8:00 AM
- Weekly business reviews on Mondays
- Hourly watcher health checks
- Monthly subscription audits

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  System         │────▶│  Orchestrator    │────▶│  AI Employee    │
│  Scheduler      │     │  (Trigger)       │     │  (Action)       │
│  (cron/Task)    │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Quick Reference

### Linux/Mac (cron)

```bash
# Edit crontab
crontab -e

# Daily briefing at 8 AM
0 8 * * * cd /path/to/project && python scripts/orchestrator.py --action daily-briefing

# Hourly health check
0 * * * * cd /path/to/project && python scripts/orchestrator.py --action health-check

# Weekly review on Monday 7 AM
0 7 * * 1 cd /path/to/project && python scripts/orchestrator.py --action weekly-review

# Monthly audit on 1st day
0 9 1 * * cd /path/to/project && python scripts/orchestrator.py --action monthly-audit
```

### Windows (Task Scheduler)

```powershell
# Create scheduled task - Daily Briefing
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "scripts/orchestrator.py --action daily-briefing"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -TaskName "AI Employee Daily Briefing" `
  -Action $action -Trigger $trigger -Description "Generate daily CEO briefing"

# Create scheduled task - Hourly Check
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "scripts/orchestrator.py --action health-check"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
  -RepetitionInterval (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName "AI Employee Health Check" `
  -Action $action -Trigger $trigger

# List scheduled tasks
Get-ScheduledTask -TaskName "AI Employee*"

# Remove scheduled task
Unregister-ScheduledTask -TaskName "AI Employee Daily Briefing" -Confirm
```

## Cron Syntax

```
* * * * * command
│ │ │ │ │
│ │ │ │ └─ Day of week (0-7, Sunday=0 or 7)
│ │ │ └─── Month (1-12)
│ │ └───── Day of month (1-31)
│ └─────── Hour (0-23)
└───────── Minute (0-59)
```

### Common Patterns

| Pattern | Description |
|---------|-------------|
| `0 * * * *` | Every hour |
| `0 8 * * *` | Daily at 8 AM |
| `0 8 * * 1` | Every Monday at 8 AM |
| `0 8 1 * *` | First of every month at 8 AM |
| `*/15 * * * *` | Every 15 minutes |
| `0 8-18 * * *` | Every hour from 8 AM to 6 PM |

## Scheduled Tasks

### Daily Briefing (8:00 AM)

```bash
0 8 * * * cd /path/to/AI-Employee && python scripts/orchestrator.py --action daily-briefing >> logs/daily_briefing.log 2>&1
```

**What it does:**
1. Reviews yesterday's completed tasks
2. Summarizes revenue/expenses
3. Identifies bottlenecks
4. Lists today's deadlines
5. Writes Briefings/YYYY-MM-DD_Daily_Briefing.md

### Weekly Review (Monday 7:00 AM)

```bash
0 7 * * 1 cd /path/to/AI-Employee && python scripts/orchestrator.py --action weekly-review >> logs/weekly_review.log 2>&1
```

**What it does:**
1. Analyzes past week's performance
2. Calculates revenue vs targets
3. Reviews subscription costs
4. Generates CEO Briefing
5. Updates Business_Goals.md

### Health Check (Hourly)

```bash
0 * * * * cd /path/to/AI-Employee && python scripts/orchestrator.py --action health-check >> logs/health.log 2>&1
```

**What it does:**
1. Checks watcher processes running
2. Verifies vault accessibility
3. Checks for stuck approvals
4. Restarts failed processes
5. Alerts on critical issues

### Monthly Audit (1st of Month, 9:00 AM)

```bash
0 9 1 * * cd /path/to/AI-Employee && python scripts/orchestrator.py --action monthly-audit >> logs/monthly_audit.log 2>&1
```

**What it does:**
1. Reviews all transactions
2. Audits subscription usage
3. Categorizes expenses
4. Generates monthly report
5. Updates quarterly goals

## Python Scheduler Script

```python
"""
scheduler_setup.py - Configure scheduled tasks
"""
import platform
import subprocess
from pathlib import Path

def setup_cron_jobs(project_path: str):
    """Setup cron jobs for Linux/Mac."""
    jobs = [
        "0 8 * * * cd {} && python scripts/orchestrator.py --action daily-briefing".format(project_path),
        "0 7 * * 1 cd {} && python scripts/orchestrator.py --action weekly-review".format(project_path),
        "0 * * * * cd {} && python scripts/orchestrator.py --action health-check".format(project_path),
        "0 9 1 * * cd {} && python scripts/orchestrator.py --action monthly-audit".format(project_path),
    ]
    
    # Get current crontab
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    current = result.stdout if result.returncode == 0 else ""
    
    # Add new jobs (avoid duplicates)
    for job in jobs:
        if job not in current:
            current += f"\n{job}"
    
    # Install new crontab
    proc = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE)
    proc.communicate(current.encode())
    
    print("Cron jobs installed!")

def setup_windows_tasks(project_path: str, python_path: str = "python"):
    """Setup Windows Task Scheduler tasks."""
    tasks = [
        {
            "name": "AI Employee Daily Briefing",
            "trigger": "-Daily -At 8am",
            "action": f"-Execute \"{python_path}\" -Argument \"scripts/orchestrator.py --action daily-briefing\""
        },
        {
            "name": "AI Employee Weekly Review",
            "trigger": "-Weekly -At 7am -DaysOfWeek Monday",
            "action": f"-Execute \"{python_path}\" -Argument \"scripts/orchestrator.py --action weekly-review\""
        },
        {
            "name": "AI Employee Health Check",
            "trigger": "-Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)",
            "action": f"-Execute \"{python_path}\" -Argument \"scripts/orchestrator.py --action health-check\""
        }
    ]
    
    for task in tasks:
        cmd = f"""
$action = New-ScheduledTaskAction {task['action']}
$trigger = New-ScheduledTaskTrigger {task['trigger']}
Register-ScheduledTask -TaskName "{task['name']}" -Action $action -Trigger $trigger
"""
        print(f"Creating task: {task['name']}")
        # Execute PowerShell command
        subprocess.run(['powershell', '-Command', cmd])

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--setup', choices=['cron', 'windows'], help='Setup scheduler')
    parser.add_argument('--path', default='.', help='Project path')
    args = parser.parse_args()
    
    if args.setup == 'cron':
        setup_cron_jobs(args.path)
    elif args.setup == 'windows':
        setup_windows_tasks(args.path)
```

## Orchestrator Integration

```python
class Orchestrator:
    def run_scheduled_action(self, action: str):
        """Execute a scheduled action."""
        self.logger.info(f'Running scheduled action: {action}')
        
        if action == 'daily-briefing':
            self.generate_daily_briefing()
        elif action == 'weekly-review':
            self.generate_weekly_review()
        elif action == 'health-check':
            self.perform_health_check()
        elif action == 'monthly-audit':
            self.perform_monthly_audit()
    
    def generate_daily_briefing(self):
        """Generate daily CEO briefing."""
        briefings = self.vault_path / 'Briefings'
        briefings.mkdir(parents=True, exist_ok=True)
        
        today = datetime.now().strftime('%Y-%m-%d')
        filepath = briefings / f'{today}_Daily_Briefing.md'
        
        # Generate briefing content
        content = self._compile_briefing_content(period='daily')
        filepath.write_text(content)
        
        self.logger.info(f'Daily briefing created: {filepath.name}')
```

## Logging & Monitoring

### Log File Location

```
logs/
├── daily_briefing.log
├── weekly_review.log
├── health.log
└── monthly_audit.log
```

### Log Rotation

```bash
# Add to crontab for log rotation
0 0 * * * find /path/to/logs -name "*.log" -mtime +30 -delete
```

### Health Check Output

```json
{
  "timestamp": "2026-02-28T10:00:00Z",
  "status": "healthy",
  "watchers": {
    "gmail": "running",
    "whatsapp": "running",
    "filesystem": "running"
  },
  "orchestrator": "running",
  "pending_approvals": 2,
  "last_briefing": "2026-02-28T08:00:00Z"
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task not running | Check scheduler logs, verify paths |
| Python not found | Use absolute path to python executable |
| Permission denied | Run scheduler with appropriate permissions |
| Task runs but fails | Check script output logs |

## Best Practices

1. **Use Absolute Paths**: Avoid path resolution issues
2. **Log Everything**: Capture stdout and stderr
3. **Set Timezone**: Ensure consistent timezone
4. **Test Manually**: Run commands manually before scheduling
5. **Monitor Health**: Set up alerts for failed tasks

---
*Task Scheduler v0.1 - Silver Tier Skill*
