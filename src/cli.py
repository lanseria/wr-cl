"""Command line interface for wr-cl."""
import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from . import config
from . import processor


def setup_logging(log_level: str) -> None:
    """Set up logging configuration."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    # Remove any existing handlers to avoid duplicate logs
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Set up basic configuration
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True  # Force reconfiguration of the root logger
    )

    # Ensure our package logger is set to the correct level
    logger = logging.getLogger("src")
    logger.setLevel(numeric_level)


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Word document content replacer command line tool"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="./config.json",
        help="Path to configuration file (default: ./config.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files",
    )
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Set the logging level",
    )

    # Parse arguments
    parsed_args = parser.parse_args(args)

    # Setup logging
    setup_logging(parsed_args.log_level)
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config_path = Path(parsed_args.config)
        if not config_path.exists():
            logger.error(f"Configuration file not found: {parsed_args.config}")
            return 1

        cfg = config.load_config(str(config_path))

        # Validate configuration
        input_path = Path(cfg["file_settings"]["input_path"])
        if not input_path.exists():
            logger.error(f"Input directory not found: {input_path}")
            return 1

        # Initialize processor
        doc_processor = processor.DocumentProcessor(
            cfg, dry_run=parsed_args.dry_run)

        # Process documents
        logger.debug("Starting document processing...")
        doc_processor.process_all()
        logger.info("Processing completed successfully")

        return 0

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
