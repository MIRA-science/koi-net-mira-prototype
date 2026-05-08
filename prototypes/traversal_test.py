from datetime import datetime, timedelta, timezone
import json
from rdflib import Dataset
from prototypes.dg_api import DiscourseGraphAPI


SPACE_ID = 14967110
SPACE_PASSWORD = "REDACTED"
VAULT_URI = "obsidian:cc0cf7742508b0c2"
BASE_URL = "https://discourse-graph-git-rt-experiments-discourse-graphs.vercel.app"

class PersistentDatetime:
    def __init__(self, filepath, default=None):
        self.filepath = filepath
        try:
            with open(filepath, "r") as f:
                raw = f.read().strip()
                self._value = datetime.fromisoformat(raw)
        except FileNotFoundError:
            self._value = default
            self._write(default)

    def _write(self, value):
        with open(self.filepath, "w") as f:
            f.write(value.isoformat(timespec='milliseconds') if value is not None else "")

    def get(self) -> datetime:
        return self._value

    def set(self, value: datetime):
        self._value = value
        self._write(value)
        
last_modified = PersistentDatetime("last_modified.txt", datetime.min)

dg = DiscourseGraphAPI(
    base_url=BASE_URL,
    space_id=SPACE_ID,
    password=SPACE_PASSWORD
)
dg.login()
ds = Dataset()

prev_time = last_modified.get()
curr_time = datetime.now(timezone.utc)

all_space = dg.get_space()

with open("all_resources.json", "w") as f:
    json.dump(all_space, f, indent=2)

print(f"Querying after {prev_time}")

diff_space = dg.get_space(
    after=(last_modified.get()).isoformat()
)

contained_resources = diff_space["container_of"]
print(f"Found {len(contained_resources)} modified resources")


last_modified.set(curr_time)

with open("resources_after.json", "w") as f:
    json.dump(diff_space, f, indent=2)


for resource in contained_resources:
    resource_id = resource["@id"].split(":")[1]
    
    print(f"Getting {resource_id}...")
    resource = dg.get_resource(resource_id)
    # print(json.dumps(resource, indent=2))
    print(resource.get("title", "<unknown>"))
    ds.parse(data=resource, format="json-ld")

ds.serialize("test_graph.ttl")

ds.parse(
    data=dg.get_space(),
    format="json-ld"
)