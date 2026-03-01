"""
File System Watcher - Monitors a drop folder for new files
Creates action files in Needs_Action folder when files are added
"""
import os
import sys
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

# Load environment variables
load_dotenv()


class FileDropHandler:
    """
    Handles file drop events using watchdog library.
    Monitors a folder and triggers actions when files are added.
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize file drop handler.
        
        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.drop_folder = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.processed_files = set()
        
        # Ensure directories exist
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        self.needs_action.mkdir(parents=True, exist_ok=True)
    
    def get_file_hash(self, filepath: Path) -> str:
        """
        Calculate MD5 hash of a file for deduplication.
        
        Args:
            filepath: Path to the file
            
        Returns:
            MD5 hash string
        """
        hash_md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def process_new_file(self, filepath: Path) -> Path:
        """
        Process a newly dropped file and create action file.
        
        Args:
            filepath: Path to the new file
            
        Returns:
            Path to created action file
        """
        # Skip if already processed
        file_hash = self.get_file_hash(filepath)
        if file_hash in self.processed_files:
            return None
        
        # Generate action file
        filename = f"FILE_{filepath.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        action_path = self.needs_action / filename
        
        # Get file info
        stat = filepath.stat()
        file_size = stat.st_size
        file_type = filepath.suffix.lower()
        
        # Create markdown content
        content = f'''---
type: file_drop
original_name: {filepath.name}
file_path: {filepath.absolute()}
size: {file_size}
size_human: {self.format_size(file_size)}
file_type: {file_type}
created: {datetime.fromtimestamp(stat.st_ctime).isoformat()}
modified: {datetime.fromtimestamp(stat.st_mtime).isoformat()}
status: pending
---

# File Drop: {filepath.name}

## File Information
- **Original Name:** {filepath.name}
- **Size:** {self.format_size(file_size)}
- **Type:** {file_type}
- **Location:** `{filepath.absolute()}`

## File Content Preview
<!-- Add relevant content preview here -->

```
<!-- If text file, preview content here -->
```

## Suggested Actions
- [ ] Review file content
- [ ] Categorize file type
- [ ] Process or archive file
- [ ] Move to Done when complete

## Notes
<!-- Add any notes or context here -->

---
*Created by File System Watcher - AI Employee v0.1*
'''
        
        action_path.write_text(content, encoding='utf-8')
        self.processed_files.add(file_hash)
        
        return action_path
    
    def format_size(self, size: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size: Size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f'{size:.2f} {unit}'
            size /= 1024
        return f'{size:.2f} TB'


class FilesystemWatcher(BaseWatcher):
    """
    File System Watcher implementation.
    Monitors the Inbox/Drop folder for new files.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        """
        Initialize File System Watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        self.file_handler = FileDropHandler(vault_path)
        self.logger.info(f'Monitoring drop folder: {self.inbox}')
    
    def check_for_updates(self) -> list:
        """
        Check for new files in the drop folder.
        
        Returns:
            List of new file paths
        """
        new_files = []
        
        try:
            # Get all files in inbox/drop folder
            if self.inbox.exists():
                for filepath in self.inbox.iterdir():
                    if filepath.is_file() and not filepath.name.startswith('.'):
                        # Check if file was modified recently (last check interval)
                        mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                        time_diff = (datetime.now() - mtime).total_seconds()
                        
                        if time_diff < self.check_interval * 2:
                            new_files.append(filepath)
        except Exception as e:
            self.logger.error(f'Error checking drop folder: {e}')
        
        return new_files
    
    def create_action_file(self, item) -> Path:
        """
        Create action file for a dropped file.
        
        Args:
            item: Path to the dropped file
            
        Returns:
            Path to created action file
        """
        return self.file_handler.process_new_file(item)


def main():
    """
    Main entry point for File System Watcher.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='File System Watcher for AI Employee')
    parser.add_argument(
        '--vault', 
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--interval', 
        type=int, 
        default=30,
        help='Check interval in seconds'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Create demo file and process it'
    )
    
    args = parser.parse_args()
    
    # Resolve vault path relative to script location
    vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()
    
    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        sys.exit(1)
    
    watcher = FilesystemWatcher(str(vault_path), args.interval)
    
    if args.demo:
        # Create a demo file in the inbox
        demo_file = watcher.inbox / 'demo_document.txt'
        demo_file.write_text('This is a demo document for testing the AI Employee system.\n\nIt was automatically created by the File System Watcher.')
        print(f'Created demo file: {demo_file}')
        
        # Process it
        action_file = watcher.file_handler.process_new_file(demo_file)
        print(f'Created action file: {action_file}')
        return
    
    watcher.run()


if __name__ == '__main__':
    main()
