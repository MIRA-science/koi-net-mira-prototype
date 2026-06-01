from dataclasses import dataclass, field

from koi_net.components.interfaces import KnowledgeHandler, HandlerType
from koi_net.protocol import KnowledgeObject
from rid_lib.types import HTTPS
from mira_extras.semble import SemblePDSClient

from .config import SembleNodeConfig


@dataclass
class SembleSyncHandler(KnowledgeHandler):
    config: SembleNodeConfig
    client: SemblePDSClient = field(init=False)
    
    handler_type=HandlerType.Network
    rid_types=(HTTPS,)
    
    def __post_init__(self):
        super().__post_init__()
        self.client = SemblePDSClient(service="https://bsky.social")
        
    def start(self):
        self.client.login(
            self.config.env.bsky_handle,
            self.config.env.bsky_app_password
        )
        
    def handle(self, kobj: KnowledgeObject):
        self.log.info(f"HANDLING NEW DG DATA {kobj.rid}")
        self.client.create_card(
            url=str(kobj.rid),
            note="test note"
        )