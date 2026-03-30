"""
Odoo MCP Server - Odoo Community Edition integration via JSON-RPC API
Handles accounting, invoices, customers, and financial operations
Requires Odoo 19+ with JSON-RPC API enabled
"""
import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class OdooMCP:
    """
    Odoo MCP for accounting and business operations.
    Interfaces with Odoo Community Edition via JSON-RPC API.
    """

    def __init__(self, odoo_url: str = None, db: str = None, 
                 username: str = None, password: str = None):
        """
        Initialize Odoo MCP.

        Args:
            odoo_url: Base URL of Odoo instance (e.g., http://localhost:8069)
            db: Database name
            username: Odoo username (usually 'admin')
            password: Odoo password or API key
        """
        self.odoo_url = odoo_url or os.getenv('ODOO_URL', 'http://localhost:8069')
        self.db = db or os.getenv('ODOO_DATABASE', 'odoo')
        self.username = username or os.getenv('ODOO_USERNAME', 'admin')
        self.password = password or os.getenv('ODOO_PASSWORD', '')
        
        self.uid = None  # User ID after authentication
        self.session = requests.Session()
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'

        import logging
        self.logger = logging.getLogger(self.__class__.__name__)

    def _json_rpc(self, endpoint: str, params: dict) -> dict:
        """
        Make JSON-RPC call to Odoo.

        Args:
            endpoint: API endpoint (e.g., '/web/dataset/call')
            params: Request parameters

        Returns:
            JSON response dict
        """
        url = f"{self.odoo_url}{endpoint}"
        
        headers = {
            'Content-Type': 'application/json',
        }

        payload = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': params,
            'id': 1
        }

        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if 'error' in result:
                self.logger.error(f"Odoo API Error: {result['error']}")
                return None
            
            return result.get('result', {})
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP Error: {e}")
            return None

    def authenticate(self) -> bool:
        """
        Authenticate with Odoo and get session UID.

        Returns:
            True if successful
        """
        if self.dry_run:
            self.logger.info('[DRY RUN] Would authenticate with Odoo')
            self.uid = 1  # Mock UID
            return True

        try:
            # Authenticate via /web/session/authenticate
            result = self._json_rpc('/web/session/authenticate', {
                'db': self.db,
                'login': self.username,
                'password': self.password
            })

            if result and result.get('uid'):
                self.uid = result['uid']
                self.logger.info(f'Authenticated as user {self.uid}')
                return True
            else:
                self.logger.error('Authentication failed')
                return False

        except Exception as e:
            self.logger.error(f'Authentication error: {e}')
            return False

    def _ensure_authenticated(self):
        """Ensure we're authenticated before making calls."""
        if not self.uid:
            if not self.authenticate():
                raise Exception('Odoo authentication failed')

    def create_invoice(self, partner_id: int, invoice_lines: list, 
                       invoice_type: str = 'out_invoice',
                       payment_terms: str = None) -> dict:
        """
        Create a customer invoice in Odoo.

        Args:
            partner_id: Customer/partner ID in Odoo
            invoice_lines: List of line items with product, quantity, price
            invoice_type: 'out_invoice' (customer) or 'in_invoice' (vendor)
            payment_terms: Payment terms reference

        Returns:
            Invoice creation result with ID
        """
        if self.dry_run:
            self.logger.info(f'[DRY RUN] Would create invoice for partner {partner_id}')
            self.logger.info(f'[DRY RUN] Lines: {invoice_lines}')
            return {'status': 'dry_run', 'invoice_id': None}

        self._ensure_authenticated()

        # Prepare invoice lines
        lines_data = []
        for line in invoice_lines:
            lines_data.append((0, 0, {
                'product_id': line.get('product_id'),
                'name': line.get('name', 'Service'),
                'quantity': line.get('quantity', 1),
                'price_unit': line.get('price_unit', 0),
                'account_id': line.get('account_id'),
            }))

        # Create invoice
        invoice_data = {
            'move_type': invoice_type,
            'partner_id': partner_id,
            'invoice_line_ids': lines_data,
            'invoice_date': datetime.now().strftime('%Y-%m-%d'),
        }

        if payment_terms:
            invoice_data['invoice_payment_term_id'] = payment_terms

        result = self._json_rpc('/web/dataset/call', {
            'model': 'account.move',
            'method': 'create',
            'args': [invoice_data],
            'kwargs': {}
        })

        if result:
            invoice_id = result if isinstance(result, int) else result.get('result')
            self.logger.info(f'Invoice created: {invoice_id}')
            return {'status': 'created', 'invoice_id': invoice_id}
        
        return {'status': 'error', 'error': 'Failed to create invoice'}

    def search_partner(self, email: str = None, name: str = None) -> list:
        """
        Search for business partners (customers/vendors).

        Args:
            email: Email to search
            name: Name to search

        Returns:
            List of matching partners
        """
        if self.dry_run:
            self.logger.info(f'[DRY RUN] Would search partner: {email or name}')
            return [{'id': 1, 'name': 'Demo Partner', 'email': 'demo@example.com'}]

        self._ensure_authenticated()

        domain = []
        if email:
            domain.append(['email', '=', email])
        if name:
            domain.append(['name', 'ilike', name])

        result = self._json_rpc('/web/dataset/search_read', {
            'model': 'res.partner',
            'domain': domain,
            'fields': ['id', 'name', 'email', 'phone', 'is_company'],
            'limit': 10
        })

        return result.get('records', []) if result else []

    def create_partner(self, name: str, email: str = None, phone: str = None,
                       is_company: bool = True) -> dict:
        """
        Create a new business partner.

        Args:
            name: Partner name
            email: Email address
            phone: Phone number
            is_company: True if company, False if individual

        Returns:
            Creation result with partner ID
        """
        if self.dry_run:
            self.logger.info(f'[DRY RUN] Would create partner: {name}')
            return {'status': 'dry_run', 'partner_id': None}

        self._ensure_authenticated()

        partner_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'is_company': is_company,
            'customer_rank': 1 if is_company else 0,
        }

        result = self._json_rpc('/web/dataset/call', {
            'model': 'res.partner',
            'method': 'create',
            'args': [partner_data],
            'kwargs': {}
        })

        if result:
            partner_id = result if isinstance(result, int) else result.get('result')
            self.logger.info(f'Partner created: {partner_id}')
            return {'status': 'created', 'partner_id': partner_id}
        
        return {'status': 'error', 'error': 'Failed to create partner'}

    def get_invoices(self, partner_id: int = None, state: str = None,
                     limit: int = 10) -> list:
        """
        Get invoices from Odoo.

        Args:
            partner_id: Filter by partner
            state: Filter by state (draft, posted, paid, cancel)
            limit: Max results

        Returns:
            List of invoices
        """
        if self.dry_run:
            self.logger.info('[DRY RUN] Would get invoices')
            return []

        self._ensure_authenticated()

        domain = []
        if partner_id:
            domain.append(['partner_id', '=', partner_id])
        if state:
            domain.append(['state', '=', state])

        result = self._json_rpc('/web/dataset/search_read', {
            'model': 'account.move',
            'domain': domain,
            'fields': ['id', 'name', 'partner_id', 'amount_total', 
                      'amount_due', 'date', 'state', 'move_type'],
            'limit': limit
        })

        return result.get('records', []) if result else []

    def post_invoice(self, invoice_id: int) -> dict:
        """
        Post an invoice (confirm it).

        Args:
            invoice_id: Odoo invoice ID

        Returns:
            Status dict
        """
        if self.dry_run:
            self.logger.info(f'[DRY RUN] Would post invoice {invoice_id}')
            return {'status': 'dry_run'}

        self._ensure_authenticated()

        result = self._json_rpc('/web/dataset/call', {
            'model': 'account.move',
            'method': 'action_post',
            'args': [[invoice_id]],
            'kwargs': {}
        })

        if result is not None:
            self.logger.info(f'Invoice {invoice_id} posted')
            return {'status': 'posted'}
        
        return {'status': 'error', 'error': 'Failed to post invoice'}

    def register_payment(self, invoice_id: int, amount: float, 
                         payment_date: str = None) -> dict:
        """
        Register a payment for an invoice.

        Args:
            invoice_id: Invoice ID
            amount: Payment amount
            payment_date: Payment date (YYYY-MM-DD)

        Returns:
            Payment registration result
        """
        if self.dry_run:
            self.logger.info(f'[DRY RUN] Would register payment {amount} for invoice {invoice_id}')
            return {'status': 'dry_run'}

        self._ensure_authenticated()

        payment_date = payment_date or datetime.now().strftime('%Y-%m-%d')

        # Create payment wizard
        wizard_result = self._json_rpc('/web/dataset/call', {
            'model': 'account.payment.register',
            'method': 'create',
            'args': [{
                'payment_date': payment_date,
                'amount': amount,
            }],
            'kwargs': {}
        })

        if wizard_result:
            wizard_id = wizard_result if isinstance(wizard_result, int) else wizard_result.get('result')
            
            # Confirm payment
            self._json_rpc('/web/dataset/call', {
                'model': 'account.payment.register',
                'method': 'action_create_payments',
                'args': [[wizard_id]],
                'kwargs': {}
            })

            self.logger.info(f'Payment registered for invoice {invoice_id}')
            return {'status': 'payment_registered'}
        
        return {'status': 'error', 'error': 'Failed to register payment'}

    def get_account_summary(self) -> dict:
        """
        Get summary of accounts (receivable, payable, etc.).

        Returns:
            Account summary dict
        """
        if self.dry_run:
            return {
                'accounts_receivable': 0.0,
                'accounts_payable': 0.0,
                'bank_balance': 0.0
            }

        self._ensure_authenticated()

        # Get account types
        result = self._json_rpc('/web/dataset/search_read', {
            'model': 'account.account',
            'domain': [
                ('deprecated', '=', False),
                ('account_type', 'in', ['asset_receivable', 'liability_payable', 'asset_cash'])
            ],
            'fields': ['id', 'name', 'code', 'account_type', 'balance'],
            'limit': 100
        })

        accounts = result.get('records', []) if result else []

        summary = {
            'accounts_receivable': 0.0,
            'accounts_payable': 0.0,
            'bank_balance': 0.0,
            'accounts': accounts
        }

        for acc in accounts:
            balance = acc.get('balance', 0)
            acc_type = acc.get('account_type', '')
            
            if acc_type == 'asset_receivable':
                summary['accounts_receivable'] += balance
            elif acc_type == 'liability_payable':
                summary['accounts_payable'] += balance
            elif acc_type == 'asset_cash':
                summary['bank_balance'] += balance

        return summary

    def create_approval_request(self, action: str, details: dict, 
                                vault_path: str) -> Path:
        """
        Create approval request file for sensitive Odoo actions.

        Args:
            action: Action type (create_invoice, register_payment, etc.)
            details: Action details
            vault_path: Path to Obsidian vault

        Returns:
            Path to approval file
        """
        vault = Path(vault_path)
        pending = vault / 'Pending_Approval'
        pending.mkdir(parents=True, exist_ok=True)

        filename = f"ODOO_APPROVAL_{action}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = pending / filename

        details_str = json.dumps(details, indent=2)

        content = f'''---
type: approval_request
action: odoo_{action}
created: {datetime.now().isoformat()}
status: pending
---

# Odoo Action Approval Request

## Action Type
{action}

## Details
```json
{details_str}
```

## To Approve
Move this file to /Approved/ folder.

## To Reject
Move this file to /Rejected/ folder.

---
*Created by Odoo MCP - AI Employee v0.1*
'''

        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f'Approval request created: {filepath.name}')
        return filepath


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Odoo MCP Server')
    parser.add_argument('action', choices=[
        'auth', 'create_invoice', 'search_partner', 'create_partner',
        'get_invoices', 'post_invoice', 'register_payment', 'summary', 'demo'
    ])
    parser.add_argument('--url', help='Odoo URL')
    parser.add_argument('--db', help='Database name')
    parser.add_argument('--user', help='Username')
    parser.add_argument('--password', help='Password')
    parser.add_argument('--partner-id', type=int, help='Partner ID')
    parser.add_argument('--invoice-id', type=int, help='Invoice ID')
    parser.add_argument('--amount', type=float, help='Amount')
    parser.add_argument('--vault', default='../AI_Employee_Vault', help='Vault path')
    parser.add_argument('--demo', action='store_true', help='Demo mode')

    args = parser.parse_args()

    # Override env vars if provided
    if args.url:
        os.environ['ODOO_URL'] = args.url
    if args.db:
        os.environ['ODOO_DATABASE'] = args.db
    if args.user:
        os.environ['ODOO_USERNAME'] = args.user
    if args.password:
        os.environ['ODOO_PASSWORD'] = args.password

    mcp = OdooMCP()

    if args.demo or args.action == 'demo':
        print('Odoo MCP Demo Mode')
        print(f'Dry Run: {mcp.dry_run}')
        print('\n1. Testing authentication...')
        if mcp.authenticate():
            print('✓ Authentication successful')
        else:
            print('✗ Authentication failed (expected in demo mode)')

        print('\n2. Testing partner search...')
        partners = mcp.search_partner(name='Demo')
        print(f'Found partners: {partners}')

        print('\n3. Testing account summary...')
        summary = mcp.get_account_summary()
        print(f'Account Summary: {json.dumps(summary, indent=2)}')

    elif args.action == 'auth':
        if mcp.authenticate():
            print('Authentication successful')
        else:
            print('Authentication failed')

    elif args.action == 'create_invoice':
        if not args.partner_id:
            print('Error: --partner-id required')
            sys.exit(1)
        
        lines = [{'name': 'Service', 'quantity': 1, 'price_unit': args.amount or 100}]
        result = mcp.create_invoice(args.partner_id, lines)
        print(f'Result: {result}')

    elif args.action == 'search_partner':
        partners = mcp.search_partner(email=args.partner_id and None, name='Test')
        print(f'Found: {partners}')

    elif args.action == 'get_invoices':
        invoices = mcp.get_invoices(limit=10)
        for inv in invoices:
            print(f"{inv['name']}: ${inv['amount_total']} - {inv['state']}")

    elif args.action == 'summary':
        summary = mcp.get_account_summary()
        print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
