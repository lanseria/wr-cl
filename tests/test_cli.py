"""Test cases for CLI interface."""
import pytest
import logging
from pathlib import Path
from src.cli import main


def test_cli_with_config(test_config, sample_docx, output_dir, monkeypatch, caplog):
    """Test CLI with configuration file."""
    # Set up logging
    caplog.set_level(logging.INFO)

    # Write test config to file
    import json
    config_path = Path("./tests/test_config.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Update config with correct paths
    test_config["file_settings"]["input_path"] = str(sample_docx.parent)
    test_config["file_settings"]["output_path"] = str(output_dir)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(test_config, f, ensure_ascii=False, indent=2)

    # Mock sys.argv
    monkeypatch.setattr("sys.argv", ["wr-cl", "--config", str(config_path)])

    # Run CLI
    result = main()

    # Check return code and logs
    assert result == 0, "CLI should return 0 on successful execution"
    assert any("Processing document" in record.message for record in caplog.records), \
        "Expected 'Processing document' in logs"
    assert any("Processing completed successfully" in record.message for record in caplog.records), \
        "Expected 'Processing completed successfully' in logs"


def test_cli_dry_run(test_config, sample_docx, output_dir, monkeypatch, caplog):
    """Test CLI in dry run mode."""
    # Set up logging
    caplog.set_level(logging.INFO)

    # Write test config to file
    import json
    config_path = Path("./tests/test_config.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Update config with correct paths
    test_config["file_settings"]["input_path"] = str(sample_docx.parent)
    test_config["file_settings"]["output_path"] = str(output_dir)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(test_config, f, ensure_ascii=False, indent=2)

    # Mock sys.argv
    monkeypatch.setattr(
        "sys.argv", ["wr-cl", "--config", str(config_path), "--dry-run"])

    # Run CLI
    result = main()

    # Check return code and logs
    assert result == 0, "CLI should return 0 on successful dry run"
    assert any("Dry run" in record.message for record in caplog.records), \
        "Expected 'Dry run' in logs"
    assert any("Processing completed successfully" in record.message for record in caplog.records), \
        "Expected 'Processing completed successfully' in logs"
