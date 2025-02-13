from importlib.metadata import version, PackageNotFoundError
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,  # Adjust this to the desired global log level
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

setup_logging()

try:
    __version__ = version("pypergraph")
except PackageNotFoundError:
    __version__ = "0.0.0"