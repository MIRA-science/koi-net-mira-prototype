from dataclasses import dataclass

from koi_net.components import Cache
from koi_net.components.interfaces import KnowledgeHandler, HandlerType
from koi_net.protocol import EdgeProfile, EventType, KnowledgeObject
from rid_lib.ext import Bundle
from rid_lib.types import HTTPS, KoiNetEdge

from .space_manager import SpaceManager


@dataclass
class NodeProxyHandler(KnowledgeHandler):
    cache: Cache
    space_manager: SpaceManager
    
    handler_type=HandlerType.Network
    rid_types=(KoiNetEdge,)
    
    def process_edge(self, edge_bundle: Bundle):
        edge = edge_bundle.validate_contents(EdgeProfile)
        if HTTPS not in edge.rid_types:
            return
        
        self.log.info(f"Processing edge {edge_bundle.rid}")
        
        self.space_manager.create_space(edge.target)
        self.space_manager.add_to_group(edge.target)
    
    def start(self):
        for rid in self.cache.list_rids((KoiNetEdge,)):
            edge_bundle = self.cache.read(rid)
            self.process_edge(edge_bundle)
    
    def handle(self, kobj: KnowledgeObject):
        if kobj.normalized_event_type not in (EventType.NEW, EventType.UPDATE):
            return
        
        self.process_edge(kobj.bundle)