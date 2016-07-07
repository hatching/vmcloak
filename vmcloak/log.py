import copy
import logging.handlers

class ConsoleHandler(logging.StreamHandler):
    """Logging to console handler."""

    def emit(self, record):
        msg = copy.copy(record)

        logging.StreamHandler.emit(self, msg)