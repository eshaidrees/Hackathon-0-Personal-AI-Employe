"""
Orchestrator - Master Process for AI Employee
Manages watchers, triggers Claude, handles approvals, and updates dashboard
"""
import os
import sys
import json
import shutil
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('orchestrator.log', encoding='utf-8')
    ]
)


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.
    Coordinates between watchers, Claude Code, and action execution.
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path).resolve()
        self.logger = logging.getLogger('Orchestrator')
        
        # Folder paths
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure all folders exist
        for folder in [self.inbox, self.needs_action, self.plans, 
                       self.pending_approval, self.approved, self.rejected, 
                       self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.claude_command = os.getenv('CLAUDE_COMMAND', 'claude')
        self.max_iterations = int(os.getenv('MAX_CLAUDE_ITERATIONS', '10'))
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        
        self.logger.info(f'Orchestrator initialized')
        self.logger.info(f'Vault: {self.vault_path}')
        self.logger.info(f'Dry Run Mode: {self.dry_run}')
    
    def count_files(self, folder: Path) -> int:
        """Count .md files in a folder."""
        if not folder.exists():
            return 0
        return len([f for f in folder.iterdir() if f.suffix == '.md' and not f.name.startswith('.')])
    
    def update_dashboard(self):
        """
        Update the Dashboard.md with current status.
        """
        self.logger.info('Updating Dashboard...')
        
        # Count items in each folder
        inbox_count = self.count_files(self.inbox)
        needs_action_count = self.count_files(self.needs_action)
        pending_approval_count = self.count_files(self.pending_approval)
        done_today = self.count_files(self.done)  # Simplified - would filter by date
        
        # Read current dashboard
        if self.dashboard.exists():
            content = self.dashboard.read_text(encoding='utf-8')
        else:
            content = "# AI Employee Dashboard\n\n"
        
        # Update quick status section
        status_update = f"""## Quick Status
- **Inbox Items**: {inbox_count}
- **Needs Action**: {needs_action_count}
- **Pending Approval**: {pending_approval_count}
- **Completed Today**: {done_today}
"""
        
        # Replace status section in content
        if '## Quick Status' in content:
            # Find the section and replace
            lines = content.split('\n')
            new_lines = []
            in_status = False
            for line in lines:
                if line.startswith('## Quick Status'):
                    in_status = True
                    new_lines.append(status_update.strip())
                elif in_status and line.startswith('---'):
                    in_status = False
                    new_lines.append('---')
                elif not in_status:
                    new_lines.append(line)
            content = '\n'.join(new_lines)
        else:
            content = status_update + '\n---\n' + content
        
        # Add timestamp
        content = content.replace(
            'last_updated:', 
            f'last_updated: {datetime.now().isoformat()}'
        ) if 'last_updated:' in content else f'---\nlast_updated: {datetime.now().isoformat()}\n---\n' + content
        
        self.dashboard.write_text(content, encoding='utf-8')
        self.logger.info('Dashboard updated')
    
    def process_needs_action(self):
        """
        Process all files in Needs_Action folder using Claude Code.
        Creates plans and moves files appropriately.
        """
        self.logger.info('Processing Needs_Action folder...')
        
        if not self.needs_action.exists():
            self.logger.info('Needs_Action folder is empty')
            return
        
        # Get all markdown files
        files = [f for f in self.needs_action.iterdir() if f.suffix == '.md' and not f.name.startswith('.')]
        
        if not files:
            self.logger.info('No files to process')
            return
        
        self.logger.info(f'Found {len(files)} files to process')
        
        for filepath in files:
            self.logger.info(f'Processing: {filepath.name}')
            
            # Read the file content
            content = filepath.read_text(encoding='utf-8')
            
            # Create a plan file for this item
            plan_filename = f"PLAN_{filepath.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            plan_path = self.plans / plan_filename
            
            # Initial plan template
            plan_content = f"""---
created: {datetime.now().isoformat()}
source: {filepath.name}
status: analyzing
---

# Plan: {filepath.stem}

## Objective
<!-- Claude will fill this in -->

## Steps
- [ ] Analyze the incoming item
- [ ] Determine required actions
- [ ] Execute or request approval

## Analysis
<!-- Claude will add analysis here -->

## Actions Required
<!-- Claude will list actions here -->

---
*Created by Orchestrator - AI Employee v0.1*
"""
            plan_path.write_text(plan_content, encoding='utf-8')
            
            # Trigger Claude Code to process
            self.trigger_claude(filepath, plan_path)
    
    def trigger_claude(self, action_file: Path, plan_file: Path):
        """
        Trigger Claude Code to process an action file.
        
        Args:
            action_file: Path to the action file in Needs_Action
            plan_file: Path to the associated plan file
        """
        self.logger.info(f'Triggering Claude Code for: {action_file.name}')
        
        # Create a prompt for Claude
        prompt = f"""You are processing an action item for the AI Employee system.

Action File: {action_file.name}
Plan File: {plan_file.name}

Please:
1. Read the action file content
2. Analyze what needs to be done
3. Update the plan file with:
   - Clear objective
   - Step-by-step actions
   - Identify if human approval is needed
4. Either:
   - Execute the action (if auto-approved per Company_Handbook)
   - Create approval request in Pending_Approval folder
   - Move to Done if complete

Follow the rules in Company_Handbook.md for approval thresholds.
"""
        
        if self.dry_run:
            self.logger.info(f'[DRY RUN] Would trigger Claude with prompt: {prompt[:200]}...')
            # In dry run, just update plan with placeholder
            current_plan = plan_file.read_text(encoding='utf-8')
            current_plan = current_plan.replace(
                '<!-- Claude will fill this in -->',
                'Analyze the action item and determine next steps (pending Claude execution)'
            )
            plan_file.write_text(current_plan, encoding='utf-8')
        else:
            # Actually trigger Claude Code
            try:
                # Change to vault directory
                os.chdir(self.vault_path)
                
                # Run Claude Code with the prompt
                result = subprocess.run(
                    [self.claude_command, '--prompt', prompt],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                self.logger.info(f'Claude output: {result.stdout[:500] if result.stdout else "No output"}')
                
                if result.stderr:
                    self.logger.warning(f'Claude stderr: {result.stderr[:200]}')
                
            except subprocess.TimeoutExpired:
                self.logger.error('Claude Code timed out')
            except FileNotFoundError:
                self.logger.error(f'Claude Code not found at: {self.claude_command}')
                self.logger.error('Make sure Claude Code is installed: npm install -g @anthropic/claude-code')
            except Exception as e:
                self.logger.error(f'Error triggering Claude: {e}')
    
    def check_approvals(self):
        """
        Check Approved folder for files ready to execute.
        """
        self.logger.info('Checking for approved actions...')
        
        if not self.approved.exists():
            return
        
        files = [f for f in self.approved.iterdir() if f.suffix == '.md' and not f.name.startswith('.')]
        
        for filepath in files:
            self.logger.info(f'Executing approved action: {filepath.name}')
            self.execute_approved_action(filepath)
    
    def execute_approved_action(self, filepath: Path):
        """
        Execute an approved action.
        
        Args:
            filepath: Path to approved action file
        """
        content = filepath.read_text(encoding='utf-8')
        
        # Parse the action type from frontmatter
        action_type = 'unknown'
        if 'type: email' in content:
            action_type = 'email'
        elif 'type: payment' in content:
            action_type = 'payment'
        elif 'type: social_post' in content:
            action_type = 'social'
        
        self.logger.info(f'Action type: {action_type}')
        
        if self.dry_run:
            self.logger.info(f'[DRY RUN] Would execute {action_type} action')
        else:
            # Execute based on action type
            # This would integrate with MCP servers for actual execution
            self.logger.info(f'Executing {action_type} action (MCP integration needed)')
        
        # Move to Done after execution
        dest = self.done / filepath.name
        shutil.move(str(filepath), str(dest))
        self.logger.info(f'Moved to Done: {dest.name}')
    
    def log_action(self, action_type: str, details: dict, status: str = 'success'):
        """
        Log an action to the daily log file.
        
        Args:
            action_type: Type of action
            details: Action details dict
            status: success/failure/pending
        """
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.json'
        
        # Load existing logs or create new
        if log_file.exists():
            logs = json.loads(log_file.read_text(encoding='utf-8'))
        else:
            logs = []
        
        # Add new log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'orchestrator',
            'parameters': details,
            'approval_status': 'auto',
            'result': status
        }
        logs.append(log_entry)
        
        # Save logs
        log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')
    
    def run_cycle(self):
        """
        Run one complete orchestration cycle.
        """
        self.logger.info('=== Starting Orchestration Cycle ===')
        
        try:
            # Update dashboard
            self.update_dashboard()
            
            # Process needs action
            self.process_needs_action()
            
            # Check and execute approvals
            self.check_approvals()
            
            # Update dashboard again
            self.update_dashboard()
            
            self.logger.info('=== Orchestration Cycle Complete ===')
            
        except Exception as e:
            self.logger.error(f'Error in orchestration cycle: {e}')
    
    def run_continuous(self, cycle_interval: int = 60):
        """
        Run orchestrator continuously.
        
        Args:
            cycle_interval: Seconds between cycles
        """
        import time
        
        self.logger.info(f'Starting continuous orchestration (interval: {cycle_interval}s)')
        
        while True:
            try:
                self.run_cycle()
            except Exception as e:
                self.logger.error(f'Cycle error: {e}')
            
            time.sleep(cycle_interval)


def main():
    """
    Main entry point for Orchestrator.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument(
        '--vault', 
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--interval', 
        type=int, 
        default=60,
        help='Cycle interval in seconds'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode (no actual actions)'
    )
    
    args = parser.parse_args()
    
    # Resolve vault path
    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()
    
    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        sys.exit(1)
    
    # Create orchestrator
    orchestrator = Orchestrator(str(vault_path))
    
    if args.dry_run:
        orchestrator.dry_run = True
    
    if args.once:
        orchestrator.run_cycle()
    else:
        orchestrator.run_continuous(args.interval)


if __name__ == '__main__':
    main()
