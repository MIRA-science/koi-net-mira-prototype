import base64
import json

import requests
import supabase

# base_url = "http://localhost:3000/"
# base_url = "https://discoursegraphs.com/"
base_url = "https://discourse-graph-git-rt-experiments-discourse-graphs.vercel.app/"


def spaceAnonUserEmail(platform: str, spaceId: int) -> str:
    return f"{platform.lower()}-{spaceId}-anon@database.discoursegraphs.com"


# Create a space. Idempotent: You can obtain the id from the space.
def create_space(platform: str, url: str, name: str, password: str) -> int:
    r = requests.post(
        base_url + "api/supabase/space",
        json=dict(name=name, platform=platform, url=url, password=password),
    )
    return r.json()["id"]


def login(client, platform: str, space_id: int, password: str, **_kwargs) -> dict:
    email = spaceAnonUserEmail(platform, space_id)
    # Use credentials to get a session, convert it into a cookie
    auth_resp = client.auth.sign_in_with_password(dict(email=email, password=password))
    cookie = "base64-" + base64.b64encode(
        auth_resp.session.model_dump_json().encode("ascii")
    ).decode("ascii")
    hostname = client.supabase_url.host.split(".")[0]
    cookiename = f"sb-{hostname}-auth-token"
    cookies = {cookiename: cookie}
    return cookies


print("Getting client... ", end="")
# Get supabase client
r = requests.get(base_url + "api/supabase/env")
e = r.json()
supabase_url = e["SUPABASE_URL"]
print("Done")
client = supabase.Client(supabase_url, e["SUPABASE_PUBLISHABLE_KEY"])


# Create a space
space_data = dict(
    name="MyTestSpace",  # the name of the space
    platform="Obsidian",  # For now constrained to Roam or Obsidian, we need to make that more open
    url="obsidian:aeb4ab025a564a97",  # generated URI. Could be a URL. Unique identifier.
    password="abcdefghi",  # Generate a real password
)

space_data["space_id"] = create_space(**space_data)

# Verify that we can login to that space
cookies = login(client, **space_data)


# Use another credential to get a resource under restricted access
# local_existing_space_data = dict(
#     platform="Obsidian", space_id=28620, password="REDACTED"
# )
existing_space_data = dict(
    platform="Obsidian",
    password="REDACTED",
    # either you have the id,
    space_id=14967110,
    # Or you have the url and name; in that case use create_space as above to get the Id.
    # url="obsidian:e2b87967ba0a06a0",
    # name="Telescope-Obsidian-Vault",
)
print("Logging in... ", end="")
cookies = login(client, **existing_space_data)
print("Done")

# look into a space that you would have access to (directly or through a group)
# space_id = 16579
# resource_id = 84512
space_id = existing_space_data["space_id"]
resource_id = 11576958
print("Querying endpoint... ", end="")
r = requests.get(
    f"{base_url}api/data/{space_id}/{resource_id}",
    cookies=cookies,
    params=dict(schema=1, context=1),
)
print("Done")
data = r.json()
print(r.json())

with open("resp.json", "w") as f:
    json.dump(data, f, indent=2)


# TODO: Add a ressource to your own space
