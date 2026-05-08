import json

from rdflib import Dataset, Graph

from koi_net_discourse_graphs_interface_node.discourse_graphs import DiscourseGraphsClient


client = DiscourseGraphsClient(
    base_url="https://discourse-graph-git-rt-experiments-discourse-graphs.vercel.app",
    space_id=14967110,
    password="REDACTED"
).connect()

ds = Dataset()

space_data = client.get_space()

with open("temp/space.json", "w") as f:
    json.dump(space_data, f, indent=2)
    
g = Graph()
g.parse(data=space_data, format="json-ld")
g.serialize("temp/space.ttl")

print(space_data)
for resource_ref in space_data["container_of"]:
    print(resource_ref)
    resource_id = resource_ref["@id"].split(":")[1]
    
    resource = client.get_resource(resource_id)
    print(resource)
    ds.parse(data=resource, format="json-ld")

    
    with open(f"temp/resource_{resource_id}.json", "w") as f:
        json.dump(resource, f, indent=2)
        
    g = Graph()
    g.parse(data=resource, format="json-ld")
    g.serialize(f"temp/resource_{resource_id}.ttl")


    ds.serialize("example.ttl")