import logging


# Create a custom formatter
class MyFormatter(logging.Formatter):
    def format(self, record):
        record.filename = record.filename.split("/")[-1]  # Extract only the filename
        return super().format(record)


# Create a logger object
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

# Create a console handler and set the level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Set the logging level for the console handler

# Create a formatter and set the format with time and log level.
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Formatter for printing class name and code line number, easy to debut the messages
# formatter = MyFormatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s')

# Formatter for printing just message, good in general
formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)
logger.propagate = False
