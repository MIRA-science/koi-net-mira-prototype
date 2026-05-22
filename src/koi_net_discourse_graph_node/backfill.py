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

from .discourse_graph import DiscourseGraphsClient
from .config import DiscourseGraphsNodeConfig
from .rid_types import DiscourseGraphNode
# from .discourse_graphs import DiscourseGraphsClient



@dataclass
class DGPoller(ThreadedComponent):
    log: Logger
    config: DiscourseGraphsNodeConfig
    # dg_client: DiscourseGraphsClient
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
        self.dg_client = DiscourseGraphsClient(
            base_url=self.config.discourse_graphs.base_url)
        self.dg_space = self.dg_client.create_space(
            name="Test Vault",
            url="obsidian:28af0fec9a63ca73",
            password="REDACTED"
        )
        
        while not self.exit_event.is_set():
            self.log.info("Polling...")
            start_time = time.monotonic()
            self.poll()
            self.exit_event.wait(
                max(0, 5 - (time.monotonic() - start_time))
            )

    def poll(self):
        space_data = self.dg_space.get_space()
        
        print(json.dumps(space_data, indent=2))

        for resource_ref in space_data["container_of"]:
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
            
            resource = self.dg_space.get_resource(res_rid.resource_id)
            
            self.kobj_queue.push(
                bundle=Bundle.generate(
                    rid=res_rid,
                    contents=resource
                )
            )