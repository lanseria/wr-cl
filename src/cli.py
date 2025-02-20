"""Command line interface for wr-cl."""
import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

# 修改导入方式
from src import config
from src import processor


def setup_logging(log_level: str = "DEBUG") -> None:
    """Set up logging configuration.

    Args:
        log_level (str, optional): Logging level. Defaults to "DEBUG".
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    # Remove any existing handlers to avoid duplicate logs
    root = logging.getLogger("")
    # Only clear handlers if they exist
    if root.handlers:
        for handler in root.handlers[:]:
            root.removeHandler(handler)

        # Add new handler with formatter
        handler = logging.StreamHandler()
        handler.setLevel(numeric_level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        root.addHandler(handler)

    # Set levels for all loggers
    root.setLevel(numeric_level)

    # Configure package loggers
    for logger_name in ["src", "src.cli", "src.processor", "src.config"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(numeric_level)
        # Enable propagation to ensure logs are captured
        logger.propagate = True


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        args (Optional[List[str]], optional): Command line arguments. Defaults to None.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
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
        choices=["debug", "info", "warning", "error", "all"],
        default="all",  # Changed default to "all"
        help="Set the logging level (default: all - shows all log levels)",
    )

    # Parse arguments
    parsed_args = parser.parse_args(args)

    # Setup logging - always show all levels if 'all' is selected
    log_level = "DEBUG" if parsed_args.log_level == "all" else parsed_args.log_level.upper()
    setup_logging(log_level)

    # Get logger for this module
    logger = logging.getLogger("src.cli")

    # Log initial information
    logger.debug("Starting application with arguments: %s", vars(parsed_args))

    try:
        # Load configuration
        config_path = Path(parsed_args.config)
        if not config_path.exists():
            logger.error(f"Configuration file not found: {parsed_args.config}")
            return 1

        logger.debug("Loading configuration from: %s", config_path)
        cfg = config.load_config(str(config_path))
        logger.info("Configuration loaded successfully")

        # Validate configuration
        input_path = Path(cfg["file_settings"]["input_path"])
        if not input_path.exists():
            logger.error(f"Input directory not found: {input_path}")
            return 1

        logger.debug("Input directory validated: %s", input_path)
        logger.debug("Output directory set to: %s",
                     cfg["file_settings"]["output_path"])

        # Initialize processor
        logger.debug("Initializing document processor...")
        doc_processor = processor.DocumentProcessor(
            cfg, dry_run=parsed_args.dry_run)
        logger.info("Document processor initialized successfully")

        # Process documents
        logger.info("Starting document processing...")
        doc_processor.process_all()
        logger.info("Processing completed successfully")

        return 0

    except Exception as e:
        logger.exception("An error occurred during execution:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
