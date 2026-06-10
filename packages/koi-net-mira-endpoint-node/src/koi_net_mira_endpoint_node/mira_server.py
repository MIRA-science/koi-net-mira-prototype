from dataclasses import dataclass
from json import JSONDecodeError

from fastapi import Request
from fastapi.responses import JSONResponse
from koi_net.components import KobjQueue, NodeServer
from rid_lib import RID
from rid_lib.ext import Bundle


@dataclass
class MiraServer(NodeServer):
    kobj_queue: KobjQueue
    
    def create_mira_endpoint(self):
        async def endpoint(req: Request):
            try:
                data = await req.json()
            except JSONDecodeError:
                return JSONResponse(
                    content=dict(error="Request body must be a valid JSON object"),
                    status_code=400
                )
            
            if type(data) is not dict:
                return JSONResponse(
                    content=dict(error="Request body must be a valid JSON object"),
                    status_code=400
                )
            
            obj_id = data.get("@id")
            try:
                obj_rid = RID.from_string(obj_id)
            except TypeError:
                return JSONResponse(
                    content=dict(error="JSON object must include a valid @id URI field"),
                    status_code=400
                )
                
            self.kobj_queue.push(
                bundle=Bundle.generate(
                    rid=obj_rid,
                    contents=data
                ))
            
        return endpoint
    
    def __post_init__(self):
        super().__post_init__()
        self.app.add_api_route(
            path="/object",
            endpoint=self.create_mira_endpoint(),
            methods=["POST"]
        )