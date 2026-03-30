"""
Ralph Wiggum Loop - Autonomous Multi-Step Task Completion
Stop hook pattern that keeps Claude Code working until tasks are complete
"""
import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Callable
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RalphWiggumLoop:
    """
    Ralph Wiggum Loop for autonomous task completion.
    Keeps Claude Code working until a task is complete by intercepting exit attempts.
    
    Based on: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
    """

    def __init__(self, vault_path: str, max_iterations: int = 10):
        """
        Initialize Ralph Wiggum Loop.

        Args:
            vault_path: Path to the Obsidian vault root
            max_iterations: Maximum loop iterations before giving up
        """
        self.vault_path = Path(vault_path).resolve()
        self.max_iterations = max_iterations

        # Folder paths
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.state_dir = self.logs_dir = self.vault_path / 'Logs' / 'ralph_state'

        # Ensure directories exist
        for folder in [self.state_dir, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.claude_command = os.getenv('CLAUDE_COMMAND', 'claude')
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'

        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('RalphWiggumLoop')

    def create_task_state(self, task_id: str, prompt: str, 
                          completion_criteria: dict = None) -> Path:
        """
        Create a task state file for tracking progress.

        Args:
            task_id: Unique task identifier
            prompt: Original prompt/instruction
            completion_criteria: Criteria for task completion

        Returns:
            Path to state file
        """
        state_file = self.state_dir / f'{task_id}.json'

        state = {
            'task_id': task_id,
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat(),
            'prompt': prompt,
            'iteration': 0,
            'status': 'pending',  # pending, in_progress, completed, failed
            'completion_criteria': completion_criteria or {},
            'attempts': [],
            'last_output': None,
            'blocked_reason': None
        }

        state_file.write_text(json.dumps(state, indent=2), encoding='utf-8')
        self.logger.info(f'Created task state: {task_id}')
        return state_file

    def load_task_state(self, task_id: str) -> Optional[dict]:
        """Load task state from file."""
        state_file = self.state_dir / f'{task_id}.json'
        if not state_file.exists():
            return None

        return json.loads(state_file.read_text(encoding='utf-8'))

    def save_task_state(self, state: dict):
        """Save task state to file."""
        state_file = self.state_dir / f"{state['task_id']}.json"
        state['updated'] = datetime.now().isoformat()
        state_file.write_text(json.dumps(state, indent=2), encoding='utf-8')

    def check_completion(self, state: dict) -> tuple:
        """
        Check if task completion criteria are met.

        Args:
            state: Task state dict

        Returns:
            Tuple of (is_complete, reason)
        """
        criteria = state.get('completion_criteria', {})

        # Check file movement criteria (task moved to Done)
        if 'file_moved_to_done' in criteria:
            expected_file = criteria['file_moved_to_done']
            if (self.done / expected_file).exists():
                return True, 'File moved to Done folder'

        # Check file content criteria
        if 'file_contains' in criteria:
            file_path = self.vault_path / criteria['file_contains']['path']
            search_text = criteria['file_contains']['text']
            if file_path.exists() and search_text in file_path.read_text():
                return True, f'File contains expected text: {search_text}'

        # Check folder is empty criteria
        if 'folder_empty' in criteria:
            folder_name = criteria['folder_empty']
            folder = self.vault_path / folder_name
            if not folder.exists() or len(list(folder.glob('*.md'))) == 0:
                return True, f'Folder {folder_name} is empty'

        # Check output promise criteria
        if 'output_promise' in criteria:
            promise = criteria['output_promise']
            last_output = state.get('last_output', '')
            if promise in last_output:
                return True, f'Output promise detected: {promise}'

        # Check plan status criteria
        if 'plan_status' in criteria:
            plan_file = self.plans / criteria['plan_status']
            if plan_file.exists():
                content = plan_file.read_text()
                if 'status: completed' in content or 'status:done' in content:
                    return True, 'Plan marked as completed'

        # Default: not complete yet
        return False, 'Completion criteria not met'

    def run_loop(self, task_id: str, prompt: str,
                 completion_criteria: dict = None,
                 on_iteration: Callable = None) -> dict:
        """
        Run the Ralph Wiggum loop until task is complete.

        Args:
            task_id: Unique task identifier
            prompt: Initial prompt for Claude
            completion_criteria: Criteria for determining completion
            on_iteration: Callback function called each iteration

        Returns:
            Final task state
        """
        self.logger.info(f'Starting Ralph Wiggum Loop for task: {task_id}')

        # Create initial state
        state = self.create_task_state(task_id, prompt, completion_criteria)
        state = json.loads(state.read_text())

        # Create initial plan file
        self._create_initial_plan(task_id, prompt)

        while state['iteration'] < self.max_iterations:
            state['iteration'] += 1
            state['status'] = 'in_progress'

            self.logger.info(f'Iteration {state["iteration"]}/{self.max_iterations}')

            # Run Claude Code
            output = self._run_claude(prompt, state)
            state['last_output'] = output

            # Call iteration callback if provided
            if on_iteration:
                on_iteration(state)

            # Check completion
            is_complete, reason = self.check_completion(state)
            
            if is_complete:
                state['status'] = 'completed'
                state['completed_at'] = datetime.now().isoformat()
                state['completion_reason'] = reason
                self.save_task_state(state)
                self.logger.info(f'Task completed: {reason}')
                return state

            # Check if blocked (needs approval, waiting for external)
            blocked, block_reason = self._check_blocked(state)
            if blocked:
                state['status'] = 'blocked'
                state['blocked_reason'] = block_reason
                self.save_task_state(state)
                self.logger.info(f'Task blocked: {block_reason}')
                return state

            # Update prompt for next iteration based on output
            prompt = self._generate_next_prompt(state, output)

            # Save state
            self.save_task_state(state)

            # Small delay between iterations
            import time
            time.sleep(1)

        # Max iterations reached
        state['status'] = 'failed'
        state['failure_reason'] = f'Max iterations ({self.max_iterations}) reached'
        self.save_task_state(state)
        self.logger.warning(f'Task failed: {state["failure_reason"]}')
        return state

    def _create_initial_plan(self, task_id: str, prompt: str):
        """Create initial plan file for the task."""
        plan_file = self.plans / f'PLAN_{task_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'

        content = f'''---
created: {datetime.now().isoformat()}
task_id: {task_id}
status: in_progress
source: ralph_wiggum_loop
---

# Plan: {task_id}

## Objective
{prompt}

## Steps
- [ ] Analyze requirements
- [ ] Execute tasks
- [ ] Verify completion
- [ ] Move to Done

## Progress
<!-- Claude will update this section -->

---
*Created by Ralph Wiggum Loop - AI Employee v0.3*
'''

        plan_file.write_text(content, encoding='utf-8')

    def _run_claude(self, prompt: str, state: dict) -> str:
        """Run Claude Code with the given prompt."""
        if self.dry_run:
            self.logger.info(f'[DRY RUN] Would run Claude with prompt: {prompt[:100]}...')
            return '[DRY RUN] Claude execution simulated'

        try:
            # Change to vault directory
            os.chdir(self.vault_path)

            # Build enhanced prompt
            enhanced_prompt = self._build_enhanced_prompt(prompt, state)

            # Run Claude Code
            result = subprocess.run(
                [self.claude_command, '--prompt', enhanced_prompt],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            output = result.stdout
            if result.stderr:
                self.logger.warning(f'Claude stderr: {result.stderr[:200]}')

            return output

        except subprocess.TimeoutExpired:
            self.logger.error('Claude Code timed out')
            return '[ERROR] Claude Code timeout'
        except FileNotFoundError:
            self.logger.error(f'Claude Code not found: {self.claude_command}')
            return f'[ERROR] Claude Code not found at {self.claude_command}'
        except Exception as e:
            self.logger.error(f'Error running Claude: {e}')
            return f'[ERROR] {str(e)}'

    def _build_enhanced_prompt(self, original_prompt: str, state: dict) -> str:
        """Build enhanced prompt with context and previous output."""
        context = f"""You are in an autonomous loop (Ralph Wiggum pattern) working on task: {state['task_id']}

ORIGINAL PROMPT:
{original_prompt}

CURRENT ITERATION: {state['iteration']}/{self.max_iterations}

PREVIOUS OUTPUT:
{state.get('last_output', 'None - first iteration')}

INSTRUCTIONS:
1. Review the previous output
2. Check if the task is complete based on completion criteria
3. If not complete, take the next action
4. If complete, output "TASK_COMPLETE" and explain what was done
5. If blocked (need approval, waiting for external), explain what's blocking

COMPLETION CRITERIA:
{json.dumps(state.get('completion_criteria', {}), indent=2)}

Remember: Keep working until the task is fully complete. Don't give up early!
"""
        return context

    def _generate_next_prompt(self, state: dict, last_output: str) -> str:
        """Generate prompt for next iteration."""
        return f"""Continue working on task {state['task_id']}.

Previous attempt output:
{last_output}

What still needs to be done? Take the next action.
"""

    def _check_blocked(self, state: dict) -> tuple:
        """Check if task is blocked and why."""
        # Check for pending approvals
        if self.pending_approval.exists():
            pending_files = list(self.pending_approval.glob('*.md'))
            if pending_files:
                return True, f'Waiting for approval: {pending_files[0].name}'

        # Check for files in needs_action that need external input
        if self.needs_action.exists():
            needs_action_files = list(self.needs_action.glob('*.md'))
            if needs_action_files:
                # Check if any are waiting for external
                for f in needs_action_files:
                    content = f.read_text()
                    if 'waiting for external' in content.lower():
                        return True, f'Waiting for external: {f.name}'

        return False, None

    def get_loop_statistics(self) -> dict:
        """Get statistics about Ralph Wiggum loops."""
        stats = {
            'total_tasks': 0,
            'completed': 0,
            'failed': 0,
            'blocked': 0,
            'in_progress': 0,
            'avg_iterations': 0,
            'total_iterations': 0
        }

        if not self.state_dir.exists():
            return stats

        states = []
        for state_file in self.state_dir.glob('*.json'):
            try:
                state = json.loads(state_file.read_text())
                states.append(state)
            except:
                continue

        stats['total_tasks'] = len(states)

        for state in states:
            status = state.get('status', 'unknown')
            if status == 'completed':
                stats['completed'] += 1
            elif status == 'failed':
                stats['failed'] += 1
            elif status == 'blocked':
                stats['blocked'] += 1
            elif status == 'in_progress':
                stats['in_progress'] += 1

            iterations = state.get('iteration', 0)
            stats['total_iterations'] += iterations

        if stats['completed'] > 0:
            stats['avg_iterations'] = stats['total_iterations'] / stats['total_tasks']

        return stats

    def cleanup_old_states(self, days: int = 30) -> int:
        """Clean up old task state files."""
        cutoff = datetime.now() - timedelta(days=days)
        removed = 0

        for state_file in self.state_dir.glob('*.json'):
            try:
                state = json.loads(state_file.read_text())
                updated = datetime.fromisoformat(state.get('updated', ''))
                if updated < cutoff:
                    state_file.unlink()
                    removed += 1
            except:
                continue

        self.logger.info(f'Cleaned up {removed} old state files')
        return removed


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Ralph Wiggum Loop')
    parser.add_argument(
        '--vault',
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--task-id',
        required=True,
        help='Unique task identifier'
    )
    parser.add_argument(
        '--prompt',
        required=True,
        help='Task prompt/instruction'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=10,
        help='Maximum iterations'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run in demo mode'
    )

    args = parser.parse_args()

    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()

    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        sys.exit(1)

    loop = RalphWiggumLoop(str(vault_path), args.max_iterations)

    if args.demo:
        print('Ralph Wiggum Loop Demo Mode')
        print(f'Vault: {vault_path}')
        print(f'Max Iterations: {loop.max_iterations}')

        # Create demo task
        state = loop.create_task_state(
            'demo_task',
            'This is a demo task for testing the Ralph Wiggum loop',
            {'output_promise': 'TASK_COMPLETE'}
        )
        print(f'\nCreated demo task state: {state}')

        # Show stats
        stats = loop.get_loop_statistics()
        print(f'\nLoop Statistics:')
        print(f'  Total Tasks: {stats["total_tasks"]}')
        print(f'  Completed: {stats["completed"]}')
        print(f'  Failed: {stats["failed"]}')

        return

    # Run loop with provided arguments
    completion_criteria = {'output_promise': 'TASK_COMPLETE'}

    print(f'Starting Ralph Wiggum Loop for task: {args.task_id}')
    print(f'Max iterations: {args.max_iterations}')
    print(f'Prompt: {args.prompt[:100]}...')

    final_state = loop.run_loop(args.task_id, args.prompt, completion_criteria)

    print(f'\nFinal Status: {final_state["status"]}')
    if final_state['status'] == 'completed':
        print(f'Completion Reason: {final_state["completion_reason"]}')
    elif final_state['status'] == 'failed':
        print(f'Failure Reason: {final_state["failure_reason"]}')
    elif final_state['status'] == 'blocked':
        print(f'Blocked Reason: {final_state["blocked_reason"]}')


if __name__ == '__main__':
    main()
