"""
Cleanup script - Remove duplicate email files from Gmail Watcher
"""
from pathlib import Path
import re
from collections import defaultdict


def cleanup_duplicates(vault_path: str):
    """Remove duplicate email files, keep only the latest."""
    
    needs_action = Path(vault_path) / 'Needs_Action'
    
    if not needs_action.exists():
        print(f'Needs_Action folder not found at {needs_action}')
        return
    
    # Group files by message ID
    files_by_id = defaultdict(list)
    
    for f in needs_action.glob('EMAIL_*.md'):
        # Extract message ID from filename
        # Pattern: EMAIL_{id}_{timestamp}.md
        match = re.match(r'EMAIL_(\d+)_(\d+)\.md', f.name)
        if match:
            msg_id = match.group(1)
            timestamp = match.group(2)
            files_by_id[msg_id].append({
                'path': f,
                'timestamp': timestamp,
                'name': f.name
            })
    
    # Remove duplicates (keep latest)
    removed = 0
    kept = 0
    
    for msg_id, files in files_by_id.items():
        if len(files) > 1:
            # Sort by timestamp (latest first)
            files.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Keep the latest
            print(f'Keeping: {files[0]["name"]}')
            kept += 1
            
            # Remove older duplicates
            for file_info in files[1:]:
                try:
                    file_info['path'].unlink()
                    print(f'  Removed: {file_info["name"]}')
                    removed += 1
                except Exception as e:
                    print(f'  Error removing {file_info["name"]}: {e}')
    
    print(f'\nCleanup complete!')
    print(f'Removed: {removed} duplicate files')
    print(f'Kept: {kept} unique files')


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Cleanup duplicate email files')
    parser.add_argument('--vault', default='../AI_Employee_Vault', help='Vault path')
    
    args = parser.parse_args()
    
    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()
    
    cleanup_duplicates(str(vault_path))
