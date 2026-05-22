import uuid
from dataclasses import dataclass, field
from logging import Logger

from rid_lib.types import KoiNetNode

from .discourse_graph import DiscourseGraphClient, DiscourseGraphSpaceClient
from .config import DiscourseGraphNodeConfig, SpaceCredentials


@dataclass
class SpaceManager:
    log: Logger
    config: DiscourseGraphNodeConfig
    
    dg_client: DiscourseGraphClient = field(init=False)
    space_clients: dict[KoiNetNode, DiscourseGraphSpaceClient] = field(init=False)
    
    def start(self):
        self.dg_client = DiscourseGraphClient(
            base_url=self.config.discourse_graph.base_url
        )
        self.load_spaces()
        
    def load_spaces(self):
        self.space_clients = {}
        for node, creds in self.config.discourse_graph.spaces.items():
            self.space_clients[node] = self.dg_client.create_space(
                name=creds.name,
                url=creds.uri,
                password=creds.password
            )
        
    def create_space(self, node: KoiNetNode, name: str):
        creds = SpaceCredentials(
            name=name,
            uri=str(node),
            password=str(uuid.uuid4())
        )
        self.config.discourse_graph.spaces[node] = creds
        self.config.save_to_yaml()