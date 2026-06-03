import base64
import json
from dataclasses import dataclass, field
from typing import Dict

import requests
from supabase import Client


@dataclass
class DiscourseGraphClient:
    base_url: str
    public_key: str = field(repr=False)

    def __init__(self, base_url):
        self.base_url = base_url
        self.setup()

    def setup(self):
        r = requests.get(self.base_url + "/api/supabase/env")
        e = r.json()
        self.supabase_url = e["SUPABASE_URL"]
        self.public_key = e["SUPABASE_PUBLISHABLE_KEY"]

    def __enter__(self):
        return self.setup()

    def __exit__(self, *_):
        pass

    def make_connection(self):
        return Client(self.supabase_url, self.public_key)

    def create_space(
        self, name: str, url: str, password: str, platform: str = "Obsidian"
    ) -> "DiscourseGraphSpaceClient":
        """Create a new space and return a client for it, ready to connect."""
        space_client = DiscourseGraphSpaceClient(
            base_client=self, name=name, platform=platform, url=url, password=password
        )
        space_client.connect()
        return space_client


@dataclass
class DiscourseGraphSpaceClient:
    base_client: DiscourseGraphClient
    url: str
    name: str
    password: str
    platform: str = "Obsidian"
    groups: Dict[str, str] = field(
        init=False, default_factory=lambda: dict(), repr=False
    )

    space_id: int = field(init=False, default=None)
    pseudo_account_id: str = field(init=False, default=None)
    _supabase: Client = field(init=False, default=None, repr=False)
    _cookies: dict = field(init=False, default_factory=dict, repr=False)

    def connect(self):
        """Fetch supabase env, authenticate, and store session cookies."""
        self._supabase = self.base_client.make_connection()
        if not self.space_id:
            self.create_space()
        email = (
            f"{self.platform.lower()}-{self.space_id}-anon@database.discoursegraphs.com"
        )
        auth = self._supabase.auth.sign_in_with_password(
            dict(email=email, password=self.password)
        )
        self.pseudo_account_id = auth.user.id
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

    def create_space(self):
        """Create a new space"""
        resp = requests.post(
            self.base_client.base_url + "/api/supabase/space",
            json=dict(
                name=self.name,
                platform=self.platform,
                url=self.url,
                password=self.password,
            ),
        )
        resp.raise_for_status()
        self.space_id = resp.json()["id"]
        return self

    def get_space(self, space_id: int = None, **params):
        sid = space_id if space_id is not None else self.space_id
        resp = requests.get(
            self.base_client.base_url + f"/api/data/{sid}",
            cookies=self._cookies,
            params=params,
        )
        resp.raise_for_status()
        return resp.json()

    def get_resource(self, resource_id: int, space_id: int = None, **params):
        sid = space_id if space_id is not None else self.space_id
        req_url = self.base_client.base_url + f"/api/data/{sid}/{resource_id}"
        resp = requests.get(
            req_url,
            cookies=self._cookies,
            params=params,
        )
        resp.raise_for_status()
        return resp.json()

    def _create_group(self, group_name: str, partial: bool = False):
        resp = self._supabase.table("my_groups").select().execute()
        resp = self._supabase.functions.invoke(
            "create-group", dict(body=dict(name=group_name))
        )
        group_id = json.loads(resp.decode("ascii"))["group_id"]
        self.groups[group_name] = group_id
        # Then decide how the group can view your space
        self.share_space(group_name, partial)
        return group_id

    def get_group(self, group_name: str):
        if group_name not in self.groups:
            resp = (
                self._supabase.table("my_groups")
                .select("id")
                .eq("name", group_name)
                .maybe_single()
                .execute()
            )
            if resp and resp.data:
                self.groups[group_name] = resp.data["id"]
        return self.groups.get(group_name)

    def get_groups(self):
        resp = self._supabase.table("my_groups").select().execute()
        self.groups = {g["id"]: g["name"] for g in resp.data}
        return self.groups

    def get_group_member_data(self, group_name: str):
        group_id = self.get_group(group_name)
        assert group_id
        resp = (
            self._supabase.table("my_pseudo_accounts")
            .select()
            .eq("group_id", group_id)
            .execute()
        )
        return resp.data

    def get_or_create_group(self, group_name: str):
        if group_name in self.groups:
            return self.groups[group_name]
        group_id = self.get_group(group_name)
        if group_id:
            return group_id
        return self._create_group(group_name)

    def share_space(self, group_name: str, partial: bool = False):
        group_id = self.get_or_create_group(group_name)
        self._supabase.table("SpaceAccess").upsert(
            dict(
                account_uid=group_id,
                space_id=self.space_id,
                permissions="partial" if partial else "reader",
            ),
            on_conflict="account_uid,space_id",
        ).execute()

    def add_to_group_direct(
        self, group_name: str, account_id: str, admin: bool = False
    ):
        # print(f"Adding {account_id} to group '{group_name}'")
        group_id = self.get_or_create_group(group_name)
        resp = (
            self._supabase.table("group_membership")
            .upsert(
                dict(group_id=group_id, member_id=account_id, admin=admin),
                on_conflict="group_id,member_id",
            )
            .execute()
        )
        assert resp.data

    def create_group_invite(self, group_name: str, admin: bool = False):
        group_id = self.get_group(group_name)
        resp = self._supabase.rpc(
            "create_secret_token",
            dict(
                v_payload=dict(groupId=group_id, type="groupInvitation", admin=admin),
                expiry_interval="60d",
            ),
        ).execute()
        return resp.data

    def join_group(self, token: str):
        resp = self._supabase.rpc(
            "accept_group_invitation",
            dict(token=token),
        ).execute()
        # assert resp.data   # works once, not idempotent (oupse!)
