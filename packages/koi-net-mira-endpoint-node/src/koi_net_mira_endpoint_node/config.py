from koi_net.config import FullNodeConfig, FullNodeProfile, NodeProvides, ServerConfig, KoiNetConfig
from rid_lib.types import HTTPS


class MiraEndpointNodeConfig(FullNodeConfig):
    server: ServerConfig = ServerConfig(port=8009)
    koi_net: KoiNetConfig = KoiNetConfig(
        node_name="mira-endpoint",
        node_profile=FullNodeProfile(
            provides=NodeProvides(
                event=[HTTPS],
                state=[HTTPS]
            )
        )
    )
