import base64
from dataclasses import dataclass, field

import requests
from supabase import Client


@dataclass
class DiscourseGraphAPI:
    base_url: str
    space_id: int
    password: str
    platform: str = field(default="Obsidian")
    cookies: dict = field(init=False)
    
    def get_client(self):
        resp = requests.get(self.base_url + "/api/supabase/env")
        env = resp.json()
        return Client(
            supabase_url=env["SUPABASE_URL"],
            supabase_key=env["SUPABASE_PUBLISHABLE_KEY"]
        )
    
    @staticmethod
    def space_anon_user_email(platform: str, spaceId: int) -> str:
        return f"{platform.lower()}-{spaceId}-anon@database.discoursegraphs.com"

    def login(self, platform: str, space_id: int, password: str):
        client = self.get_client()
        
        email = self.space_anon_user_email(platform, space_id)
        # Use credentials to get a session, convert it into a cookie
        auth_resp = client.auth.sign_in_with_password(dict(
            email=email, password=password))
        cookie = "base64-" + base64.b64encode(
            auth_resp.session.model_dump_json().encode("ascii")
        ).decode("ascii")
        hostname = client.supabase_url.host.split(".")[0]
        cookiename = f"sb-{hostname}-auth-token"
        self.cookies = {cookiename: cookie}
    
    def create_space(self, platform: str, url: str, name: str, password: str) -> int:
        resp = requests.post(
            self.base_url + "/api/supabase/space",
            json=dict(
                name=name,
                platform=platform,
                url=url,
                password=password
            )
        )
        resp.json()["id"]

    def get_space(self, **kwargs):
        resp = requests.get(
            self.base_url + f"/api/data/{self.space_id}",
            cookies=self.cookies,
            params=kwargs
        )
        return resp.json()
    
    def get_resource(self, resource_id: int, **kwargs):
        resp = requests.get(
            self.base_url + f"/api/data/{self.space_id}/{resource_id}",
            cookies=self.cookies,
            params=kwargs
        )
        return resp.json()
    
    
    
