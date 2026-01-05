"""
CAR File Utilities for Bluesky Tracker

Provides functionality to:
1. Resolve DIDs to their Personal Data Server (PDS) endpoints
2. Download user repositories as CAR files (no auth required!)
3. Parse CAR files to extract follows, likes, posts, blocks, reposts

This enables:
- Historical timestamps (when actions actually happened)
- One API call instead of many paginated calls
- Access to blocks without authentication
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from functools import lru_cache

import requests

from config import Config
from http_client import create_retrying_session

logger = logging.getLogger(__name__)

# Constants
PLC_DIRECTORY_URL = "https://plc.directory"
DEFAULT_TIMEOUT = Config.CAR_DOWNLOAD_TIMEOUT  # CAR files can be large


class PDSResolver:
    """Resolve DIDs to their Personal Data Server endpoints."""

    def __init__(
        self,
        plc_directory_url: str = PLC_DIRECTORY_URL,
        session: Optional[requests.Session] = None,
    ):
        self.plc_directory_url = plc_directory_url
        self._cache: Dict[str, str] = {}
        self.session = session or create_retrying_session(
            max_retries=Config.MAX_RETRIES,
            backoff_factor=Config.RETRY_BACKOFF_FACTOR,
        )

    def resolve_handle_to_did(self, handle: str) -> str:
        """
        Resolve a Bluesky handle to its DID.

        Args:
            handle: Bluesky handle (e.g., "user.bsky.social")

        Returns:
            DID string (e.g., "did:plc:abc123...")
        """
        # Use public API to resolve handle
        url = f"https://public.api.bsky.app/xrpc/com.atproto.identity.resolveHandle"
        params = {"handle": handle}

        try:
            response = self.session.get(url, params=params, timeout=Config.HTTP_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            return data["did"]
        except requests.RequestException as e:
            logger.error(f"Failed to resolve handle {handle}: {e}")
            raise

    def resolve_did_to_pds(self, did: str) -> str:
        """
        Resolve a DID to its PDS endpoint.

        Args:
            did: DID string (e.g., "did:plc:abc123...")

        Returns:
            PDS URL (e.g., "https://bsky.social")
        """
        # Check cache first
        if did in self._cache:
            return self._cache[did]

        if did.startswith("did:plc:"):
            pds = self._resolve_plc_did(did)
        elif did.startswith("did:web:"):
            pds = self._resolve_web_did(did)
        else:
            raise ValueError(f"Unsupported DID method: {did}")

        # Cache the result
        self._cache[did] = pds
        return pds

    def _resolve_plc_did(self, did: str) -> str:
        """Resolve a did:plc: DID using the PLC directory."""
        url = f"{self.plc_directory_url}/{did}"

        try:
            response = self.session.get(url, timeout=Config.HTTP_TIMEOUT)
            response.raise_for_status()
            doc = response.json()

            # Find the atproto PDS service
            for service in doc.get("service", []):
                if service.get("type") == "AtprotoPersonalDataServer":
                    return service["serviceEndpoint"]

            raise ValueError(f"No PDS endpoint found in DID document for {did}")

        except requests.RequestException as e:
            logger.error(f"Failed to resolve DID {did}: {e}")
            raise

    def _resolve_web_did(self, did: str) -> str:
        """Resolve a did:web: DID."""
        # Extract domain from did:web:example.com
        domain = did[8:]  # Remove "did:web:" prefix
        url = f"https://{domain}/.well-known/did.json"

        try:
            response = self.session.get(url, timeout=Config.HTTP_TIMEOUT)
            response.raise_for_status()
            doc = response.json()

            for service in doc.get("service", []):
                if service.get("type") == "AtprotoPersonalDataServer":
                    return service["serviceEndpoint"]

            raise ValueError(f"No PDS endpoint found for {did}")

        except requests.RequestException as e:
            logger.error(f"Failed to resolve web DID {did}: {e}")
            raise

    def get_repo_url(self, did: str) -> str:
        """Get the full getRepo URL for a DID."""
        pds = self.resolve_did_to_pds(did)
        return f"{pds}/xrpc/com.atproto.sync.getRepo"


class CARClient:
    """Download and parse CAR files from Bluesky PDSes."""

    def __init__(
        self,
        pds_resolver: Optional[PDSResolver] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.resolver = pds_resolver or PDSResolver()
        self.timeout = timeout
        self.session = create_retrying_session(
            max_retries=Config.MAX_RETRIES,
            backoff_factor=Config.RETRY_BACKOFF_FACTOR,
        )

    def download_repo(self, did: str) -> bytes:
        """
        Download full repository CAR file for a DID.

        Args:
            did: User's DID

        Returns:
            Raw CAR file bytes

        Note:
            This is ONE call vs. many paginated API calls!
            No auth required for public repos.
        """
        pds = self.resolver.resolve_did_to_pds(did)
        url = f"{pds}/xrpc/com.atproto.sync.getRepo"
        params = {"did": did}

        logger.info(f"Downloading CAR file for {did} from {pds}")
        start_time = time.time()

        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
                stream=True,
            )
            response.raise_for_status()

            # Read the entire response
            car_bytes = response.content
            duration = time.time() - start_time

            logger.info(
                f"Downloaded {len(car_bytes):,} bytes in {duration:.2f}s for {did}"
            )
            return car_bytes

        except requests.RequestException as e:
            logger.error(f"Failed to download repo for {did}: {e}")
            raise

    def parse_car(self, car_bytes: bytes) -> Dict[str, List[Dict]]:
        """
        Parse CAR file into record collections.

        Returns:
            Dict mapping collection names to record lists:
            {
                'app.bsky.graph.follow': [
                    {'rkey': 'abc123', 'value': {...}},
                    ...
                ],
                'app.bsky.feed.post': [...],
                'app.bsky.feed.like': [...],
                'app.bsky.graph.block': [...],
                'app.bsky.feed.repost': [...],
                'app.bsky.actor.profile': [...]
            }
        """
        try:
            from atproto import CAR
        except ImportError:
            raise ImportError(
                "atproto package is required. Install with: pip install atproto"
            )

        car = CAR.from_bytes(car_bytes)

        # Organize records by collection type
        records_by_type: Dict[str, List[Dict]] = {}

        for cid, block in car.blocks.items():
            if isinstance(block, dict) and "$type" in block:
                record_type = block["$type"]

                if record_type not in records_by_type:
                    records_by_type[record_type] = []

                records_by_type[record_type].append(
                    {
                        "cid": str(cid),
                        "value": block,
                    }
                )

        return records_by_type

    def get_follows_with_timestamps(self, did: str) -> List[Dict]:
        """
        Get all follows with their creation timestamps.

        Returns:
            List of dicts with:
            - subject_did: Who they follow
            - created_at: When they started following (datetime)
            - rkey: Record key
        """
        car_bytes = self.download_repo(did)
        records = self.parse_car(car_bytes)

        follows = []
        for record in records.get("app.bsky.graph.follow", []):
            value = record["value"]
            subject_did = value.get("subject")
            created_at_str = value.get("createdAt")

            if subject_did and created_at_str:
                follows.append(
                    {
                        "subject_did": subject_did,
                        "did": subject_did,  # Alias for compatibility
                        "created_at": self._parse_timestamp(created_at_str),
                        "created_at_str": created_at_str,
                        "cid": record.get("cid"),
                    }
                )

        # Sort by creation date (oldest first)
        follows.sort(key=lambda x: x["created_at"])
        return follows

    def get_likes_with_timestamps(self, did: str) -> List[Dict]:
        """
        Get all likes with their creation timestamps.

        Returns:
            List of dicts with:
            - subject_uri: Post they liked
            - subject_cid: CID of the liked post
            - created_at: When they liked it (datetime)
        """
        car_bytes = self.download_repo(did)
        records = self.parse_car(car_bytes)

        likes = []
        for record in records.get("app.bsky.feed.like", []):
            value = record["value"]
            subject = value.get("subject", {})
            created_at_str = value.get("createdAt")

            if subject and created_at_str:
                likes.append(
                    {
                        "subject_uri": subject.get("uri"),
                        "subject_cid": subject.get("cid"),
                        "created_at": self._parse_timestamp(created_at_str),
                        "created_at_str": created_at_str,
                        "cid": record.get("cid"),
                    }
                )

        likes.sort(key=lambda x: x["created_at"])
        return likes

    def get_posts_from_repo(self, did: str) -> List[Dict]:
        """
        Get all posts with full content and timestamps.

        Returns:
            List of dicts with:
            - uri: AT-URI of post
            - text: Post content
            - created_at: Creation timestamp (datetime)
            - is_reply: Whether it's a reply
            - reply_to: Reply info if applicable
        """
        car_bytes = self.download_repo(did)
        records = self.parse_car(car_bytes)

        posts = []
        for record in records.get("app.bsky.feed.post", []):
            value = record["value"]
            created_at_str = value.get("createdAt")

            if created_at_str:
                reply_info = value.get("reply")
                posts.append(
                    {
                        "text": value.get("text", ""),
                        "created_at": self._parse_timestamp(created_at_str),
                        "created_at_str": created_at_str,
                        "is_reply": reply_info is not None,
                        "reply_to": reply_info,
                        "embed": value.get("embed"),
                        "facets": value.get("facets"),
                        "langs": value.get("langs"),
                        "cid": record.get("cid"),
                    }
                )

        posts.sort(key=lambda x: x["created_at"])
        return posts

    def get_blocks_from_repo(self, did: str) -> List[Dict]:
        """
        Get all blocks with timestamps (NO AUTH NEEDED!).

        This is a key advantage - the getBlocks API requires auth,
        but CAR files are public and contain block records.

        Returns:
            List of dicts with:
            - subject_did: Who they blocked
            - created_at: When they blocked them (datetime)
        """
        car_bytes = self.download_repo(did)
        records = self.parse_car(car_bytes)

        blocks = []
        for record in records.get("app.bsky.graph.block", []):
            value = record["value"]
            subject_did = value.get("subject")
            created_at_str = value.get("createdAt")

            if subject_did and created_at_str:
                blocks.append(
                    {
                        "subject_did": subject_did,
                        "did": subject_did,  # Alias for compatibility
                        "created_at": self._parse_timestamp(created_at_str),
                        "created_at_str": created_at_str,
                        "cid": record.get("cid"),
                    }
                )

        blocks.sort(key=lambda x: x["created_at"])
        return blocks

    def get_reposts_from_repo(self, did: str) -> List[Dict]:
        """
        Get all reposts with timestamps.

        Returns:
            List of dicts with:
            - subject_uri: Post they reposted
            - subject_cid: CID of the reposted post
            - created_at: When they reposted it (datetime)
        """
        car_bytes = self.download_repo(did)
        records = self.parse_car(car_bytes)

        reposts = []
        for record in records.get("app.bsky.feed.repost", []):
            value = record["value"]
            subject = value.get("subject", {})
            created_at_str = value.get("createdAt")

            if subject and created_at_str:
                reposts.append(
                    {
                        "subject_uri": subject.get("uri"),
                        "subject_cid": subject.get("cid"),
                        "created_at": self._parse_timestamp(created_at_str),
                        "created_at_str": created_at_str,
                        "cid": record.get("cid"),
                    }
                )

        reposts.sort(key=lambda x: x["created_at"])
        return reposts

    def get_all_data(self, did: str) -> Dict[str, Any]:
        """
        Get all data from a user's CAR file in one call.

        Returns:
            Dict with all collections and stats
        """
        logger.info(f"Fetching all data for {did}")
        car_bytes = self.download_repo(did)
        records = self.parse_car(car_bytes)

        result = {
            "did": did,
            "car_size_bytes": len(car_bytes),
            "fetched_at": datetime.utcnow().isoformat(),
            "collections": {},
            "counts": {},
        }

        # Process each collection
        collection_processors = {
            "app.bsky.graph.follow": self._process_follows,
            "app.bsky.feed.like": self._process_likes,
            "app.bsky.feed.post": self._process_posts,
            "app.bsky.graph.block": self._process_blocks,
            "app.bsky.feed.repost": self._process_reposts,
            "app.bsky.actor.profile": self._process_profile,
        }

        for collection_name, processor in collection_processors.items():
            raw_records = records.get(collection_name, [])
            processed = processor(raw_records)
            result["collections"][collection_name] = processed
            result["counts"][collection_name] = len(processed)

        # Also add simplified top-level keys for easier access
        result["follows"] = result["collections"].get("app.bsky.graph.follow", [])
        result["likes"] = result["collections"].get("app.bsky.feed.like", [])
        result["posts"] = result["collections"].get("app.bsky.feed.post", [])
        result["blocks"] = result["collections"].get("app.bsky.graph.block", [])
        result["reposts"] = result["collections"].get("app.bsky.feed.repost", [])
        result["profile"] = result["collections"].get("app.bsky.actor.profile", [])

        logger.info(
            f"Processed {did}: {result['counts']} records, {len(car_bytes):,} bytes"
        )
        return result

    def _process_follows(self, records: List[Dict]) -> List[Dict]:
        """Process follow records."""
        follows = []
        for record in records:
            value = record["value"]
            subject_did = value.get("subject")
            created_at_str = value.get("createdAt")

            if subject_did and created_at_str:
                follows.append(
                    {
                        "subject_did": subject_did,
                        "did": subject_did,  # Alias for compatibility
                        "created_at": self._parse_timestamp(created_at_str),
                        "created_at_str": created_at_str,
                    }
                )
        return sorted(follows, key=lambda x: x["created_at"])

    def _process_likes(self, records: List[Dict]) -> List[Dict]:
        """Process like records."""
        likes = []
        for record in records:
            value = record["value"]
            subject = value.get("subject", {})
            created_at_str = value.get("createdAt")

            if subject and created_at_str:
                # Extract author DID from URI if possible
                uri = subject.get("uri", "")
                author_did = None
                if uri.startswith("at://"):
                    parts = uri.split("/")
                    if len(parts) >= 3:
                        author_did = parts[2]

                likes.append(
                    {
                        "subject_uri": uri,
                        "subject_cid": subject.get("cid"),
                        "author_did": author_did,
                        "created_at": self._parse_timestamp(created_at_str),
                        "created_at_str": created_at_str,
                    }
                )
        return sorted(likes, key=lambda x: x["created_at"])

    def _process_posts(self, records: List[Dict]) -> List[Dict]:
        """Process post records."""
        posts = []
        for record in records:
            value = record["value"]
            created_at_str = value.get("createdAt")

            if created_at_str:
                reply_info = value.get("reply")
                posts.append(
                    {
                        "cid": record.get("cid"),  # Unique content identifier
                        "text": value.get("text", ""),
                        "created_at": self._parse_timestamp(created_at_str),
                        "created_at_str": created_at_str,
                        "is_reply": reply_info is not None,
                        "reply_to": reply_info,
                        "has_embed": value.get("embed") is not None,
                        "langs": value.get("langs"),
                    }
                )
        return sorted(posts, key=lambda x: x["created_at"])

    def _process_blocks(self, records: List[Dict]) -> List[Dict]:
        """Process block records."""
        blocks = []
        for record in records:
            value = record["value"]
            subject_did = value.get("subject")
            created_at_str = value.get("createdAt")

            if subject_did and created_at_str:
                blocks.append(
                    {
                        "subject_did": subject_did,
                        "did": subject_did,  # Alias for compatibility
                        "created_at": self._parse_timestamp(created_at_str),
                        "created_at_str": created_at_str,
                    }
                )
        return sorted(blocks, key=lambda x: x["created_at"])

    def _process_reposts(self, records: List[Dict]) -> List[Dict]:
        """Process repost records."""
        reposts = []
        for record in records:
            value = record["value"]
            subject = value.get("subject", {})
            created_at_str = value.get("createdAt")

            if subject and created_at_str:
                # Extract author DID from URI if possible
                uri = subject.get("uri", "")
                author_did = None
                if uri.startswith("at://"):
                    parts = uri.split("/")
                    if len(parts) >= 3:
                        author_did = parts[2]

                reposts.append(
                    {
                        "subject_uri": uri,
                        "subject_cid": subject.get("cid"),
                        "author_did": author_did,
                        "created_at": self._parse_timestamp(created_at_str),
                        "created_at_str": created_at_str,
                    }
                )
        return sorted(reposts, key=lambda x: x["created_at"])

    def _process_profile(self, records: List[Dict]) -> List[Dict]:
        """Process profile records (usually just one)."""
        profiles = []
        for record in records:
            value = record["value"]
            profiles.append(
                {
                    "display_name": value.get("displayName"),
                    "description": value.get("description"),
                    "created_at_str": value.get("createdAt"),
                }
            )
        return profiles

    @staticmethod
    def _parse_timestamp(ts_str: str) -> datetime:
        """Parse ISO timestamp string to datetime."""
        # Handle various ISO formats
        ts_str = ts_str.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(ts_str)
        except ValueError:
            # Fallback for edge cases
            return datetime.strptime(ts_str[:19], "%Y-%m-%dT%H:%M:%S")


# Convenience functions for simple usage
def get_user_data(handle_or_did: str) -> Dict[str, Any]:
    """
    Get all CAR data for a user by handle or DID.

    Example:
        data = get_user_data("user.bsky.social")
        print(f"Following {data['counts']['app.bsky.graph.follow']} accounts")
    """
    resolver = PDSResolver()
    client = CARClient(resolver)

    # Resolve handle to DID if needed
    if not handle_or_did.startswith("did:"):
        did = resolver.resolve_handle_to_did(handle_or_did)
    else:
        did = handle_or_did

    return client.get_all_data(did)
