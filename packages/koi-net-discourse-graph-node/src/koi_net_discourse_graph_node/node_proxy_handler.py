from dataclasses import dataclass

from koi_net.components import Cache, NodeIdentity
from koi_net.infra import depends_on
from koi_net.components.interfaces import KnowledgeHandler, HandlerType
from koi_net.protocol import EdgeProfile, NodeProfile, EventType, KnowledgeObject
from rid_lib.ext import Bundle
from rid_lib.types import HTTPS, KoiNetEdge, KoiNetNode

from .space_manager import SpaceManager


@dataclass
class NodeProxyHandler(KnowledgeHandler):
    cache: Cache
    space_manager: SpaceManager
    identity: NodeIdentity
    
    handler_type=HandlerType.Network
    rid_types=(KoiNetEdge, KoiNetNode)
    
    def process_edge(self, edge_bundle: Bundle):
        edge = edge_bundle.validate_contents(EdgeProfile)
        if HTTPS not in edge.rid_types:
            self.log.info("Skipping non-HTTPS edge target")
            return
        
        self.log.info(f"Processing edge target {edge_bundle.rid}")
        
        self.space_manager.create_space(edge.target)
        self.space_manager.add_to_group(edge.target)
        
    def process_node(self, node_bundle: Bundle):
        node = node_bundle.validate_contents(NodeProfile)
        if HTTPS not in node.provides.event:
            self.log.info("Skipping non-HTTPS event provider")
            return
        
        if node_bundle.rid is self.identity.rid:
            self.log.info("Skipping myself")
            return
        
        self.log.info(f"Processing node provider {node_bundle.rid}")
        
        self.space_manager.create_space(node_bundle.rid)
        self.space_manager.add_to_group(node_bundle.rid)
    
    @depends_on("space_manager")
    def start(self):
        for rid in self.cache.list_rids((KoiNetEdge, KoiNetNode)):
            bundle = self.cache.read(rid)
            if type(rid) is KoiNetNode:
                self.log.info(f"Processing node {rid}")
                self.process_node(bundle)
            
            elif type(rid) is KoiNetEdge:
                self.log.info(f"Processing edge {rid}")
                self.process_edge(bundle)
        
    def handle(self, kobj: KnowledgeObject):
        if kobj.source is not None:
            return
        
        if kobj.normalized_event_type not in (EventType.NEW, EventType.UPDATE):
            return
        
        if type(kobj.rid) is KoiNetNode:
            self.process_node(kobj.bundle)
        
        elif type(kobj.rid) is KoiNetEdge:
            self.process_edge(kobj.bundle)