"""
Public API Client for Bluesky Tracker

Provides unauthenticated access to public Bluesky API endpoints.
No app password required for these endpoints!

Endpoints available without auth:
- getFollowers - Who follows a user
- getFollows - Who a user follows
- getProfile - User profile info
- getAuthorFeed - User's posts with engagement counts
- resolveHandle - Convert handle to DID
"""

import logging
import time
from typing import Dict, List, Optional, Any

import requests

logger = logging.getLogger(__name__)

# Public API endpoint (no auth required)
PUBLIC_API_URL = "https://public.api.bsky.app"

# Rate limiting
DEFAULT_DELAY = 0.5  # Seconds between requests
DEFAULT_TIMEOUT = 30


class PublicAPIClient:
    """
    Client for Bluesky's public API endpoints.

    These endpoints don't require authentication and can be used
    to fetch public data like followers, following, profiles, and posts.
    """

    def __init__(
        self,
        base_url: str = PUBLIC_API_URL,
        delay: float = DEFAULT_DELAY,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.base_url = base_url
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self._last_request_time = 0

    def _rate_limit(self):
        """Apply rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_request_time = time.time()

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a GET request to the API."""
        self._rate_limit()

        url = f"{self.base_url}/xrpc/{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API request failed: {endpoint} - {e}")
            raise

    def resolve_handle(self, handle: str) -> str:
        """
        Resolve a handle to its DID.

        Args:
            handle: Bluesky handle (e.g., "user.bsky.social")

        Returns:
            DID string (e.g., "did:plc:abc123...")
        """
        data = self._get("com.atproto.identity.resolveHandle", {"handle": handle})
        return data["did"]

    def get_profile(self, actor: str) -> Dict[str, Any]:
        """
        Get a user's profile information.

        Args:
            actor: Handle or DID

        Returns:
            Profile dict with:
            - did, handle, displayName, description
            - avatar, banner
            - followersCount, followsCount, postsCount
            - indexedAt
        """
        return self._get("app.bsky.actor.getProfile", {"actor": actor})

    def get_followers(
        self,
        actor: str,
        limit: int = 100,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get a page of followers for a user.

        Args:
            actor: Handle or DID
            limit: Max results per page (max 100)
            cursor: Pagination cursor

        Returns:
            Dict with:
            - followers: List of follower profiles
            - cursor: Next page cursor (None if no more pages)
        """
        params = {"actor": actor, "limit": min(limit, 100)}
        if cursor:
            params["cursor"] = cursor

        return self._get("app.bsky.graph.getFollowers", params)

    def get_all_followers(self, actor: str) -> List[Dict]:
        """
        Get ALL followers for a user (handles pagination).

        Args:
            actor: Handle or DID

        Returns:
            Complete list of follower profiles
        """
        followers = []
        cursor = None

        logger.info(f"Fetching all followers for {actor}")

        while True:
            data = self.get_followers(actor, limit=100, cursor=cursor)
            followers.extend(data.get("followers", []))
            cursor = data.get("cursor")

            if not cursor:
                break

            logger.debug(f"Fetched {len(followers)} followers so far...")

        logger.info(f"Fetched {len(followers)} total followers for {actor}")
        return followers

    def get_follows(
        self,
        actor: str,
        limit: int = 100,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get a page of accounts a user follows.

        Args:
            actor: Handle or DID
            limit: Max results per page (max 100)
            cursor: Pagination cursor

        Returns:
            Dict with:
            - follows: List of followed profiles
            - cursor: Next page cursor (None if no more pages)
        """
        params = {"actor": actor, "limit": min(limit, 100)}
        if cursor:
            params["cursor"] = cursor

        return self._get("app.bsky.graph.getFollows", params)

    def get_all_following(self, actor: str) -> List[Dict]:
        """
        Get ALL accounts a user follows (handles pagination).

        Note: For historical data with timestamps, use CAR files instead!
        This method only returns current state, not when follows happened.

        Args:
            actor: Handle or DID

        Returns:
            Complete list of followed profiles
        """
        following = []
        cursor = None

        logger.info(f"Fetching all following for {actor}")

        while True:
            data = self.get_follows(actor, limit=100, cursor=cursor)
            following.extend(data.get("follows", []))
            cursor = data.get("cursor")

            if not cursor:
                break

            logger.debug(f"Fetched {len(following)} following so far...")

        logger.info(f"Fetched {len(following)} total following for {actor}")
        return following

    def get_author_feed(
        self,
        actor: str,
        limit: int = 50,
        cursor: Optional[str] = None,
        filter_type: str = "posts_with_replies",
    ) -> Dict[str, Any]:
        """
        Get a user's posts with engagement counts.

        Args:
            actor: Handle or DID
            limit: Max results per page (max 100)
            cursor: Pagination cursor
            filter_type: One of:
                - "posts_with_replies" (default)
                - "posts_no_replies"
                - "posts_and_author_threads"
                - "posts_with_media"

        Returns:
            Dict with:
            - feed: List of post items with engagement
            - cursor: Next page cursor
        """
        params = {
            "actor": actor,
            "limit": min(limit, 100),
            "filter": filter_type,
        }
        if cursor:
            params["cursor"] = cursor

        return self._get("app.bsky.feed.getAuthorFeed", params)

    def get_recent_posts(
        self,
        actor: str,
        limit: int = 50,
        include_replies: bool = True,
    ) -> List[Dict]:
        """
        Get recent posts with engagement metrics.

        Args:
            actor: Handle or DID
            limit: Number of posts to fetch
            include_replies: Whether to include replies

        Returns:
            List of post dicts with:
            - uri, cid, text, createdAt
            - likeCount, repostCount, replyCount, quoteCount
            - author info
        """
        filter_type = "posts_with_replies" if include_replies else "posts_no_replies"

        posts = []
        cursor = None
        fetched = 0

        while fetched < limit:
            page_limit = min(100, limit - fetched)
            data = self.get_author_feed(actor, limit=page_limit, cursor=cursor, filter_type=filter_type)

            feed_items = data.get("feed", [])
            if not feed_items:
                break

            for item in feed_items:
                post = item.get("post", {})
                # Skip reposts - they have a "reason" field
                if "reason" in item:
                    continue

                posts.append(
                    {
                        "uri": post.get("uri"),
                        "cid": post.get("cid"),
                        "text": post.get("record", {}).get("text", ""),
                        "created_at": post.get("record", {}).get("createdAt"),
                        "indexed_at": post.get("indexedAt"),
                        "like_count": post.get("likeCount", 0),
                        "repost_count": post.get("repostCount", 0),
                        "reply_count": post.get("replyCount", 0),
                        "quote_count": post.get("quoteCount", 0),
                        "author_did": post.get("author", {}).get("did"),
                        "author_handle": post.get("author", {}).get("handle"),
                    }
                )
                fetched += 1

                if fetched >= limit:
                    break

            cursor = data.get("cursor")
            if not cursor:
                break

        return posts

    def get_post_engagement(self, actor: str, limit: int = 50) -> Dict[str, Any]:
        """
        Get engagement summary for recent posts.

        Args:
            actor: Handle or DID
            limit: Number of posts to analyze

        Returns:
            Dict with:
            - total_likes, total_reposts, total_replies, total_quotes
            - posts_count
            - avg_engagement_per_post
            - posts: List of post details
        """
        posts = self.get_recent_posts(actor, limit=limit)

        total_likes = sum(p.get("like_count", 0) for p in posts)
        total_reposts = sum(p.get("repost_count", 0) for p in posts)
        total_replies = sum(p.get("reply_count", 0) for p in posts)
        total_quotes = sum(p.get("quote_count", 0) for p in posts)

        total_engagement = total_likes + total_reposts + total_replies + total_quotes
        avg_engagement = total_engagement / len(posts) if posts else 0

        return {
            "total_likes": total_likes,
            "total_reposts": total_reposts,
            "total_replies": total_replies,
            "total_quotes": total_quotes,
            "total_engagement": total_engagement,
            "posts_count": len(posts),
            "avg_engagement_per_post": round(avg_engagement, 2),
            "posts": posts,
        }

    def get_profile_with_counts(self, actor: str) -> Dict[str, Any]:
        """
        Get profile with formatted counts.

        Returns:
            Dict with profile info and engagement metrics
        """
        profile = self.get_profile(actor)

        return {
            "did": profile.get("did"),
            "handle": profile.get("handle"),
            "display_name": profile.get("displayName"),
            "description": profile.get("description"),
            "avatar": profile.get("avatar"),
            "followers_count": profile.get("followersCount", 0),
            "following_count": profile.get("followsCount", 0),
            "posts_count": profile.get("postsCount", 0),
            "indexed_at": profile.get("indexedAt"),
        }


# Convenience functions for simple usage
def get_public_profile(handle_or_did: str) -> Dict[str, Any]:
    """Get profile info without auth."""
    client = PublicAPIClient()
    return client.get_profile_with_counts(handle_or_did)


def get_public_followers(handle_or_did: str) -> List[Dict]:
    """Get all followers without auth."""
    client = PublicAPIClient()
    return client.get_all_followers(handle_or_did)


def get_public_following(handle_or_did: str) -> List[Dict]:
    """Get all following without auth."""
    client = PublicAPIClient()
    return client.get_all_following(handle_or_did)
