from dataclasses import dataclass, field

from koi_net.components.interfaces import KnowledgeHandler, HandlerType
from koi_net.protocol import KnowledgeObject
from rdflib import Dataset
from rid_lib.types import HTTPS
from mira_extras.semble import SemblePDSClient
from koi_net_graph_extension.components import GraphParser

from .config import SembleNodeConfig


@dataclass
class SembleSyncHandler(KnowledgeHandler):
    config: SembleNodeConfig
    semble_client: SemblePDSClient = field(init=False)
    rdf_dataset: Dataset
    graph_parser: GraphParser
    
    handler_type=HandlerType.Final
    rid_types=(HTTPS,)
    
    def __post_init__(self):
        super().__post_init__()
        self.semble_client = SemblePDSClient(service="https://bsky.social")
        
    def start(self):
        self.semble_client.login(
            self.config.env.bsky_handle,
            self.config.env.bsky_app_password
        )
        
    def handle(self, kobj: KnowledgeObject):
        self.log.info(f"HANDLING NEW DG DATA {kobj.rid}")
        
        graph = self.graph_parser.bundle_to_graph(kobj.bundle)
        
        result = graph.query(f"""
            PREFIX dc: <http://purl.org/dc/elements/1.1/>
            PREFIX dgc: <https://discoursegraphs.com/schema/dg_core#>
            SELECT ?type ?title
            WHERE {{
                VALUES ?type {{ dgc:Claim dgc:Evidence dgc:Question }}
                <{kobj.rid}> a ?type ; dc:title ?title .
            }}
        """)
        
        if not result:
            return
        
        (row,) = result
        
        # print(f"DRY RUN creating card <{kobj.rid}> '{row.title}'")
        
        self.semble_client.create_card(
            url=str(kobj.rid),
            note=row.title
        )