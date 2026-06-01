from dataclasses import dataclass, field

from koi_net.config import FullNodeConfig, FullNodeProfile, NodeProvides, ServerConfig, KoiNetConfig, EnvConfig
from koi_net.core import FullNode
from koi_net.components.interfaces import KnowledgeHandler, HandlerType
from koi_net.protocol import KnowledgeObject
from koi_net_graph_extension.core import GraphMixin
from pydantic import Field
from rid_lib.types import HTTPS, KoiNetNode
from mira_extras.semble import SemblePDSClient


class SembleEnvConfig(EnvConfig):
    bsky_handle: str
    bsky_app_password: str

class SembleNodeConfig(FullNodeConfig):
    server: ServerConfig = ServerConfig(port=8009)
    koi_net: KoiNetConfig = KoiNetConfig(
        node_name="semble",
        node_profile=FullNodeProfile(
            provides=NodeProvides()
        ),
        rid_types_of_interest=[KoiNetNode, HTTPS]
    )
    env: SembleEnvConfig = Field(default_factory=SembleEnvConfig)

@dataclass
class SembleHandler(KnowledgeHandler):
    config: SembleNodeConfig
    client: SemblePDSClient = field(init=False)
    
    handler_type=HandlerType.Network
    rid_types=(HTTPS,)
    
    def __post_init__(self):
        super().__post_init__()
        self.client = SemblePDSClient(service="https://bsky.social")
        self.client.login(
            self.config.env.bsky_handle,
            self.config.env.bsky_app_password
        )
        
    def handle(self, kobj: KnowledgeObject):
        self.client.create_card(
            url=str(kobj.rid),
            note="test note"
        )
        

class SembleNode(FullNode, GraphMixin):
    config_schema = SembleNodeConfig
    semble_handler = SembleHandler



if __name__ == "__main__":
    SembleNode().run()