from koi_net.core import FullNode

from .node_proxy_handler import NodeProxyHandler
from .space_manager import SpaceManager

from .dg_poller import DGPoller
from .config import DiscourseGraphNodeConfig


class DiscourseGraphNode(FullNode):
    config_schema = DiscourseGraphNodeConfig
    space_manager = SpaceManager
    backfiller = DGPoller
    node_proxy_handler = NodeProxyHandler