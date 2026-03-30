"""
Weekly Business and Accounting Audit
Generates comprehensive CEO Briefing with revenue, expenses, bottlenecks, and suggestions
"""
import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class WeeklyAudit:
    """
    Weekly Business and Accounting Audit Generator.
    Analyzes business performance and generates CEO Briefing.
    """

    def __init__(self, vault_path: str):
        """
        Initialize Weekly Audit.

        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path).resolve()
        self.logger = self._setup_logging()

        # Folder paths
        self.done = self.vault_path / 'Done'
        self.briefings = self.vault_path / 'Briefings'
        self.logs = self.vault_path / 'Logs'
        self.accounting = self.vault_path / 'Accounting'
        self.plans = self.vault_path / 'Plans'

        # Ensure folders exist
        for folder in [self.briefings, self.logs, self.accounting]:
            folder.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'

    def _setup_logging(self):
        """Setup logging."""
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger('WeeklyAudit')

    def get_week_date_range(self) -> tuple:
        """Get the date range for last week (Monday to Sunday)."""
        today = datetime.now()
        # Get last Monday
        last_monday = today - timedelta(days=today.weekday(), weeks=1)
        # Get last Sunday
        last_sunday = last_monday + timedelta(days=6)
        
        return last_monday, last_sunday

    def analyze_completed_tasks(self, start_date: datetime, end_date: datetime) -> dict:
        """
        Analyze completed tasks from last week.

        Args:
            start_date: Week start date
            end_date: Week end date

        Returns:
            Dict with task analysis
        """
        analysis = {
            'total_completed': 0,
            'by_type': {},
            'tasks': []
        }

        if not self.done.exists():
            return analysis

        # Scan Done folder for files from last week
        for f in self.done.glob('*.md'):
            try:
                # Try to parse date from filename or content
                content = f.read_text(encoding='utf-8')
                
                # Extract type from frontmatter
                task_type = 'unknown'
                if 'type: email' in content:
                    task_type = 'email'
                elif 'type: whatsapp' in content:
                    task_type = 'whatsapp'
                elif 'type: linkedin' in content:
                    task_type = 'linkedin'
                elif 'type: twitter' in content:
                    task_type = 'twitter'
                elif 'type: invoice' in content:
                    task_type = 'invoice'

                analysis['total_completed'] += 1
                analysis['by_type'][task_type] = analysis['by_type'].get(task_type, 0) + 1
                
                analysis['tasks'].append({
                    'file': f.name,
                    'type': task_type,
                    'completed_date': f.stat().st_mtime
                })

            except Exception as e:
                self.logger.debug(f'Error analyzing file {f.name}: {e}')

        return analysis

    def analyze_financials(self) -> dict:
        """
        Analyze financial data from Accounting folder and Odoo (if available).

        Returns:
            Dict with financial summary
        """
        financials = {
            'revenue': 0.0,
            'expenses': 0.0,
            'profit': 0.0,
            'invoices_sent': 0,
            'invoices_paid': 0,
            'pending_amount': 0.0,
            'transactions': []
        }

        # Try to read accounting files
        if self.accounting.exists():
            for f in self.accounting.glob('*.md'):
                try:
                    content = f.read_text(encoding='utf-8')
                    
                    # Simple parsing for revenue/expense markers
                    for line in content.split('\n'):
                        if 'revenue:' in line.lower() or 'income:' in line.lower():
                            try:
                                amount = float(line.split(':')[1].strip().replace('$', ''))
                                financials['revenue'] += amount
                            except:
                                pass
                        elif 'expense:' in line.lower() or 'cost:' in line.lower():
                            try:
                                amount = float(line.split(':')[1].strip().replace('$', ''))
                                financials['expenses'] += amount
                            except:
                                pass
                except Exception as e:
                    self.logger.debug(f'Error reading accounting file {f.name}: {e}')

        # Try Odoo integration if available
        try:
            from odoo_mcp_server import OdooMCP
            odoo = OdooMCP()
            
            if not self.dry_run:
                if odoo.authenticate():
                    # Get account summary
                    summary = odoo.get_account_summary()
                    financials['odoo_summary'] = summary
                    
                    # Get invoices
                    invoices = odoo.get_invoices(limit=50)
                    financials['invoices_sent'] = len([i for i in invoices if i.get('move_type') == 'out_invoice'])
                    financials['invoices_paid'] = len([i for i in invoices if i.get('state') == 'paid'])
                    
                    self.logger.info('Odoo integration successful')
        except Exception as e:
            self.logger.debug(f'Odoo integration not available: {e}')

        financials['profit'] = financials['revenue'] - financials['expenses']

        return financials

    def identify_bottlenecks(self, task_analysis: dict, financials: dict) -> list:
        """
        Identify business bottlenecks and issues.

        Args:
            task_analysis: Task analysis dict
            financials: Financial summary dict

        Returns:
            List of identified bottlenecks
        """
        bottlenecks = []

        # Check for low task completion
        if task_analysis['total_completed'] < 5:
            bottlenecks.append({
                'type': 'low_activity',
                'severity': 'medium',
                'description': f'Only {task_analysis["total_completed"]} tasks completed this week',
                'suggestion': 'Review pipeline and prioritize lead generation'
            })

        # Check for revenue gaps
        if financials['revenue'] == 0:
            bottlenecks.append({
                'type': 'no_revenue',
                'severity': 'high',
                'description': 'No revenue recorded this week',
                'suggestion': 'Follow up on pending invoices and proposals'
            })

        # Check for high expenses
        if financials['expenses'] > financials['revenue'] * 0.5 and financials['revenue'] > 0:
            bottlenecks.append({
                'type': 'high_expenses',
                'severity': 'medium',
                'description': f'Expenses ({financials["expenses"]:.2f}) exceed 50% of revenue',
                'suggestion': 'Review and optimize cost structure'
            })

        # Check for unpaid invoices
        if financials['invoices_sent'] > financials['invoices_paid']:
            unpaid_count = financials['invoices_sent'] - financials['invoices_paid']
            bottlenecks.append({
                'type': 'unpaid_invoices',
                'severity': 'medium',
                'description': f'{unpaid_count} invoices sent but not yet paid',
                'suggestion': 'Send payment reminders to outstanding clients'
            })

        return bottlenecks

    def generate_suggestions(self, bottlenecks: list, task_analysis: dict, 
                            financials: dict) -> list:
        """
        Generate proactive business suggestions.

        Args:
            bottlenecks: List of identified bottlenecks
            task_analysis: Task analysis dict
            financials: Financial summary dict

        Returns:
            List of suggestions
        """
        suggestions = []

        # Add suggestions from bottlenecks
        for bottleneck in bottlenecks:
            if 'suggestion' in bottleneck:
                suggestions.append({
                    'priority': 'high' if bottleneck['severity'] == 'high' else 'medium',
                    'category': 'issue_resolution',
                    'suggestion': bottleneck['suggestion'],
                    'related_to': bottleneck['type']
                })

        # Subscription audit suggestion
        suggestions.append({
            'priority': 'low',
            'category': 'cost_optimization',
            'suggestion': 'Review software subscriptions for unused services',
            'related_to': 'subscription_audit'
        })

        # Client follow-up suggestion
        if task_analysis['by_type'].get('email', 0) < 5:
            suggestions.append({
                'priority': 'medium',
                'category': 'client_relations',
                'suggestion': 'Increase client communication frequency',
                'related_to': 'client_engagement'
            })

        return suggestions

    def generate_briefing(self) -> Path:
        """
        Generate the Weekly CEO Briefing document.

        Returns:
            Path to generated briefing file
        """
        self.logger.info('Generating Weekly CEO Briefing...')

        # Get date range
        start_date, end_date = self.get_week_date_range()
        
        # Analyze data
        task_analysis = self.analyze_completed_tasks(start_date, end_date)
        financials = self.analyze_financials()
        bottlenecks = self.identify_bottlenecks(task_analysis, financials)
        suggestions = self.generate_suggestions(bottlenecks, task_analysis, financials)

        # Generate briefing content
        briefing_date = datetime.now()
        filename = f"WEEKLY_BRIEFING_{briefing_date.strftime('%Y-%m-%d')}.md"
        filepath = self.briefings / filename

        # Format dates for display
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        # Build task breakdown section
        task_breakdown = ""
        for task_type, count in task_analysis['by_type'].items():
            task_breakdown += f"- **{task_type.title()}**: {count}\n"

        # Build bottlenecks section
        bottlenecks_md = ""
        for b in bottlenecks:
            severity_emoji = "🔴" if b['severity'] == 'high' else "🟡"
            bottlenecks_md += f"{severity_emoji} **{b['type'].replace('_', ' ').title()}**\n"
            bottlenecks_md += f"   - {b['description']}\n\n"

        if not bottlenecks:
            bottlenecks_md = "*No significant bottlenecks identified*\n"

        # Build suggestions section
        suggestions_md = ""
        for s in suggestions:
            priority_emoji = "🔴" if s['priority'] == 'high' else "🟡" if s['priority'] == 'medium' else "🟢"
            suggestions_md += f"{priority_emoji} **{s['category'].replace('_', ' ').title()}**\n"
            suggestions_md += f"   - {s['suggestion']}\n\n"

        content = f'''---
generated: {briefing_date.isoformat()}
period: {start_str} to {end_str}
type: weekly_briefing
---

# 📊 Weekly CEO Briefing

**Period:** {start_str} - {end_str}  
**Generated:** {briefing_date.strftime('%Y-%m-%d %H:%M')}

---

## 📈 Executive Summary

{self._generate_executive_summary(task_analysis, financials, bottlenecks)}

---

## ✅ Completed Tasks

**Total Completed:** {task_analysis['total_completed']}

### By Type
{task_breakdown if task_breakdown else '*No tasks categorized*'}

### Recent Tasks
{self._format_recent_tasks(task_analysis['tasks'][:10])}

---

## 💰 Financial Summary

| Metric | Amount |
|--------|--------|
| Revenue | ${financials['revenue']:.2f} |
| Expenses | ${financials['expenses']:.2f} |
| **Profit** | **${financials['profit']:.2f}** |
| Invoices Sent | {financials['invoices_sent']} |
| Invoices Paid | {financials['invoices_paid']} |

---

## 🚧 Bottlenecks

{bottlenecks_md}

---

## 💡 Proactive Suggestions

{suggestions_md}

---

## 📅 Upcoming Deadlines

{self._get_upcoming_deadlines()}

---

## 📝 Notes for Next Week

<!-- Add any additional notes or context here -->

---

*Briefing generated by AI Employee v0.3 - Gold Tier*
*Next briefing: {(briefing_date + timedelta(days=7)).strftime('%Y-%m-%d')}*
'''

        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f'Briefing generated: {filepath.name}')

        # Log the action
        self._log_action('weekly_briefing_generated', {
            'filepath': str(filepath),
            'period': f'{start_str} to {end_str}',
            'tasks_completed': task_analysis['total_completed'],
            'revenue': financials['revenue'],
            'bottlenecks_found': len(bottlenecks)
        })

        return filepath

    def _generate_executive_summary(self, task_analysis: dict, financials: dict, 
                                    bottlenecks: list) -> str:
        """Generate executive summary text."""
        summary_parts = []

        # Task summary
        if task_analysis['total_completed'] > 10:
            summary_parts.append(f"High activity week with {task_analysis['total_completed']} tasks completed.")
        elif task_analysis['total_completed'] > 5:
            summary_parts.append(f"Moderate activity with {task_analysis['total_completed']} tasks completed.")
        else:
            summary_parts.append(f"Low activity week with only {task_analysis['total_completed']} tasks.")

        # Financial summary
        if financials['profit'] > 0:
            summary_parts.append(f"Profitable week with ${financials['profit']:.2f} profit.")
        elif financials['profit'] < 0:
            summary_parts.append(f"Loss of ${abs(financials['profit']):.2f} this week.")
        else:
            summary_parts.append("No financial activity recorded.")

        # Bottleneck summary
        high_severity = [b for b in bottlenecks if b['severity'] == 'high']
        if high_severity:
            summary_parts.append(f"{len(high_severity)} critical issue(s) require attention.")

        return " ".join(summary_parts)

    def _format_recent_tasks(self, tasks: list) -> str:
        """Format recent tasks for display."""
        if not tasks:
            return "*No recent tasks*"

        formatted = []
        for task in tasks[-5:]:  # Last 5 tasks
            date_str = datetime.fromtimestamp(task['completed_date']).strftime('%m-%d')
            formatted.append(f"- [{task['type']}] {task['file']} ({date_str})")

        return '\n'.join(formatted)

    def _get_upcoming_deadlines(self) -> str:
        """Get upcoming deadlines from Business_Goals.md."""
        deadlines = []
        
        goals_file = self.vault_path / 'Business_Goals.md'
        if goals_file.exists():
            content = goals_file.read_text(encoding='utf-8')
            
            # Look for deadline patterns
            import re
            deadline_pattern = r'Deadline[:\s]+(\d{4}-\d{2}-\d{2})'
            matches = re.findall(deadline_pattern, content, re.IGNORECASE)
            
            for match in matches:
                try:
                    deadline = datetime.strptime(match, '%Y-%m-%d')
                    if deadline > datetime.now():
                        days_until = (deadline - datetime.now()).days
                        deadlines.append(f"- Project due {match} ({days_until} days)")
                except:
                    pass

        if not deadlines:
            return "*No upcoming deadlines found*"

        return '\n'.join(deadlines[:5])  # Max 5 deadlines

    def _log_action(self, action_type: str, details: dict):
        """Log an action to the daily log file."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.json'

        # Load existing logs or create new
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text(encoding='utf-8'))
            except:
                logs = []
        else:
            logs = []

        # Add new log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'weekly_audit',
            'parameters': details,
            'approval_status': 'auto',
            'result': 'success'
        }
        logs.append(log_entry)

        # Save logs
        log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')

    def run_audit(self):
        """Run the weekly audit and generate briefing."""
        self.logger.info('Starting Weekly Business Audit...')
        
        try:
            briefing_path = self.generate_briefing()
            self.logger.info(f'Weekly Audit complete. Briefing: {briefing_path}')
            return briefing_path
        except Exception as e:
            self.logger.error(f'Audit error: {e}')
            raise


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Weekly Business Audit')
    parser.add_argument(
        '--vault',
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run in demo mode'
    )

    args = parser.parse_args()

    # Resolve vault path
    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()

    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        sys.exit(1)

    audit = WeeklyAudit(str(vault_path))

    if args.demo:
        print('Weekly Audit Demo Mode')
        print(f'Dry Run: {audit.dry_run}')
        
        # Generate demo briefing
        briefing_path = audit.generate_briefing()
        print(f'\nDemo briefing generated: {briefing_path}')
        return

    # Run audit
    briefing_path = audit.run_audit()
    print(f'Weekly briefing generated: {briefing_path}')


if __name__ == '__main__':
    main()
