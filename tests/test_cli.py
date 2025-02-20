"""Test cases for CLI interface."""
import pytest
import shutil
from pathlib import Path
from src.cli import main


@pytest.fixture
def clean_test_env(test_config, sample_docx, output_dir):
    """Set up a clean test environment."""
    # Clear and recreate output directory
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    # Create config file
    config_path = Path("./tests/test_config.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Update config with correct paths
    test_config["file_settings"]["input_path"] = str(sample_docx.parent)
    test_config["file_settings"]["output_path"] = str(output_dir)

    # Write config
    import json
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(test_config, f, ensure_ascii=False, indent=2)

    return config_path


def test_cli_with_config(clean_test_env, caplog):
    """Test CLI with configuration file."""
    config_path = clean_test_env

    # Run CLI with explicit arguments
    result = main([
        "--config", str(config_path),
    ])

    assert result == 0, "CLI should return 0 on successful execution"


def test_cli_dry_run(clean_test_env, caplog):
    """Test CLI in dry run mode."""
    config_path = clean_test_env

    # Run CLI with dry-run option
    result = main(["--config", str(config_path), "--dry-run"])

    # Verify results
    assert result == 0, "CLI should return 0 on successful dry run"
