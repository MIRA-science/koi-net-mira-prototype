from koi_net.core import FullNode

from .dg_client import DGClient

from .config import DiscourseGraphsNodeConfig


class DiscourseGraphsNode(FullNode):
    config_schema = DiscourseGraphsNodeConfig
    dg_client = DGClient