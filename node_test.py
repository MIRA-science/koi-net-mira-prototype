from pathlib import Path

from koi_net.core import LogSystem

from koi_net_discourse_graph_node.core import DiscourseGraphNode
from rid_lib.types import KoiNetNode

from koi_net_discourse_graph_node.discourse_graph import DiscourseGraphClient

node = DiscourseGraphNode(root_dir=Path("dg"))

LogSystem(use_console_handler=False)

node.start()
# node.space_manager.create_space(
#     node=KoiNetNode("test-node", "example-hash"),
#     name="Example KOI Node"
# )

dg_client = DiscourseGraphClient(base_url=node.config.discourse_graph.base_url)
user_client = dg_client.create_space(
    name="Luke's Demo Space",
    url="obsidian:cc0cf7742508b0c2",
    password="REDACTED"
)
GROUP_NAME = "devtest3"

# node_client = list(node.space_manager.space_clients.values())[0]

# user_client.add_to_group_direct(GROUP_NAME, node_client.pseudo_account_id)

# groups = user_client.get_groups()
# print(groups)
# node.stop()