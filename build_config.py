"""Configuration for building executable."""
import sys
from pathlib import Path

# Basic Information
APP_NAME = "wr-cl"
VERSION = "1.0.0"
AUTHOR = "lanseria"
DESCRIPTION = "Word Document Content Replacer"

# Build Paths
ROOT_DIR = Path(__file__).parent
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"

# Entry Point
MAIN_SCRIPT = "src/cli.py"

# Files to Include
DATA_FILES = [
    ('config.json.template', 'config.json.template'),
]

# Hidden Imports
HIDDEN_IMPORTS = [
    'docx',
    'concurrent.futures',
]

# Icon File (Platform Specific)
ICON_FILE = None
if sys.platform.startswith('win'):
    ICON_FILE = ROOT_DIR / "resources" / "icon.ico"
elif sys.platform.startswith('darwin'):
    ICON_FILE = ROOT_DIR / "resources" / "icon.icns"
