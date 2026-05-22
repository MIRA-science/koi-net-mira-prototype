import datetime

from pydantic import BaseModel
from koi_net.config import (
    FullNodeConfig, 
    KoiNetConfig, 
    ServerConfig, 
    FullNodeProfile, 
    NodeProvides
)

class DiscourseGraphsConfig(BaseModel):
    base_url: str = ""
    space_id: str = ""
    password: str = ""

class DiscourseGraphsNodeConfig(FullNodeConfig):
    server: ServerConfig = ServerConfig(port=8008)
    koi_net: KoiNetConfig = KoiNetConfig(
        node_name="discourse-graphs-node",
        node_profile=FullNodeProfile(
            provides=NodeProvides()
        )
    )
    discourse_graphs: DiscourseGraphsConfig = DiscourseGraphsConfig()
