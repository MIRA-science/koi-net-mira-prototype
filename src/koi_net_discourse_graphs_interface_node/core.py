from koi_net.core import FullNode

from .backfill import DGPoller

from .discourse_graphs import DiscourseGraphsClient
from .config import DiscourseGraphsNodeConfig


class DiscourseGraphsInterfaceNode(FullNode):
    config_schema = DiscourseGraphsNodeConfig
    dg_client = lambda config: DiscourseGraphsClient(
        base_url=config.discourse_graphs.base_url,
        space_id=config.discourse_graphs.space_id,
        password=config.discourse_graphs.password
    ).connect()
    backfiller = DGPoller