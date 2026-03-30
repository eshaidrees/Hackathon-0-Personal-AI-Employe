# Odoo Integration Skill

## Purpose
Integrate with Odoo Community ERP (v19+) for accounting and business operations via JSON-RPC API.

## Capabilities
- Create and manage invoices (customer/vendor)
- Search and create business partners (customers/vendors)
- Register payments against invoices
- Post invoices (confirm them)
- Get account summaries (receivable, payable, bank balance)
- Financial reporting and analysis

## Files
- `scripts/odoo_mcp_server.py` - Main Odoo MCP implementation
- `scripts/odoo_mcp_server.py` - Can be used as MCP server or standalone CLI

## Usage

### CLI Commands

```bash
# Authenticate with Odoo
python scripts/odoo_mcp_server.py auth

# Create invoice for partner
python scripts/odoo_mcp_server.py create_invoice --partner-id 1 --amount 1500

# Search for business partner
python scripts/odoo_mcp_server.py search_partner --name "Client Name"

# Get all invoices
python scripts/odoo_mcp_server.py get_invoices

# Get account summary
python scripts/odoo_mcp_server.py summary

# Demo mode (test connection)
python scripts/odoo_mcp_server.py demo
```

### Python API

```python
from odoo_mcp_server import OdooMCP

# Initialize
odoo = OdooMCP(
    odoo_url='http://localhost:8069',
    db='odoo',
    username='admin',
    password='your_password'
)

# Authenticate
if odoo.authenticate():
    # Create partner
    partner = odoo.create_partner(
        name='Acme Corp',
        email='contact@acme.com',
        phone='+1234567890'
    )
    
    # Create invoice
    invoice = odoo.create_invoice(
        partner_id=partner['partner_id'],
        invoice_lines=[
            {
                'name': 'Consulting Services',
                'quantity': 10,
                'price_unit': 150
            }
        ]
    )
    
    # Post invoice
    odoo.post_invoice(invoice['invoice_id'])
    
    # Register payment
    odoo.register_payment(
        invoice_id=invoice['invoice_id'],
        amount=1500
    )
```

## Configuration

### Environment Variables
```bash
# Odoo instance URL
ODOO_URL=http://localhost:8069

# Odoo database name
ODOO_DATABASE=odoo

# Odoo username (usually 'admin')
ODOO_USERNAME=admin

# Odoo password or API key
ODOO_PASSWORD=your_password

# Dry run mode (no actual actions)
DRY_RUN=true
```

## Setup

### Option A: Docker (Recommended)
```bash
# Run Odoo container
docker run -d -p 8069:8069 --name odoo odoo:19.0

# Wait 2-3 minutes for Odoo to start
# Open browser: http://localhost:8069
# Create database and install "Invoicing" module
```

### Option B: Local Installation
1. Download Odoo Community v19+ from https://www.odoo.com/page/download
2. Install and start Odoo service
3. Create database via web interface
4. Install Accounting/Invoicing module

## Approval Workflow

For sensitive actions (creating invoices, registering payments), the skill creates approval request files:

```
Pending_Approval/
└── ODOO_APPROVAL_create_invoice_20260314_103000.md
```

Human reviews and moves file to:
- `Approved/` - Execute the action
- `Rejected/` - Discard the action

## Error Handling

- Authentication failures are logged and reported
- Network errors trigger retry logic (via error_recovery.py)
- API errors are quarantined for review

## Audit Logging

All Odoo operations are logged via audit_logger.py:
- Action type
- Parameters
- Result (success/failure)
- Approval status
- Timestamp

## Troubleshooting

### Connection Failed
- Verify Odoo service is running
- Check URL format: `http://localhost:8069`
- Ensure database exists

### Authentication Failed
- Verify username/password
- Check database name
- Ensure user has API access permissions

### JSON-RPC Error
- Verify Odoo version (19+ required)
- Check endpoint URLs
- Review Odoo logs for errors

---

*Skill Version: 1.0*
*AI Employee v0.3 - Gold Tier*
