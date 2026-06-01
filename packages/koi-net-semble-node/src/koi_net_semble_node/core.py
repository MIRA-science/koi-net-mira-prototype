
from koi_net.core import FullNode
from koi_net_graph_extension.core import GraphMixin

from .config import SembleNodeConfig
from .semble_sync_handler import SembleSyncHandler

class SembleNode(FullNode, GraphMixin):
    config_schema = SembleNodeConfig
    semble_sync_handler = SembleSyncHandler



if __name__ == "__main__":
    SembleNode().run()