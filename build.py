"""Build script for creating executable."""
import os
import sys
import shutil
import subprocess
from pathlib import Path
from build_config import *


def clean_build_dirs():
    """Clean build and dist directories."""
    print("Cleaning build directories...")
    for dir_path in [DIST_DIR, BUILD_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"Removed {dir_path}")


def create_spec_file():
    """Create spec file for PyInstaller."""
    icon_path = ''
    if ICON_FILE and ICON_FILE.exists():
        icon_path = str(ICON_FILE).replace('\\', '\\\\')

    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['{ROOT_DIR}'],
    binaries=[],
    datas={DATA_FILES},
    hiddenimports={HIDDEN_IMPORTS},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{icon_path}' if '{icon_path}' else None,
)
"""
    spec_file = ROOT_DIR / f"{APP_NAME}.spec"
    spec_file.write_text(spec_content, encoding='utf-8')
    print(f"Created spec file: {spec_file}")
    return spec_file


def build_executable():
    """Build the executable using PyInstaller."""
    try:
        # Install PyInstaller if not already installed
        subprocess.run([sys.executable, "-m", "pip",
                       "install", "pyinstaller"], check=True)

        # Clean previous builds
        clean_build_dirs()

        # Create spec file
        spec_file = create_spec_file()

        # Build executable
        print("\nBuilding executable...")
        result = subprocess.run(
            ["pyinstaller", "--clean", str(spec_file)],
            check=True,
            encoding='utf-8',
            env={
                **os.environ,
                'PYTHONIOENCODING': 'utf-8',
                'PYTHONUTF8': '1'
            }
        )

        print("\nBuild completed successfully!")
        exe_path = DIST_DIR / \
            (f"{APP_NAME}.exe" if sys.platform.startswith('win') else APP_NAME)
        print(f"Executable location: {exe_path}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def main():
    """Main entry point for build script."""
    try:
        if build_executable():
            print("\nBuild successful!")
            sys.exit(0)
        else:
            print("\nBuild failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\nBuild failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
