import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.markup import escape

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Manage log files - keep only the 5 most recent
log_files = sorted(logs_dir.glob("harmony_*.log"), key=os.path.getmtime)
if len(log_files) >= 5:
    # Remove oldest log files to keep only 4, making room for the new one
    for old_file in log_files[: (len(log_files) - 4)]:
        old_file.unlink()

# Create a single log file with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"harmony_{timestamp}.log"


class Logger:
    """
    A logger class that provides methods for logging at different levels
    and optionally printing to console.

    All loggers write to a single log file with a timestamp in the filename.
    """

    def __init__(self, name=None):
        """
        Initialize a logger with the given name.

        Args:
            name: The name for the logger. If None, returns the root logger.
        """
        self._logger = logging.getLogger(name)
        self.console = Console()

        # Only configure if handlers haven't been added yet
        if not self._logger.handlers:
            self._logger.setLevel(logging.INFO)

            # Prevent propagation to avoid duplicate log entries
            self._logger.propagate = False

            # Create formatters
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_formatter = logging.Formatter("%(levelname)s - %(message)s")

            # Create file handler for logging to a single file
            file_handler = RotatingFileHandler(
                logs_dir / log_filename,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
            )
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(file_formatter)

            # Create console handler for logging to console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(
                logging.WARNING
            )  # Only warnings and above to console
            console_handler.setFormatter(console_formatter)

            # Add handlers to logger
            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)

    def debug(self, message):
        """Log a debug message."""
        self._logger.debug(message)

    def info(self, message):
        """Log an info message."""
        self._logger.info(message)

    def warning(self, message):
        """Log a warning message."""
        self._logger.warning(message)

    def error(self, message):
        """Log an error message."""
        self._logger.error(message)

    def critical(self, message):
        """Log a critical message."""
        self._logger.critical(message)

    def log(self, level, message):
        """
        Log a message with the specified level.

        Args:
            level: The logging level (e.g., logging.INFO, logging.DEBUG)
            message: The message to log
        """
        self._logger.log(level, message)

    def log_and_print(self, message, level=logging.INFO):
        """
        Log a message to the log file and print it to the console.

        Args:
            message: The message to log and print
            level: The logging level. Defaults to logging.INFO.
        """
        # Log to file - escape rich markup tags for log file
        self._logger.log(level, escape(message))

        # Also print to console regardless of level
        self.console.print(message)
