# Weekly Audit Skill

## Purpose
Generate comprehensive weekly CEO briefings by analyzing business performance, completed tasks, financial data, and identifying bottlenecks with proactive suggestions.

## Capabilities
- Analyze completed tasks from the past week
- Review financial performance (revenue, expenses, profit)
- Integrate with Odoo for accounting data
- Identify business bottlenecks
- Generate proactive suggestions
- Create formatted CEO Briefing document
- Track upcoming deadlines

## Files
- `scripts/weekly_audit.py` - Main audit and briefing generator

## Usage

```bash
# Generate weekly briefing
python scripts/weekly_audit.py --vault ../AI_Employee_Vault

# Demo mode (test generation)
python scripts/weekly_audit.py --vault ../AI_Employee_Vault --demo
```

## Output

Generates briefing in: `AI_Employee_Vault/Briefings/WEEKLY_BRIEFING_YYYY-MM-DD.md`

## Briefing Structure

```markdown
# 📊 Weekly CEO Briefing

**Period:** 2026-03-07 - 2026-03-13
**Generated:** 2026-03-14 10:30

---

## 📈 Executive Summary
High activity week with 15 tasks completed. Profitable week with $2,450 profit.

## ✅ Completed Tasks
**Total Completed:** 15

### By Type
- **Email**: 8
- **LinkedIn**: 4
- **Twitter**: 3

## 💰 Financial Summary
| Metric | Amount |
|--------|--------|
| Revenue | $3,500.00 |
| Expenses | $1,050.00 |
| **Profit** | **$2,450.00** |
| Invoices Sent | 5 |
| Invoices Paid | 3 |

## 🚧 Bottlenecks
🟡 **Unpaid Invoices**
   - 2 invoices sent but not yet paid

## 💡 Proactive Suggestions
🟡 **Client Relations**
   - Increase client communication frequency

🟢 **Cost Optimization**
   - Review software subscriptions for unused services

## 📅 Upcoming Deadlines
- Project Alpha due 2026-03-20 (6 days)
- Project Beta due 2026-03-30 (16 days)

## 📝 Notes for Next Week
<!-- Add any additional notes or context here -->
```

## Configuration

### Environment Variables
```bash
# Dry run mode
DRY_RUN=true

# Odoo integration (optional)
ODOO_URL=http://localhost:8069
ODOO_DATABASE=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=your_password
```

## Audit Logic

### Task Analysis
- Scans `Done/` folder for completed tasks
- Categorizes by type (email, whatsapp, linkedin, twitter, invoice)
- Counts total completed
- Identifies trends

### Financial Analysis
- Reads `Accounting/` folder for transactions
- Parses revenue and expense markers
- Integrates with Odoo for real-time data
- Calculates profit/loss
- Tracks invoice status

### Bottleneck Detection

| Condition | Severity | Suggestion |
|-----------|----------|------------|
| < 5 tasks completed | Medium | Review pipeline |
| No revenue recorded | High | Follow up on invoices |
| Expenses > 50% revenue | Medium | Optimize costs |
| Unpaid invoices | Medium | Send reminders |

### Suggestion Generation
- Based on identified bottlenecks
- Cost optimization recommendations
- Client engagement suggestions
- Subscription audit suggestions

## Scheduling

### Windows Task Scheduler
```batch
:: Run every Monday at 7:00 AM
schtasks /create /tn "Weekly Audit" /tr "python C:\path\to\weekly_audit.py --vault C:\path\to\vault" /sc weekly /d MON /st 07:00
```

### Linux/Mac Cron
```bash
# Run every Monday at 7:00 AM
0 7 * * 1 cd /path/to/project && python weekly_audit.py --vault /path/to/vault
```

## Integration Points

### Odoo Integration
- Fetches invoice data
- Gets account summaries
- Tracks payment status
- Provides real-time financials

### Business Goals
- Reads `Business_Goals.md` for deadlines
- Compares actual vs. targets
- Identifies gaps

### Audit Logger
- Logs briefing generation
- Tracks analysis metrics
- Creates audit trail

## Error Handling

- Missing folders handled gracefully
- Odoo connection failures logged
- File parsing errors skipped
- Empty data reported clearly

## Troubleshooting

### Empty Briefing
- Need completed tasks in `Done/` folder
- Run some tasks first
- Check date range calculation

### Odoo Connection Failed
- Verify Odoo service running
- Check credentials in `.env`
- Ensure database exists

### No Financial Data
- Add accounting files to `Accounting/`
- Configure Odoo integration
- Check file parsing patterns

### Missing Deadlines
- Add deadlines to `Business_Goals.md`
- Use format: `Deadline: YYYY-MM-DD`
- Ensure dates are in future

---

*Skill Version: 1.0*
*AI Employee v0.3 - Gold Tier*
