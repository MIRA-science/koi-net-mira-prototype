from rid_lib.core import ORN
from rid_lib.types import SlackMessage


class DiscourseGraphNode(ORN):
    namespace: str = "discourse-graph.node"
    
    def __init__(self, space_id: str, resource_id: str):
        self.space_id = space_id
        self.resource_id = resource_id

    @property
    def reference(self):
        return f"{self.space_id}/{self.resource_id}"

    @classmethod
    def from_reference(cls, reference):
        components = reference.split("/")
        if len(components) == 2:
            return cls(*components)
        else:
            raise ValueError("Discourse Graph Node reference must contain two '/'-separated components: '<space_id>/<resource_id>'")