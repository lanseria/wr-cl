import argparse
import sys
from pathlib import Path
from typing import List, Optional

# 导入抽离的 logger 配置方法
from src import config
from src import processor
from src.logger_config import setup_logger


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
        default="debug",
        help="Set the logging level (default: debug)",
    )

    parsed_args = parser.parse_args(args)

    # 使用抽离的 logger 设置方法
    logger = setup_logger("src.cli", level=parsed_args.log_level)

    logger.debug("Current log level: %s", parsed_args.log_level)
    logger.debug("Starting application with arguments: %s", vars(parsed_args))

    try:
        config_path = Path(parsed_args.config)
        if not config_path.exists():
            logger.error("Configuration file not found: %s",
                         parsed_args.config)
            return 1

        logger.debug("Loading configuration from: %s", config_path)
        cfg = config.load_config(str(config_path))
        logger.info("Configuration loaded successfully")

        input_path = Path(cfg["file_settings"]["input_path"])
        if not input_path.exists():
            logger.error("Input directory not found: %s", input_path)
            return 1

        logger.debug("Input directory validated: %s", input_path)
        logger.debug("Output directory set to: %s",
                     cfg["file_settings"]["output_path"])

        logger.debug("Initializing document processor...")
        doc_processor = processor.DocumentProcessor(
            cfg, dry_run=parsed_args.dry_run)
        logger.info("Document processor initialized")

        logger.info("Starting document processing...")
        doc_processor.process_all()
        logger.info("Processing completed successfully")
        return 0

    except Exception as e:
        logger.exception("An error occurred during execution:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
