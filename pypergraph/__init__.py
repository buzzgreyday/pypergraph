from importlib.metadata import version, PackageNotFoundError
import logging

from pypergraph.account import DagAccount, MetagraphTokenClient
from pypergraph.account.monitor import Monitor as DagMonitor
from pypergraph.network.dag_network import DagTokenNetwork
from pypergraph.network.metagraph_network import MetagraphTokenNetwork
from pypergraph.keystore.keystore import KeyStore
from pypergraph.keyring.manager import KeyringManager

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,  # Adjust this to the desired global log level
        format='%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(funcName)s - %(message)s',
    )

setup_logging()

try:
    __version__ = version("pypergraph")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["DagAccount", "MetagraphTokenClient", "DagMonitor", "MetagraphTokenNetwork", "DagTokenNetwork", "KeyStore", "KeyringManager"]