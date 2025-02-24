import logging
from logging import Logger


def setup_logger(name: str, level: str = "debug") -> Logger:
    """
    Set up and return a logger with the specified name and log level.
    This logger is configured to output logs to the console with a formatted output.
    """
    log_level = level.upper()
    level_value = getattr(logging, log_level, logging.DEBUG)

    logger = logging.getLogger(name)
    logger.setLevel(level_value)

    # 清除已有的 Handler 避免重复添加
    if logger.hasHandlers():
        logger.handlers.clear()

    # 创建终端 Handler 并设置级别和格式
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level_value)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 禁止日志向上层传播，避免重复输出
    logger.propagate = False

    logger.debug("Logger '%s' has been set up with level '%s'",
                 name, log_level)
    return logger
