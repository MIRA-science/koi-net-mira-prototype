from rid_lib.core import ORN


class DiscourseGraphNode(ORN):
    namespace: str = "discourse-graph.node"
    
    def __init__(self, space_id: str, resource_id: str):
        ...