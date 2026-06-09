
from koi_net.core import FullNode
from koi_net_graph_extension.core import GraphMixin

from .config import DashboardNodeConfig
from .dashboard_server import DashboardServer


class DashboardNode(FullNode, GraphMixin):
    config_schema: DashboardNodeConfig = DashboardNodeConfig
    server = DashboardServer

if __name__ == "__main__":
    DashboardNode().run()