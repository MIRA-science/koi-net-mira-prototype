
from koi_net.core import FullNode
from koi_net_graph_extension.core import GraphMixin
from mira_extras import SembleClient

from .config import SembleNodeConfig
from .semble_sync_handler import SembleSyncHandler


class SembleNode(FullNode, GraphMixin):
    config_schema: SembleNodeConfig = SembleNodeConfig
    semble_sync_handler: SembleSyncHandler = SembleSyncHandler
    semble_client: SembleClient = lambda config: SembleClient(
        api_key=config.env.semble_api_key
    )


if __name__ == "__main__":
    SembleNode().run()