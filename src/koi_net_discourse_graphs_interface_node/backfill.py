from dataclasses import dataclass, field
from datetime import datetime
import json
from logging import Logger
import threading
import time

from koi_net.components import KobjQueue, Cache
from koi_net.components.interfaces import ThreadedComponent
from koi_net.infra import depends_on
from rid_lib.ext import Bundle

from .config import DiscourseGraphsNodeConfig
from .rid_types import DiscourseGraphNode
from .discourse_graphs import DiscourseGraphsClient



@dataclass
class DGPoller(ThreadedComponent):
    log: Logger
    config: DiscourseGraphsNodeConfig
    dg_client: DiscourseGraphsClient
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
                max(0, 5 - (time.monotonic() - start_time))
            )

    def poll(self):
        space = self.dg_client.get_space()
        
        print(json.dumps(space, indent=2))

        for resource_ref in space["container_of"]:
            res_rid = DiscourseGraphNode(
                space_id=self.config.discourse_graphs.space_id,
                resource_id=resource_ref["@id"].split(":")[1]
            )
            
            prev_bundle = self.cache.read(res_rid)
            
            if prev_bundle:
                last_modified = datetime.fromisoformat(
                    prev_bundle.contents["modified"])
                
                curr_modified = datetime.fromisoformat(
                    resource_ref["modified"])
                
                if curr_modified <= last_modified:
                    continue
                else:
                    self.log.info("existing resource modified!")
            else:
                self.log.info("new resource!")
            
            resource = self.dg_client.get_resource(res_rid.resource_id)
            
            self.kobj_queue.push(
                bundle=Bundle.generate(
                    rid=res_rid,
                    contents=resource
                )
            )