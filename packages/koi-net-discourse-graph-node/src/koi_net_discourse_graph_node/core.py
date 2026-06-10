from koi_net.core import FullNode
from .dg_write_handler import DGWriteHandler

from .node_proxy_handler import NodeProxyHandler
from .space_manager import SpaceManager

from .dg_poller import DGPoller
from .config import DiscourseGraphNodeConfig


class DiscourseGraphNode(FullNode):
    config_schema: DiscourseGraphNodeConfig = DiscourseGraphNodeConfig
    space_manager: SpaceManager = SpaceManager
    backfiller: DGPoller = DGPoller
    node_proxy_handler: NodeProxyHandler = NodeProxyHandler
    dg_write_handler: DGWriteHandler = DGWriteHandler