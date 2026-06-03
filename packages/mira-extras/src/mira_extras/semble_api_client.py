"""[LLM GENERATED IMPLEMENTATION] Simple httpx client for the Semble API (api.dev.semble.so)."""

from typing import Any, Literal, Optional
import httpx

BASE_URL = "https://api.dev.semble.so/xrpc"

UrlType = Literal["article", "link", "book", "research", "audio", "video", "social", "event", "software"]
SortOrder = Literal["asc", "desc"]
AccessType = Literal["OPEN", "CLOSED"]
TargetType = Literal["USER", "COLLECTION"]
ConnectionType = Literal["SUPPORTS", "OPPOSES", "ADDRESSES", "HELPFUL", "LEADS_TO", "RELATED", "SUPPLEMENT", "EXPLAINER"]
SourceTargetType = Literal["URL", "CARD"]
Direction = Literal["forward", "backward", "both"]


class SembleAPIError(Exception):
    def __init__(self, status_code: int, body: Any):
        self.status_code = status_code
        self.body = body
        super().__init__(f"HTTP {status_code}: {body}")


class SembleClient:
    def __init__(self, api_key: str, base_url: str = BASE_URL):
        self._client = httpx.Client(
            base_url=base_url,
            headers={"x-api-key": api_key},
        )

    def _get(self, path: str, params: Optional[dict] = None) -> Any:
        resp = self._client.get(path, params={k: v for k, v in (params or {}).items() if v is not None})
        self._raise_for_status(resp)
        return resp.json()

    def _post(self, path: str, body: Optional[dict] = None) -> Any:
        resp = self._client.post(path, json={k: v for k, v in (body or {}).items() if v is not None})
        self._raise_for_status(resp)
        return resp.json()

    def _raise_for_status(self, resp: httpx.Response) -> None:
        if resp.is_error:
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            raise SembleAPIError(resp.status_code, body)

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # ── Cards ──────────────────────────────────────────────────────────────

    def add_url(
        self,
        url: str,
        note: Optional[str] = None,
        collection_ids: Optional[list[str]] = None,
        via_card_id: Optional[str] = None,
    ) -> dict:
        return self._post("/network.cosmik.card.addUrl", {
            "url": url,
            "note": note,
            "collectionIds": collection_ids,
            "viaCardId": via_card_id,
        })

    def update_url_associations(
        self,
        card_id: str,
        note: Optional[str] = None,
        add_to_collections: Optional[list[str]] = None,
        remove_from_collections: Optional[list[str]] = None,
        via_card_id: Optional[str] = None,
    ) -> dict:
        return self._post("/network.cosmik.card.updateUrlAssociations", {
            "cardId": card_id,
            "note": note,
            "addToCollections": add_to_collections,
            "removeFromCollections": remove_from_collections,
            "viaCardId": via_card_id,
        })

    def list_my_cards(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
        url_type: Optional[UrlType] = None,
        uncollected: Optional[bool] = None,
    ) -> dict:
        return self._get("/network.cosmik.card.listMine", {
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
            "sortOrder": sort_order,
            "urlType": url_type,
            "uncollected": uncollected,
        })

    def get_url_metadata(self, url: str, include_stats: Optional[bool] = None) -> dict:
        return self._get("/network.cosmik.card.getUrlMetadata", {"url": url, "includeStats": include_stats})

    def get_library_status(self, url: str) -> dict:
        return self._get("/network.cosmik.card.getLibraryStatus", {"url": url})

    def get_libraries_for_url(
        self,
        url: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
    ) -> dict:
        return self._get("/network.cosmik.card.getLibrariesForUrl", {
            "url": url,
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        })

    def get_note_cards_for_url(
        self,
        url: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
    ) -> dict:
        return self._get("/network.cosmik.card.getNoteCardsForUrl", {
            "url": url,
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        })

    def search_cards(
        self,
        search_query: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
        url_type: Optional[UrlType] = None,
    ) -> dict:
        return self._get("/network.cosmik.card.search", {
            "searchQuery": search_query,
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
            "sortOrder": sort_order,
            "urlType": url_type,
        })

    def get_card(self, card_id: str) -> dict:
        return self._get("/network.cosmik.card.get", {"cardId": card_id})

    def get_card_libraries(self, card_id: str) -> dict:
        return self._get("/network.cosmik.card.getLibraries", {"cardId": card_id})

    def update_note(self, card_id: str, note: str) -> dict:
        return self._post("/network.cosmik.card.updateNote", {"cardId": card_id, "note": note})

    def remove_from_library(self, card_id: str) -> dict:
        return self._post("/network.cosmik.card.removeFromLibrary", {"cardId": card_id})

    def list_cards_by_user(
        self,
        identifier: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
        url_type: Optional[UrlType] = None,
        uncollected: Optional[bool] = None,
    ) -> dict:
        return self._get("/network.cosmik.card.listByUser", {
            "identifier": identifier,
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
            "sortOrder": sort_order,
            "urlType": url_type,
            "uncollected": uncollected,
        })

    # ── Collections ────────────────────────────────────────────────────────

    def list_my_collections(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
        search_text: Optional[str] = None,
    ) -> dict:
        return self._get("/network.cosmik.collection.listMine", {
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
            "sortOrder": sort_order,
            "searchText": search_text,
        })

    def create_collection(
        self,
        name: str,
        description: Optional[str] = None,
        access_type: Optional[AccessType] = None,
    ) -> dict:
        return self._post("/network.cosmik.collection.create", {
            "name": name,
            "description": description,
            "accessType": access_type,
        })

    def get_collections_for_url(
        self,
        url: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
    ) -> dict:
        return self._get("/network.cosmik.collection.getForUrl", {
            "url": url,
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        })

    def search_collections(
        self,
        search_text: Optional[str] = None,
        identifier: Optional[str] = None,
        access_type: Optional[AccessType] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
    ) -> dict:
        return self._get("/network.cosmik.collection.search", {
            "searchText": search_text,
            "identifier": identifier,
            "accessType": access_type,
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        })

    def get_collection(
        self,
        collection_id: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
        url_type: Optional[UrlType] = None,
    ) -> dict:
        return self._get("/network.cosmik.collection.get", {
            "collectionId": collection_id,
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
            "sortOrder": sort_order,
            "urlType": url_type,
        })

    def update_collection(
        self,
        collection_id: str,
        name: str,
        description: Optional[str] = None,
        access_type: Optional[AccessType] = None,
    ) -> dict:
        return self._post("/network.cosmik.collection.update", {
            "collectionId": collection_id,
            "name": name,
            "description": description,
            "accessType": access_type,
        })

    def delete_collection(self, collection_id: str) -> dict:
        return self._post("/network.cosmik.collection.delete", {"collectionId": collection_id})

    def list_collections_by_user(
        self,
        identifier: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
        search_text: Optional[str] = None,
    ) -> dict:
        return self._get("/network.cosmik.collection.listByUser", {
            "identifier": identifier,
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
            "sortOrder": sort_order,
            "searchText": search_text,
        })

    def get_collection_by_at_uri(
        self,
        handle: str,
        record_key: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
        url_type: Optional[UrlType] = None,
    ) -> dict:
        return self._get("/network.cosmik.collection.getByAtUri", {
            "handle": handle,
            "recordKey": record_key,
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
            "sortOrder": sort_order,
            "urlType": url_type,
        })

    def list_contributed_collections(
        self,
        identifier: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
    ) -> dict:
        return self._get("/network.cosmik.collection.listContributed", {
            "identifier": identifier,
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        })

    def get_collection_followers(
        self,
        collection_id: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict:
        return self._get("/network.cosmik.collection.getFollowers", {
            "collectionId": collection_id,
            "page": page,
            "limit": limit,
        })

    def get_collection_follower_count(self, collection_id: str) -> dict:
        return self._get("/network.cosmik.collection.getFollowerCount", {"collectionId": collection_id})

    def get_collection_contributors(
        self,
        collection_id: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict:
        return self._get("/network.cosmik.collection.getContributors", {
            "collectionId": collection_id,
            "page": page,
            "limit": limit,
        })

    # ── Actor ──────────────────────────────────────────────────────────────

    def get_my_profile(self, include_stats: Optional[bool] = None) -> dict:
        return self._get("/network.cosmik.actor.getMyProfile", {"includeStats": include_stats})

    def get_profile(self, identifier: str, include_stats: Optional[bool] = None) -> dict:
        return self._get("/network.cosmik.actor.getProfile", {"identifier": identifier, "includeStats": include_stats})

    # ── Graph ──────────────────────────────────────────────────────────────

    def follow(self, target_id: str, target_type: TargetType) -> dict:
        return self._post("/network.cosmik.graph.follow", {"targetId": target_id, "targetType": target_type})

    def unfollow(self, target_id: str, target_type: TargetType) -> dict:
        return self._post("/network.cosmik.graph.unfollow", {"targetId": target_id, "targetType": target_type})

    def get_following(
        self,
        identifier: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict:
        return self._get("/network.cosmik.graph.getFollowing", {"identifier": identifier, "page": page, "limit": limit})

    def get_followers(
        self,
        identifier: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict:
        return self._get("/network.cosmik.graph.getFollowers", {"identifier": identifier, "page": page, "limit": limit})

    def get_following_collections(
        self,
        identifier: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict:
        return self._get("/network.cosmik.graph.getFollowingCollections", {
            "identifier": identifier,
            "page": page,
            "limit": limit,
        })

    def get_following_count(self, identifier: str) -> dict:
        return self._get("/network.cosmik.graph.getFollowingCount", {"identifier": identifier})

    def get_followers_count(self, identifier: str) -> dict:
        return self._get("/network.cosmik.graph.getFollowersCount", {"identifier": identifier})

    def get_following_collections_count(self, identifier: str) -> dict:
        return self._get("/network.cosmik.graph.getFollowingCollectionsCount", {"identifier": identifier})

    # ── Feed ───────────────────────────────────────────────────────────────

    def get_global_feed(self, page: Optional[int] = None, limit: Optional[int] = None) -> dict:
        return self._get("/network.cosmik.feed.getGlobal", {"page": page, "limit": limit})

    def get_following_feed(self, page: Optional[int] = None, limit: Optional[int] = None) -> dict:
        return self._get("/network.cosmik.feed.getFollowing", {"page": page, "limit": limit})

    # ── Notifications ──────────────────────────────────────────────────────

    def list_notifications(self, page: Optional[int] = None, limit: Optional[int] = None) -> dict:
        return self._get("/network.cosmik.notification.list", {"page": page, "limit": limit})

    def get_unread_count(self) -> dict:
        return self._get("/network.cosmik.notification.getUnreadCount")

    def mark_read(self, notification_ids: list[str]) -> dict:
        return self._post("/network.cosmik.notification.markRead", {"notificationIds": notification_ids})

    def mark_all_read(self) -> dict:
        return self._post("/network.cosmik.notification.markAllRead", {})

    # ── Connections ────────────────────────────────────────────────────────

    def get_connections_for_url(
        self,
        url: str,
        direction: Optional[Direction] = None,
        connection_types: Optional[list[ConnectionType]] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
    ) -> dict:
        return self._get("/network.cosmik.connection.getForUrl", {
            "url": url,
            "direction": direction,
            "connectionTypes": connection_types,
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        })

    def create_connection(
        self,
        source_type: SourceTargetType,
        source_value: str,
        target_type: SourceTargetType,
        target_value: str,
        connection_type: Optional[ConnectionType] = None,
        note: Optional[str] = None,
    ) -> dict:
        return self._post("/network.cosmik.connection.create", {
            "sourceType": source_type,
            "sourceValue": source_value,
            "targetType": target_type,
            "targetValue": target_value,
            "connectionType": connection_type,
            "note": note,
        })

    def list_connections_by_user(
        self,
        identifier: str,
        connection_types: Optional[list[ConnectionType]] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
    ) -> dict:
        return self._get("/network.cosmik.connection.listByUser", {
            "identifier": identifier,
            "connectionTypes": connection_types,
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        })

    def update_connection(
        self,
        connection_id: str,
        connection_type: Optional[ConnectionType] = None,
        note: Optional[str] = None,
        remove_note: Optional[bool] = None,
        swap: Optional[bool] = None,
    ) -> dict:
        return self._post("/network.cosmik.connection.update", {
            "connectionId": connection_id,
            "connectionType": connection_type,
            "note": note,
            "removeNote": remove_note,
            "swap": swap,
        })

    def delete_connection(self, connection_id: str) -> dict:
        return self._post("/network.cosmik.connection.delete", {"connectionId": connection_id})

    # ── Search ─────────────────────────────────────────────────────────────

    def get_similar_urls(
        self,
        url: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
        threshold: Optional[float] = None,
        url_type: Optional[UrlType] = None,
    ) -> dict:
        return self._get("/network.cosmik.search.getSimilarUrls", {
            "url": url,
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
            "sortOrder": sort_order,
            "threshold": threshold,
            "urlType": url_type,
        })

    def semantic_search(
        self,
        query: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[SortOrder] = None,
        threshold: Optional[float] = None,
        url_type: Optional[UrlType] = None,
        identifier: Optional[str] = None,
    ) -> dict:
        return self._get("/network.cosmik.search.semantic", {
            "query": query,
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
            "sortOrder": sort_order,
            "threshold": threshold,
            "urlType": url_type,
            "identifier": identifier,
        })

    def get_accounts(
        self,
        term: Optional[str] = None,
        q: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> dict:
        return self._get("/network.cosmik.search.getAccounts", {
            "term": term,
            "q": q,
            "limit": limit,
            "cursor": cursor,
        })
