from koi_net.config import FullNodeConfig, FullNodeProfile, NodeProvides, ServerConfig, KoiNetConfig, EnvConfig
from rid_lib.types import HTTPS, KoiNetNode
from pydantic import Field


class SembleEnvConfig(EnvConfig):
    bsky_handle: str
    bsky_app_password: str

class SembleNodeConfig(FullNodeConfig):
    server: ServerConfig = ServerConfig(port=8009)
    koi_net: KoiNetConfig = KoiNetConfig(
        node_name="semble",
        node_profile=FullNodeProfile(
            provides=NodeProvides()
        ),
        rid_types_of_interest=[KoiNetNode, HTTPS]
    )
    env: SembleEnvConfig = Field(default_factory=SembleEnvConfig)
