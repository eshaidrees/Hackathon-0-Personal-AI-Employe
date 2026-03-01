"""
Approval Manager - Manage HITL approval workflow
List, expire, and monitor approval requests
"""
import sys
import json
from pathlib import Path
from datetime import datetime
import re


class ApprovalManager:
    """Manage approval requests in the AI Employee system."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path).resolve()
        self.pending = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        
        # Ensure folders exist
        for folder in [self.pending, self.approved, self.rejected]:
            folder.mkdir(parents=True, exist_ok=True)
    
    def list_pending(self) -> list:
        """List all pending approval requests."""
        if not self.pending.exists():
            return []
        
        pending_list = []
        for f in self.pending.glob('APPROVAL_*.md'):
            content = f.read_text(encoding='utf-8')
            info = self._parse_approval(content, f)
            pending_list.append(info)
        
        return pending_list
    
    def list_approved(self) -> list:
        """List all approved (executed) requests."""
        if not self.approved.exists():
            return []
        
        approved_list = []
        for f in self.approved.glob('APPROVAL_*.md'):
            content = f.read_text(encoding='utf-8')
            info = self._parse_approval(content, f)
            approved_list.append(info)
        
        return approved_list
    
    def list_expired(self) -> list:
        """List expired approval requests."""
        expired = []
        for item in self.list_pending():
            if item['expires'] and datetime.now() > item['expires']:
                expired.append(item)
        return expired
    
    def _parse_approval(self, content: str, filepath: Path) -> dict:
        """Parse approval file content."""
        info = {
            'filename': filepath.name,
            'path': str(filepath),
            'type': 'unknown',
            'action': 'unknown',
            'created': None,
            'expires': None,
            'status': 'pending'
        }
        
        # Extract frontmatter
        if content.startswith('---'):
            lines = content.split('\n')
            in_frontmatter = False
            for line in lines:
                if line.strip() == '---':
                    in_frontmatter = not in_frontmatter
                    continue
                if in_frontmatter:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'type':
                            info['type'] = value
                        elif key == 'action':
                            info['action'] = value
                        elif key == 'created':
                            try:
                                info['created'] = datetime.fromisoformat(value)
                            except:
                                pass
                        elif key == 'expires':
                            try:
                                info['expires'] = datetime.fromisoformat(value)
                            except:
                                pass
                        elif key == 'status':
                            info['status'] = value
        
        return info
    
    def expire_old_approvals(self, hours: int = 48) -> int:
        """Move expired approvals to Rejected folder."""
        expired = self.list_expired()
        moved = 0
        
        for item in expired:
            src = Path(item['path'])
            dest = self.rejected / src.name
            src.rename(dest)
            moved += 1
            print(f"Moved expired: {src.name}")
        
        return moved
    
    def get_stats(self) -> dict:
        """Get approval statistics."""
        return {
            'pending': len(self.list_pending()),
            'approved': len(self.list_approved()),
            'expired': len(self.list_expired()),
            'rejected': len(list(self.rejected.glob('APPROVAL_*.md'))) if self.rejected.exists() else 0
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Approval Manager')
    parser.add_argument('--vault', default='../AI_Employee_Vault', help='Vault path')
    parser.add_argument('action', choices=['list', 'stats', 'expire'], help='Action')
    parser.add_argument('--type', choices=['pending', 'approved', 'expired'], 
                       default='pending', help='List type')
    parser.add_argument('--hours', type=int, default=48, help='Expiry hours')
    
    args = parser.parse_args()
    
    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()
    
    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        sys.exit(1)
    
    manager = ApprovalManager(str(vault_path))
    
    if args.action == 'list':
        if args.type == 'pending':
            items = manager.list_pending()
        elif args.type == 'approved':
            items = manager.list_approved()
        elif args.type == 'expired':
            items = manager.list_expired()
        
        if items:
            print(f"{'Filename':<50} {'Type':<20} {'Action':<20} {'Created':<25}")
            print("-" * 115)
            for item in items:
                created = item['created'].strftime('%Y-%m-%d %H:%M') if item['created'] else 'N/A'
                print(f"{item['filename']:<50} {item['type']:<20} {item['action']:<20} {created:<25}")
        else:
            print(f"No {args.type} approvals found")
    
    elif args.action == 'stats':
        stats = manager.get_stats()
        print("Approval Statistics:")
        print(f"  Pending:   {stats['pending']}")
        print(f"  Approved:  {stats['approved']}")
        print(f"  Expired:   {stats['expired']}")
        print(f"  Rejected:  {stats['rejected']}")
    
    elif args.action == 'expire':
        moved = manager.expire_old_approvals(args.hours)
        print(f"Moved {moved} expired approvals to Rejected folder")


if __name__ == '__main__':
    main()
