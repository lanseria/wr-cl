"""Configuration management for wr-cl."""
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "replacements": {
        "pattern_type": "plain",
        "rules": [
            {
                "old_text": "\\b公司A\\b",
                "new_text": "DeepSeek",
                "options": {
                    "case_sensitive": True,
                    "whole_word": True,
                    "preserve_format": True
                }
            }
        ]
    },
    "file_settings": {
        "input_path": "./docs",
        "file_types": [".docx"],
        "output_path": "./modified"
    },
    "advanced": {
        "max_workers": 4,
        "timeout": 30
    }
}

def create_default_config(config_path: str) -> None:
    """Create a default configuration file."""
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
    logger.info(f"Created default configuration file at {config_path}")

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    config_file = Path(config_path)
    
    if not config_file.exists():
        logger.warning(f"Configuration file not found at {config_path}")
        create_default_config(config_path)
        return DEFAULT_CONFIG
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {str(e)}")