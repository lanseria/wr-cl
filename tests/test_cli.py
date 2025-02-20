"""Test cases for CLI interface."""
import pytest
from pathlib import Path
from src.cli import main
# CLI 接口测试


def test_cli_with_config(test_config, sample_docx, output_dir, monkeypatch, capsys):
    """Test CLI with configuration file."""
    # Write test config to file
    import json
    config_path = Path("./tests/test_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(test_config, f, ensure_ascii=False, indent=2)

    # Mock sys.argv
    monkeypatch.setattr("sys.argv", ["wr-cl", "--config", str(config_path)])

    # Run CLI
    result = main()
    assert result == 0

    # Check output
    captured = capsys.readouterr()
    assert "Processing document" in captured.out


def test_cli_dry_run(test_config, sample_docx, output_dir, monkeypatch, capsys):
    """Test CLI in dry run mode."""
    # Write test config to file
    import json
    config_path = Path("./tests/test_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(test_config, f, ensure_ascii=False, indent=2)

    # Mock sys.argv
    monkeypatch.setattr(
        "sys.argv", ["wr-cl", "--config", str(config_path), "--dry-run"])

    # Run CLI
    result = main()
    assert result == 0

    # Check output
    captured = capsys.readouterr()
    assert "Dry run" in captured.out
