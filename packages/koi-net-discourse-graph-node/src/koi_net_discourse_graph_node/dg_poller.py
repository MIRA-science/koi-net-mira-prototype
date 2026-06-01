import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from logging import Logger

from koi_net.components import KobjQueue, Cache
from koi_net.components.interfaces import ThreadedComponent
from koi_net.infra import depends_on
from koi_net.protocol import KnowledgeObject
from rdflib import Graph, Namespace
from rid_lib.ext import Bundle

from .space_manager import SpaceManager

from .config import DiscourseGraphNodeConfig


@dataclass
class DGPoller(ThreadedComponent):
    log: Logger
    space_manager: SpaceManager
    config: DiscourseGraphNodeConfig
    kobj_queue: KobjQueue
    cache: Cache
    
    exit_event: threading.Event = field(init=False, default_factory=threading.Event)
    
    @depends_on("kobj_worker")
    def start(self):
        self.exit_event.clear()
        super().start()
        
    def stop(self):
        self.exit_event.set()
        super().stop()
        
    def run(self):
        while not self.exit_event.is_set():
            self.log.info("Polling...")
            start_time = time.monotonic()
            self.poll()
            self.exit_event.wait(
                max(0, 30 - (time.monotonic() - start_time))
            )
    
    
    def poll(self):
        for node, space_client in self.space_manager.space_clients.items():
            self.log.debug(f"Polling for {node}")
            groups = space_client.get_groups().copy()
            self.log.debug(f"Polling node {node}")
            for group_id, group_name in groups.items():
                self.log.debug(f"Polling group {group_name}")
                group_spaces = space_client.get_group_member_data(group_name)

                for group_space_data in group_spaces:
                    if group_space_data["sharing_permissions"] is None:
                        continue
                    
                    space_id = group_space_data["space_id"]
                    self.log.debug(f"Polling space {space_id} ({group_space_data['name']})")
                    space_data = space_client.get_space(space_id)
                    
                    # self.log.debug(json.dumps(space_data, indent=2))
                    
                    space_graph = Graph()
                    space_graph.parse(data=space_data, format="json-ld")
                    
                    SIOC = Namespace("http://rdfs.org/sioc/ns#")
                    DC = Namespace("http://purl.org/dc/elements/1.1/")
                    
                    for _, _, resource_uri in space_graph.triples((None, SIOC.container_of, None)):
                        self.log.debug(f"Processing {resource_uri}")
                        prev_bundle = self.cache.read(resource_uri)
                        
                        if prev_bundle:
                            last_modified = datetime.fromisoformat(
                                prev_bundle.contents["modified"])
                            
                            curr_modified_str = space_graph.value(
                                subject=resource_uri, 
                                predicate=DC.modified)
                            curr_modified = datetime.fromisoformat(curr_modified_str)
                            
                            if curr_modified <= last_modified:
                                continue
                            else:
                                self.log.info("existing resource modified!")
                        else:
                            self.log.info("new resource!")
                        
                        resource_data = space_client.get_resource(resource_uri.split("/")[-1])
                        
                        kobj = KnowledgeObject.from_bundle(
                            Bundle.generate(
                                rid=resource_uri,
                                contents=resource_data
                            )
                        )
                        kobj.network_targets.add(node)
                        
                        self.kobj_queue.push(kobj=kobj)
                        
