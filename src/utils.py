"""Utility functions for wr-cl."""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def ensure_directory(path: str) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory

def get_output_path(input_path: Path, output_dir: Path) -> Path:
    """Generate output path for processed files."""
    return output_dir / input_path.name