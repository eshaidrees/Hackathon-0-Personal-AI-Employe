"""
Base Watcher Class - Template for all watchers
All Watchers follow this structure for consistency
"""
import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher scripts.
    Watchers monitor external sources and create action files in Needs_Action folder.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        self.processed_ids = set()
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process.
        
        Returns:
            List of new items (dicts with item data)
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a .md file in Needs_Action folder for the item.
        
        Args:
            item: The item to process
            
        Returns:
            Path to the created file
        """
        pass
    
    def run(self):
        """
        Main run loop - continuously checks for updates and creates action files.
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    try:
                        filepath = self.create_action_file(item)
                        self.logger.info(f'Created action file: {filepath.name}')
                    except Exception as e:
                        self.logger.error(f'Error creating action file: {e}')
            except Exception as e:
                self.logger.error(f'Error in check loop: {e}')
            
            time.sleep(self.check_interval)
    
    def generate_filename(self, prefix: str, unique_id: str) -> str:
        """
        Generate a standardized filename.
        
        Args:
            prefix: File type prefix (EMAIL, WHATSAPP, etc.)
            unique_id: Unique identifier for the item
            
        Returns:
            Filename string
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'{prefix}_{unique_id}_{timestamp}.md'
