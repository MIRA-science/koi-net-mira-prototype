import uuid
from dataclasses import dataclass, field
from logging import Logger

from koi_net.components import NodeIdentity
from rid_lib.types import KoiNetNode
from mira_extras import DiscourseGraphClient, DiscourseGraphSpaceClient

from .config import DiscourseGraphNodeConfig, SpaceCredentials


@dataclass
class SpaceManager:
    log: Logger
    config: DiscourseGraphNodeConfig
    identity: NodeIdentity
    
    dg_client: DiscourseGraphClient = field(init=False)
    space_clients: dict[KoiNetNode, DiscourseGraphSpaceClient] = field(init=False)
    
    def start(self):
        self.dg_client = DiscourseGraphClient(
            base_url=self.config.discourse_graph.base_url
        )
        self.load_spaces()
        
    def load_spaces(self):
        self.log.info("Loading spaces from configuration...")
        self.space_clients = {}
        for node, creds in self.config.discourse_graph.spaces.items():
            space_client = self.dg_client.create_space(
                name=creds.name,
                url=creds.uri,
                password=creds.password
            )
            self.space_clients[node] = space_client
            self.log.info(f"Loaded {node} space proxy, member of " + ", ".join(space_client.get_groups().values()))
        
        if self.identity.rid not in self.space_clients:
            self.create_space(self.identity.rid)
        
    def create_space(self, node: KoiNetNode):
        if node in self.config.discourse_graph.spaces:
            return
        
        self.log.info(f"Creating new space for {node}")
        creds = SpaceCredentials(
            name=node.name,
            uri=str(node),
            password=str(uuid.uuid4())
        )
        self.config.discourse_graph.spaces[node] = creds
        self.config.save_to_yaml()
        
    def add_to_group(self, node: KoiNetNode):
        self.log.info(f"Adding {node} space proxy to group '{self.config.discourse_graph.group_name}'")
        manager_client = self.space_clients.get(self.identity.rid)
        space_client = self.space_clients.get(node)
        manager_client.add_to_group_direct(
            group_name=self.config.discourse_graph.group_name,
            account_id=space_client.pseudo_account_id
        )