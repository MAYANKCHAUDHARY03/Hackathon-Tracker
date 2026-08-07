import os
import shutil
import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backup_sqlite():
    """Create a point-in-time backup of the SQLite database."""
    base_dir = Path(__file__).resolve().parent.parent
    db_path = base_dir / "hackathon.db"
    backup_dir = base_dir / "backups"
    
    if not backup_dir.exists():
        backup_dir.mkdir(parents=True)
        
    if not db_path.exists():
        logger.error(f"Database not found at {db_path}")
        return
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"hackathon_backup_{timestamp}.db"
    
    logger.info(f"Creating backup of {db_path} to {backup_path}")
    try:
        shutil.copy2(db_path, backup_path)
        logger.info(f"Backup successful: {backup_path}")
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        
if __name__ == "__main__":
    backup_sqlite()
