from koi_net.config import FullNodeConfig, FullNodeProfile, NodeProvides, ServerConfig, KoiNetConfig, EnvConfig
from rid_lib.types import HTTPS, KoiNetNode
from pydantic import Field


class DashboardEnvConfig(EnvConfig):
    dashboard_api_key: str


class DashboardNodeConfig(FullNodeConfig):
    server: ServerConfig = ServerConfig(port=8010)
    koi_net: KoiNetConfig = KoiNetConfig(
        node_name="dashboard",
        node_profile=FullNodeProfile(
            provides=NodeProvides()
        ),
        rid_types_of_interest=[KoiNetNode, HTTPS]
    )
    env: DashboardEnvConfig = Field(default_factory=DashboardEnvConfig)