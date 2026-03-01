"""
Scheduler Setup - Configure scheduled tasks for AI Employee
Supports cron (Linux/Mac) and Task Scheduler (Windows)
"""
import platform
import subprocess
import sys
from pathlib import Path


def get_python_path():
    """Get absolute path to Python executable."""
    return sys.executable


def get_project_path():
    """Get absolute path to project directory."""
    return Path(__file__).parent.resolve()


def setup_cron_jobs():
    """Setup cron jobs for Linux/Mac."""
    python_path = get_python_path()
    project_path = get_project_path()
    
    jobs = [
        f"0 8 * * * cd {project_path} && {python_path} scripts/orchestrator.py --action daily-briefing >> {project_path}/logs/daily_briefing.log 2>&1",
        f"0 7 * * 1 cd {project_path} && {python_path} scripts/orchestrator.py --action weekly-review >> {project_path}/logs/weekly_review.log 2>&1",
        f"0 * * * * cd {project_path} && {python_path} scripts/orchestrator.py --action health-check >> {project_path}/logs/health.log 2>&1",
        f"0 9 1 * * cd {project_path} && {python_path} scripts/orchestrator.py --action monthly-audit >> {project_path}/logs/monthly_audit.log 2>&1",
    ]
    
    print("Setting up cron jobs...")
    print(f"Project path: {project_path}")
    print(f"Python path: {python_path}")
    
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
    
    print("\n✓ Cron jobs installed!")
    print("\nScheduled tasks:")
    for job in jobs:
        print(f"  {job[:80]}...")
    
    print("\nTo view crontab: crontab -l")
    print("To remove all: crontab -r")


def setup_windows_tasks():
    """Setup Windows Task Scheduler tasks."""
    python_path = get_python_path()
    project_path = get_project_path()
    
    tasks = [
        {
            "name": "AI_Employee_Daily_Briefing",
            "trigger": "-Daily -At 8am",
            "action": f"-Execute \"{python_path}\" -Argument \"scripts/orchestrator.py --action daily-briefing\"",
            "description": "Generate daily CEO briefing at 8 AM"
        },
        {
            "name": "AI_Employee_Weekly_Review",
            "trigger": "-Weekly -At 7am -DaysOfWeek Monday",
            "action": f"-Execute \"{python_path}\" -Argument \"scripts/orchestrator.py --action weekly-review\"",
            "description": "Generate weekly business review on Mondays"
        },
        {
            "name": "AI_Employee_Health_Check",
            "trigger": "-Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)",
            "action": f"-Execute \"{python_path}\" -Argument \"scripts/orchestrator.py --action health-check\"",
            "description": "Hourly health check of AI Employee system"
        }
    ]
    
    print("Setting up Windows Task Scheduler tasks...")
    print(f"Project path: {project_path}")
    print(f"Python path: {python_path}")
    
    for task in tasks:
        powershell_cmd = f"""
$action = New-ScheduledTaskAction {task['action']} -WorkingDirectory "{project_path}"
$trigger = New-ScheduledTaskTrigger {task['trigger']}
$principal = New-ScheduledTaskPrincipal -UserId "{subprocess.check_output(['whoami']).decode().strip()}" -LogonType Interactive -RunLevel Highest
Register-ScheduledTask -TaskName "{task['name']}" -Action $action -Trigger $trigger -Principal $principal -Description "{task['description']}"
"""
        
        print(f"\nCreating task: {task['name']}")
        try:
            result = subprocess.run(
                ['powershell', '-Command', powershell_cmd],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"  ✓ Task created successfully")
            else:
                print(f"  ✗ Error: {result.stderr}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\nTo view tasks: Open Task Scheduler → Task Scheduler Library")
    print("To remove: Unregister-ScheduledTask -TaskName \"TASK_NAME\"")


def list_scheduled_tasks():
    """List existing scheduled tasks."""
    system = platform.system()
    
    if system in ['Darwin', 'Linux']:
        print("Current cron jobs:")
        subprocess.run(['crontab', '-l'])
    else:
        print("Current AI Employee scheduled tasks:")
        subprocess.run(['powershell', '-Command', 'Get-ScheduledTask -TaskName "AI_Employee*" | Select-Object TaskName, State'])


def remove_all_tasks():
    """Remove all AI Employee scheduled tasks."""
    system = platform.system()
    
    if system in ['Darwin', 'Linux']:
        print("Removing all cron jobs...")
        subprocess.run(['crontab', '-r'])
        print("✓ All cron jobs removed")
    else:
        print("Removing AI Employee scheduled tasks...")
        tasks = ['AI_Employee_Daily_Briefing', 'AI_Employee_Weekly_Review', 'AI_Employee_Health_Check']
        for task in tasks:
            subprocess.run(['powershell', '-Command', f'Unregister-ScheduledTask -TaskName "{task}" -Confirm:$false'])
        print("✓ All AI Employee tasks removed")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee Scheduler Setup')
    parser.add_argument('action', choices=['setup', 'list', 'remove'], 
                       help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'setup':
        system = platform.system()
        if system in ['Darwin', 'Linux']:
            setup_cron_jobs()
        else:
            setup_windows_tasks()
    
    elif args.action == 'list':
        list_scheduled_tasks()
    
    elif args.action == 'remove':
        remove_all_tasks()


if __name__ == '__main__':
    main()
