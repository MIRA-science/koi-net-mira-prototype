from koi_net.core import FullNode
from koi_net_graph_extension.core import GraphMixin

from .mira_server import MiraServer
from .config import MiraEndpointNodeConfig


class MiraEndpointNode(FullNode, GraphMixin):
    config_schema: MiraEndpointNodeConfig = MiraEndpointNodeConfig
    server: MiraServer = MiraServer

if __name__ == "__main__":
    MiraEndpointNode().run()