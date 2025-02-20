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
RESOURCES_DIR = ROOT_DIR / "resources"
ICONS_DIR = RESOURCES_DIR / "icons"

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

# Icon Files
ICON_FILE = None
if sys.platform.startswith('win'):
    icon_path = ICONS_DIR / "icon.ico"
    if icon_path.exists():
        ICON_FILE = icon_path
elif sys.platform.startswith('darwin'):
    icon_path = ICONS_DIR / "icon.icns"
    if icon_path.exists():
        ICON_FILE = icon_path

# Resource Files
RESOURCE_FILES = [
    (str(ICONS_DIR), 'icons')
]
