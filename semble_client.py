"""LLM generated translation of @cosmik.network/semble-pds-client into Python."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import requests
from atproto import Client


BASE_NSID = "network.cosmik"
CARD_COLLECTION = f"{BASE_NSID}.card"
COLLECTION_COLLECTION = f"{BASE_NSID}.collection"
COLLECTION_LINK_COLLECTION = f"{BASE_NSID}.collectionLink"
CONNECTION_COLLECTION = f"{BASE_NSID}.connection"


@dataclass
class StrongRef:
    uri: str
    cid: str


@dataclass
class CardRecord:
    uri: str
    cid: str
    value: dict


@dataclass
class GetCardsResult:
    records: list[CardRecord]
    cursor: Optional[str] = None


@dataclass
class CollectionRecord:
    uri: str
    cid: str
    value: dict


@dataclass
class GetCollectionsResult:
    records: list[CollectionRecord]
    cursor: Optional[str] = None


@dataclass
class ConnectionRecord:
    uri: str
    cid: str
    value: dict


@dataclass
class GetConnectionsResult:
    records: list[ConnectionRecord]
    cursor: Optional[str] = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _rkey(uri: str) -> str:
    rkey = uri.split("/")[-1]
    if not rkey:
        raise ValueError(f"Invalid URI format: {uri}")
    return rkey


def _fetch_url_metadata(url: str) -> Optional[dict]:
    try:
        resp = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
            allow_redirects=True,
        )
        from html.parser import HTMLParser

        class MetaParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.meta = {}
                self.title = None
                self._in_title = False

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if tag == "title":
                    self._in_title = True
                if tag == "meta":
                    name = attrs.get("property") or attrs.get("name", "")
                    content = attrs.get("content", "")
                    self.meta[name] = content

            def handle_data(self, data):
                if self._in_title and self.title is None:
                    self.title = data.strip()

            def handle_endtag(self, tag):
                if tag == "title":
                    self._in_title = False

        parser = MetaParser()
        parser.feed(resp.text)
        m = parser.meta

        return {
            "$type": f"{BASE_NSID}.card#urlMetadata",
            "title": m.get("og:title") or parser.title,
            "description": m.get("og:description") or m.get("description"),
            "author": m.get("author"),
            "siteName": m.get("og:site_name"),
            "imageUrl": m.get("og:image"),
            "type": m.get("og:type") or "link",
            "retrievedAt": _now(),
        }
    except Exception:
        return None


class SemblePDSClient:
    def __init__(self, service: str):
        self._client = Client(base_url=service)

    def login(self, identifier: str, password: str) -> None:
        self._client.login(identifier, password)

    def _require_auth(self):
        if not self._client.me:
            raise RuntimeError("Not authenticated. Call login() first.")

    # --- Cards ---

    def create_card(
        self,
        url: str,
        note: Optional[str] = None,
        via_card: Optional[StrongRef] = None,
    ) -> dict:
        self._require_auth()
        metadata = _fetch_url_metadata(url)
        content = {
            "$type": f"{BASE_NSID}.card#urlContent",
            "url": url,
            **({"metadata": metadata} if metadata else {}),
        }
        record = {
            "$type": CARD_COLLECTION,
            "type": "URL",
            "url": url,
            "content": content,
            "createdAt": _now(),
        }
        if via_card:
            record["provenance"] = {
                "$type": f"{BASE_NSID}.defs#provenance",
                "via": {"uri": via_card.uri, "cid": via_card.cid},
            }

        resp = self._client.com.atproto.repo.create_record({
            "repo": self._client.me.did,
            "collection": CARD_COLLECTION,
            "record": record,
        })
        url_card = StrongRef(uri=resp.uri, cid=resp.cid)

        note_card = None
        if note:
            note_record = {
                "$type": CARD_COLLECTION,
                "type": "NOTE",
                "url": url,
                "content": {
                    "$type": f"{BASE_NSID}.card#noteContent",
                    "text": note,
                },
                "parentCard": {"uri": url_card.uri, "cid": url_card.cid},
                "createdAt": _now(),
            }
            note_resp = self._client.com.atproto.repo.create_record({
                "repo": self._client.me.did,
                "collection": CARD_COLLECTION,
                "record": note_record,
            })
            note_card = StrongRef(uri=note_resp.uri, cid=note_resp.cid)

        return {"url_card": url_card, "note_card": note_card}

    def add_note_to_card(self, parent_card: StrongRef, note_text: str) -> StrongRef:
        self._require_auth()
        record = {
            "$type": CARD_COLLECTION,
            "type": "NOTE",
            "content": {
                "$type": f"{BASE_NSID}.card#noteContent",
                "text": note_text,
            },
            "parentCard": {"uri": parent_card.uri, "cid": parent_card.cid},
            "createdAt": _now(),
        }
        resp = self._client.com.atproto.repo.create_record({
            "repo": self._client.me.did,
            "collection": CARD_COLLECTION,
            "record": record,
        })
        return StrongRef(uri=resp.uri, cid=resp.cid)

    def update_note(self, note_ref: StrongRef, updated_text: str) -> None:
        self._require_auth()
        rkey = _rkey(note_ref.uri)
        existing = self._client.com.atproto.repo.get_record({
            "repo": self._client.me.did,
            "collection": CARD_COLLECTION,
            "rkey": rkey,
        })
        record = {
            **existing.value,
            "content": {
                "$type": f"{BASE_NSID}.card#noteContent",
                "text": updated_text,
            },
            "updatedAt": _now(),
        }
        self._client.com.atproto.repo.put_record({
            "repo": self._client.me.did,
            "collection": CARD_COLLECTION,
            "rkey": rkey,
            "record": record,
        })

    def delete_card(self, card_ref: StrongRef) -> None:
        self._require_auth()
        self._client.com.atproto.repo.delete_record({
            "repo": self._client.me.did,
            "collection": CARD_COLLECTION,
            "rkey": _rkey(card_ref.uri),
        })

    def get_card(self, card_ref: StrongRef) -> CardRecord:
        self._require_auth()
        resp = self._client.com.atproto.repo.get_record({
            "repo": self._client.me.did,
            "collection": CARD_COLLECTION,
            "rkey": _rkey(card_ref.uri),
        })
        return CardRecord(uri=resp.uri, cid=resp.cid or "", value=resp.value)

    def get_my_cards(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        reverse: Optional[bool] = None,
    ) -> GetCardsResult:
        self._require_auth()
        params = {"repo": self._client.me.did, "collection": CARD_COLLECTION}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if reverse is not None:
            params["reverse"] = reverse
        resp = self._client.com.atproto.repo.list_records(params)
        return GetCardsResult(
            cursor=resp.cursor,
            records=[CardRecord(uri=r.uri, cid=r.cid, value=r.value) for r in resp.records],
        )

    def get_cards(
        self,
        did: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        reverse: Optional[bool] = None,
    ) -> GetCardsResult:
        params = {"repo": did, "collection": CARD_COLLECTION}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if reverse is not None:
            params["reverse"] = reverse
        resp = self._client.com.atproto.repo.list_records(params)
        return GetCardsResult(
            cursor=resp.cursor,
            records=[CardRecord(uri=r.uri, cid=r.cid, value=r.value) for r in resp.records],
        )

    # --- Batch ---

    def create_cards(self, cards: list[dict]) -> list[StrongRef]:
        """
        cards: list of dicts with keys: url (required), note (optional), via_card (optional StrongRef)
        Returns list of StrongRefs for all created records (url cards first, then note cards).
        """
        self._require_auth()

        metadatas = [_fetch_url_metadata(c["url"]) for c in cards]

        url_writes = []
        for card, metadata in zip(cards, metadatas):
            content = {
                "$type": f"{BASE_NSID}.card#urlContent",
                "url": card["url"],
                **({"metadata": metadata} if metadata else {}),
            }
            record = {
                "$type": CARD_COLLECTION,
                "type": "URL",
                "url": card["url"],
                "content": content,
                "createdAt": _now(),
            }
            if card.get("via_card"):
                record["provenance"] = {
                    "$type": f"{BASE_NSID}.defs#provenance",
                    "via": {"uri": card["via_card"].uri, "cid": card["via_card"].cid},
                }
            url_writes.append({
                "$type": "com.atproto.repo.applyWrites#create",
                "collection": CARD_COLLECTION,
                "value": record,
            })

        url_resp = self._client.com.atproto.repo.apply_writes({
            "repo": self._client.me.did,
            "writes": url_writes,
        })
        url_results = [StrongRef(uri=r.uri, cid=r.cid) for r in (url_resp.results or [])]

        note_writes = []
        for card, url_ref in zip(cards, url_results):
            if card.get("note"):
                note_writes.append({
                    "$type": "com.atproto.repo.applyWrites#create",
                    "collection": CARD_COLLECTION,
                    "value": {
                        "$type": CARD_COLLECTION,
                        "type": "NOTE",
                        "url": card["url"],
                        "content": {
                            "$type": f"{BASE_NSID}.card#noteContent",
                            "text": card["note"],
                        },
                        "parentCard": {"uri": url_ref.uri, "cid": url_ref.cid},
                        "createdAt": _now(),
                    },
                })

        note_results = []
        if note_writes:
            note_resp = self._client.com.atproto.repo.apply_writes({
                "repo": self._client.me.did,
                "writes": note_writes,
            })
            note_results = [StrongRef(uri=r.uri, cid=r.cid) for r in (note_resp.results or [])]

        return url_results + note_results

    # --- Collections ---

    def create_collection(self, name: str, description: Optional[str] = None) -> StrongRef:
        self._require_auth()
        now = _now()
        record = {
            "$type": COLLECTION_COLLECTION,
            "name": name,
            "accessType": "CLOSED",
            "collaborators": [],
            "createdAt": now,
            "updatedAt": now,
        }
        if description:
            record["description"] = description
        resp = self._client.com.atproto.repo.create_record({
            "repo": self._client.me.did,
            "collection": COLLECTION_COLLECTION,
            "record": record,
        })
        return StrongRef(uri=resp.uri, cid=resp.cid)

    def update_collection(
        self, collection_ref: StrongRef, name: str, description: Optional[str] = None
    ) -> None:
        self._require_auth()
        now = _now()
        record = {
            "$type": COLLECTION_COLLECTION,
            "name": name,
            "accessType": "CLOSED",
            "collaborators": [],
            "createdAt": now,
            "updatedAt": now,
        }
        if description:
            record["description"] = description
        self._client.com.atproto.repo.put_record({
            "repo": self._client.me.did,
            "collection": COLLECTION_COLLECTION,
            "rkey": _rkey(collection_ref.uri),
            "record": record,
        })

    def delete_collection(self, collection_ref: StrongRef) -> None:
        self._require_auth()
        self._client.com.atproto.repo.delete_record({
            "repo": self._client.me.did,
            "collection": COLLECTION_COLLECTION,
            "rkey": _rkey(collection_ref.uri),
        })

    def get_collection(self, collection_ref: StrongRef) -> CollectionRecord:
        self._require_auth()
        resp = self._client.com.atproto.repo.get_record({
            "repo": self._client.me.did,
            "collection": COLLECTION_COLLECTION,
            "rkey": _rkey(collection_ref.uri),
        })
        return CollectionRecord(uri=resp.uri, cid=resp.cid or "", value=resp.value)

    def get_my_collections(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        reverse: Optional[bool] = None,
    ) -> GetCollectionsResult:
        self._require_auth()
        params = {"repo": self._client.me.did, "collection": COLLECTION_COLLECTION}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if reverse is not None:
            params["reverse"] = reverse
        resp = self._client.com.atproto.repo.list_records(params)
        return GetCollectionsResult(
            cursor=resp.cursor,
            records=[CollectionRecord(uri=r.uri, cid=r.cid, value=r.value) for r in resp.records],
        )

    def get_collections(
        self,
        did: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        reverse: Optional[bool] = None,
    ) -> GetCollectionsResult:
        params = {"repo": did, "collection": COLLECTION_COLLECTION}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if reverse is not None:
            params["reverse"] = reverse
        resp = self._client.com.atproto.repo.list_records(params)
        return GetCollectionsResult(
            cursor=resp.cursor,
            records=[CollectionRecord(uri=r.uri, cid=r.cid, value=r.value) for r in resp.records],
        )

    def create_collections(self, collections: list[dict]) -> list[StrongRef]:
        """
        collections: list of dicts with keys: name (required), description (optional)
        """
        self._require_auth()
        now = _now()
        writes = []
        for col in collections:
            record = {
                "$type": COLLECTION_COLLECTION,
                "name": col["name"],
                "accessType": "CLOSED",
                "collaborators": [],
                "createdAt": now,
                "updatedAt": now,
            }
            if col.get("description"):
                record["description"] = col["description"]
            writes.append({
                "$type": "com.atproto.repo.applyWrites#create",
                "collection": COLLECTION_COLLECTION,
                "value": record,
            })
        resp = self._client.com.atproto.repo.apply_writes({
            "repo": self._client.me.did,
            "writes": writes,
        })
        return [StrongRef(uri=r.uri, cid=r.cid) for r in (resp.results or [])]

    # --- Connections ---

    def create_connection(
        self,
        source: str,
        target: str,
        note: Optional[str] = None,
        connection_type: Optional[str] = None,
    ) -> StrongRef:
        self._require_auth()
        now = _now()
        record = {
            "$type": CONNECTION_COLLECTION,
            "source": source,
            "target": target,
            "createdAt": now,
            "updatedAt": now,
        }
        if note:
            record["note"] = note
        if connection_type:
            record["connectionType"] = connection_type
        resp = self._client.com.atproto.repo.create_record({
            "repo": self._client.me.did,
            "collection": CONNECTION_COLLECTION,
            "record": record,
        })
        return StrongRef(uri=resp.uri, cid=resp.cid)

    def update_connection(
        self,
        connection_ref: StrongRef,
        source: Optional[str] = None,
        target: Optional[str] = None,
        note: Optional[str] = None,
        connection_type: Optional[str] = None,
    ) -> None:
        self._require_auth()
        rkey = _rkey(connection_ref.uri)
        existing = self._client.com.atproto.repo.get_record({
            "repo": self._client.me.did,
            "collection": CONNECTION_COLLECTION,
            "rkey": rkey,
        })
        record = {
            **existing.value,
            "updatedAt": _now(),
        }
        if source is not None:
            record["source"] = source
        if target is not None:
            record["target"] = target
        if note is not None:
            record["note"] = note
        if connection_type is not None:
            record["connectionType"] = connection_type
        self._client.com.atproto.repo.put_record({
            "repo": self._client.me.did,
            "collection": CONNECTION_COLLECTION,
            "rkey": rkey,
            "record": record,
        })

    def delete_connection(self, connection_ref: StrongRef) -> None:
        self._require_auth()
        self._client.com.atproto.repo.delete_record({
            "repo": self._client.me.did,
            "collection": CONNECTION_COLLECTION,
            "rkey": _rkey(connection_ref.uri),
        })

    def get_connection(self, connection_ref: StrongRef) -> ConnectionRecord:
        self._require_auth()
        resp = self._client.com.atproto.repo.get_record({
            "repo": self._client.me.did,
            "collection": CONNECTION_COLLECTION,
            "rkey": _rkey(connection_ref.uri),
        })
        return ConnectionRecord(uri=resp.uri, cid=resp.cid or "", value=resp.value)

    def get_my_connections(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        reverse: Optional[bool] = None,
    ) -> GetConnectionsResult:
        self._require_auth()
        params = {"repo": self._client.me.did, "collection": CONNECTION_COLLECTION}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if reverse is not None:
            params["reverse"] = reverse
        resp = self._client.com.atproto.repo.list_records(params)
        return GetConnectionsResult(
            cursor=resp.cursor,
            records=[ConnectionRecord(uri=r.uri, cid=r.cid, value=r.value) for r in resp.records],
        )

    def get_connections(
        self,
        did: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        reverse: Optional[bool] = None,
    ) -> GetConnectionsResult:
        params = {"repo": did, "collection": CONNECTION_COLLECTION}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if reverse is not None:
            params["reverse"] = reverse
        resp = self._client.com.atproto.repo.list_records(params)
        return GetConnectionsResult(
            cursor=resp.cursor,
            records=[ConnectionRecord(uri=r.uri, cid=r.cid, value=r.value) for r in resp.records],
        )

    # --- Collection Links ---

    def add_card_to_collection(
        self,
        card: StrongRef,
        collection: StrongRef,
        via_card: Optional[StrongRef] = None,
    ) -> StrongRef:
        self._require_auth()
        now = _now()
        record = {
            "$type": COLLECTION_LINK_COLLECTION,
            "card": {"uri": card.uri, "cid": card.cid},
            "collection": {"uri": collection.uri, "cid": collection.cid},
            "addedBy": self._client.me.did,
            "addedAt": now,
            "createdAt": now,
        }
        if via_card:
            record["provenance"] = {
                "$type": f"{BASE_NSID}.defs#provenance",
                "via": {"uri": via_card.uri, "cid": via_card.cid},
            }
        resp = self._client.com.atproto.repo.create_record({
            "repo": self._client.me.did,
            "collection": COLLECTION_LINK_COLLECTION,
            "record": record,
        })
        return StrongRef(uri=resp.uri, cid=resp.cid)

    def remove_card_from_collection(self, collection_link_ref: StrongRef) -> None:
        self._require_auth()
        self._client.com.atproto.repo.delete_record({
            "repo": self._client.me.did,
            "collection": COLLECTION_LINK_COLLECTION,
            "rkey": _rkey(collection_link_ref.uri),
        })

    def add_cards_to_collection(
        self,
        collection: StrongRef,
        cards: list[StrongRef],
        via_card: Optional[StrongRef] = None,
    ) -> list[StrongRef]:
        self._require_auth()
        now = _now()
        writes = []
        for card in cards:
            record = {
                "$type": COLLECTION_LINK_COLLECTION,
                "card": {"uri": card.uri, "cid": card.cid},
                "collection": {"uri": collection.uri, "cid": collection.cid},
                "addedBy": self._client.me.did,
                "addedAt": now,
                "createdAt": now,
            }
            if via_card:
                record["provenance"] = {
                    "$type": f"{BASE_NSID}.defs#provenance",
                    "via": {"uri": via_card.uri, "cid": via_card.cid},
                }
            writes.append({
                "$type": "com.atproto.repo.applyWrites#create",
                "collection": COLLECTION_LINK_COLLECTION,
                "value": record,
            })
        resp = self._client.com.atproto.repo.apply_writes({
            "repo": self._client.me.did,
            "writes": writes,
        })
        return [StrongRef(uri=r.uri, cid=r.cid) for r in (resp.results or [])]
