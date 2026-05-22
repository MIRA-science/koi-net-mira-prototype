from pydantic import BaseModel, Field
from koi_net.config import (
    FullNodeConfig, 
    KoiNetConfig, 
    ServerConfig, 
    FullNodeProfile, 
    NodeProvides
)
from rid_lib.types import KoiNetNode


class SpaceCredentials(BaseModel):
    name: str
    uri: str
    password: str

class DiscourseGraphConfig(BaseModel):
    base_url: str = ""
    spaces: dict[KoiNetNode, SpaceCredentials] = {}

class DiscourseGraphNodeConfig(FullNodeConfig):
    server: ServerConfig = ServerConfig(port=8008)
    koi_net: KoiNetConfig = KoiNetConfig(
        node_name="discourse-graphs-node",
        node_profile=FullNodeProfile(
            provides=NodeProvides()
        )
    )
    discourse_graph: DiscourseGraphConfig = Field(default_factory=DiscourseGraphConfig)