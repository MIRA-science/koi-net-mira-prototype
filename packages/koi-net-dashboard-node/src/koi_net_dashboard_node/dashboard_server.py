from dataclasses import dataclass

from fastapi import Request
from koi_net.components import KobjQueue, NodeServer
from rdflib import Dataset


@dataclass
class DashboardServer(NodeServer):
    kobj_queue: KobjQueue
    rdf_dataset: Dataset
    
    def create_dashboard_endpoint(self):
        async def endpoint(req: Request):
            query = (await req.body()).decode()
            results = self.rdf_dataset.query(query)
            return [
                {str(var): str(val) for var, val in zip(results.vars, row)}
                for row in results
            ]
        
        return endpoint
    
    def __post_init__(self):
        super().__post_init__()
        self.app.add_api_route(
            path="/query",
            endpoint=self.create_dashboard_endpoint(),
            methods=["POST"]
        )