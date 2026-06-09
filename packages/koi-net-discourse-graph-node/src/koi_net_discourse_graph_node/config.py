from pydantic import BaseModel, Field
from koi_net.config import (
    FullNodeConfig, 
    KoiNetConfig, 
    ServerConfig, 
    FullNodeProfile, 
    NodeProvides
)
from rid_lib.types import HTTPS, KoiNetNode


class SpaceCredentials(BaseModel):
    name: str
    uri: str
    password: str

class DiscourseGraphConfig(BaseModel):
    base_url: str = "https://discourse-graph-git-mira-collab-discourse-graphs.vercel.app"
    group_name: str = ""
    spaces: dict[KoiNetNode, SpaceCredentials] = {}

class DiscourseGraphNodeConfig(FullNodeConfig):
    server: ServerConfig = ServerConfig(port=8008)
    koi_net: KoiNetConfig = KoiNetConfig(
        node_name="discourse-graph",
        node_profile=FullNodeProfile(
            provides=NodeProvides(
                event=[HTTPS],
                state=[HTTPS]
            )
        )
    )
    discourse_graph: DiscourseGraphConfig = Field(default_factory=DiscourseGraphConfig)