from dataclasses import dataclass

from fastapi import Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from koi_net.components import KobjQueue, NodeServer
from .config import DashboardNodeConfig
from rdflib import Dataset


@dataclass
class DashboardServer(NodeServer):
    kobj_queue: KobjQueue
    rdf_dataset: Dataset
    config: DashboardNodeConfig
    
    def create_dashboard_endpoint(self):
        async def endpoint(req: Request):
            if req.headers.get("X-API-Key") != self.config.env.dashboard_api_key:
                raise HTTPException(status_code=401, detail="Unauthorized")
            
            query = (await req.body()).decode()
            results = self.rdf_dataset.query(query)
            return [
                {str(var): str(val) for var, val in zip(results.vars, row)}
                for row in results
            ]

        return endpoint
    
    def __post_init__(self):
        super().__post_init__()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:8000"],
            allow_methods=["POST"],
            allow_headers=["*"],
        )
        self.app.add_api_route(
            path="/query",
            endpoint=self.create_dashboard_endpoint(),
            methods=["POST"]
        )