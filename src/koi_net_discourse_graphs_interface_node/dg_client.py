import base64
from dataclasses import dataclass, field
import threading
import time

import requests
from supabase import Client
from koi_net.components.interfaces import ThreadedComponent

from .config import DiscourseGraphsNodeConfig


@dataclass
class DGClient(ThreadedComponent):
    config: DiscourseGraphsNodeConfig

    exit_event: threading.Event = field(init=False, default_factory=threading.Event)
    
    def start(self):
        self.exit_event.clear()
        self.client = self.get_client()
        self.cookies = self.login(
            platform="Obsidian",
            password=self.config.discourse_graphs.password,
            space_id=self.config.discourse_graphs.space_id
        )
        super().start()
        
    def stop(self):
        self.exit_event.set()
        super().stop()
        
    def run(self):
        while not self.exit_event.is_set():
            start_time = time.monotonic()
            self.poll()
            elapsed = time.monotonic() - start_time
            wait_time = max(0, 5 - elapsed)
            self.exit_event.wait(wait_time)
            
    def poll(self):
        space = self.get_space()
        for res in space["container_of"]:
            resource_id = res["@id"].split(":")[1]
            resource = self.get_resource(resource_id)
            print(resource.get("title", "<unknown>"), resource_id)
    
    def get_client(self) -> Client:
        self.log.info("Getting client...")
        resp = requests.get(self.config.discourse_graphs.base_url + "/api/supabase/env")
        env = resp.json()
        return Client(
            supabase_url=env["SUPABASE_URL"],
            supabase_key=env["SUPABASE_PUBLISHABLE_KEY"]
        )
    
    @staticmethod
    def spaceAnonUserEmail(platform: str, spaceId: int) -> str:
        return f"{platform.lower()}-{spaceId}-anon@database.discoursegraphs.com"

    def login(self, platform: str, space_id: int, password: str, **_kwargs) -> dict:
        self.log.info("Logging in...")
        email = self.spaceAnonUserEmail(platform, space_id)
        # Use credentials to get a session, convert it into a cookie
        auth_resp = self.client.auth.sign_in_with_password(dict(email=email, password=password))
        cookie = "base64-" + base64.b64encode(
            auth_resp.session.model_dump_json().encode("ascii")
        ).decode("ascii")
        hostname = self.client.supabase_url.host.split(".")[0]
        cookiename = f"sb-{hostname}-auth-token"
        cookies = {cookiename: cookie}
        return cookies

    def get_space(self, **kwargs):
        resp = requests.get(
            self.config.discourse_graphs.base_url + f"/api/data/{self.config.discourse_graphs.space_id}",
            cookies=self.cookies,
            params=kwargs
        )
        return resp.json()
    
    def get_resource(self, resource_id: int, **kwargs):
        resp = requests.get(
            self.config.discourse_graphs.base_url + f"/api/data/{self.config.discourse_graphs.space_id}/{resource_id}",
            cookies=self.cookies,
            params=kwargs
        )
        return resp.json()