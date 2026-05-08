import base64
from dataclasses import dataclass, field

import requests
from supabase import Client


@dataclass
class DiscourseGraphClient:
    base_url: str
    space_id: int
    password: str
    platform: str = "Obsidian"

    _supabase: Client = field(init=False, default=None, repr=False)
    _cookies: dict = field(init=False, default_factory=dict, repr=False)

    def connect(self):
        """Fetch supabase env, authenticate, and store session cookies."""
        resp = requests.get(self.base_url + "/api/supabase/env")
        resp.raise_for_status()
        env = resp.json()
        self._supabase = Client(
            supabase_url=env["SUPABASE_URL"],
            supabase_key=env["SUPABASE_PUBLISHABLE_KEY"],
        )
        email = f"{self.platform.lower()}-{self.space_id}-anon@database.discoursegraphs.com"
        auth = self._supabase.auth.sign_in_with_password(
            dict(email=email, password=self.password)
        )
        cookie_value = "base64-" + base64.b64encode(
            auth.session.model_dump_json().encode("ascii")
        ).decode("ascii")
        hostname = self._supabase.supabase_url.host.split(".")[0]
        self._cookies = {f"sb-{hostname}-auth-token": cookie_value}
        return self

    def __enter__(self):
        return self.connect()

    def __exit__(self, *_):
        pass

    @classmethod
    def create_space(cls, base_url: str, name: str, platform: str, url: str, password: str) -> "DiscourseGraphClient":
        """Create a new space and return a client for it, ready to connect."""
        resp = requests.post(
            base_url + "/api/supabase/space",
            json=dict(name=name, platform=platform, url=url, password=password),
        )
        resp.raise_for_status()
        space_id = resp.json()["id"]
        return cls(base_url=base_url, space_id=space_id, platform=platform, password=password)

    def get_space(self, space_id: int = None, **params):
        sid = space_id if space_id is not None else self.space_id
        resp = requests.get(
            self.base_url + f"/api/data/{sid}",
            cookies=self._cookies,
            params=params,
        )
        # resp.raise_for_status()
        return resp.json()

    def get_resource(self, resource_id: int, space_id: int = None, **params):
        sid = space_id if space_id is not None else self.space_id
        req_url = self.base_url + f"/api/data/{sid}/{resource_id}"
        print(f"Making request to <{req_url}>")
        resp = requests.get(
            req_url,
            cookies=self._cookies,
            params=params,
        )
        # resp.raise_for_status()
        return resp.json()
