"""
Bluesky Data Collector

Hybrid approach using:
- CAR files for following, blocks, likes given, reposts given, posts (ONE API call, includes timestamps)
- Public API for followers, profile counts, engagement received (no auth needed)
- Authenticated API only for interactions (who liked/replied to you)
"""

import time
import requests
from datetime import date, datetime
from config import Config
from database import Database
from car_utils import CARClient
from public_api import PublicAPIClient
import logging

logger = logging.getLogger(__name__)


class BlueskyCollector:
    def __init__(self):
        self.db = Database()
        self.session = None
        self.access_token = None
        self.auth_enabled = Config.AUTH_ENABLED
        self.car_client = CARClient()
        self.public_api = PublicAPIClient()
        self.user_did = None

    def authenticate(self):
        """Authenticate with Bluesky using app password (only if enabled)"""
        if not self.auth_enabled:
            logger.info("Authentication disabled - skipping")
            return True

        try:
            logger.info("Authenticating with app password...")

            response = requests.post(
                f"{Config.BLUESKY_API_URL}/xrpc/com.atproto.server.createSession",
                json={
                    "identifier": Config.BLUESKY_HANDLE,
                    "password": Config.BLUESKY_APP_PASSWORD,
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            self.access_token = data.get("accessJwt")
            self.session = data
            self.user_did = data.get("did")
            logger.info(f"Authenticated successfully as {data.get('handle')}")
            return True

        except Exception as e:
            # Don't log password in error messages
            error_msg = str(e)
            if Config.BLUESKY_APP_PASSWORD:
                error_msg = error_msg.replace(Config.BLUESKY_APP_PASSWORD, "***")
            logger.error(f"Authentication failed: {error_msg}")
            return False

    def get_auth_headers(self):
        """Get authentication headers if available"""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}

    def resolve_did(self):
        """Resolve handle to DID using public API"""
        if self.user_did:
            return self.user_did

        try:
            self.user_did = self.public_api.resolve_handle(Config.BLUESKY_HANDLE)
            logger.info(f"Resolved DID: {self.user_did}")
            return self.user_did
        except Exception as e:
            logger.error(f"Failed to resolve DID: {e}")
            raise

    def fetch_car_data(self, did):
        """
        Fetch all data from CAR file in a single download.

        This is the optimized approach - downloads once and returns all data.
        Pass the result to other fetch_*_from_car methods to avoid redundant downloads.

        Returns:
            Dict with all CAR data including follows, likes, posts, blocks, reposts
        """
        try:
            logger.info("=" * 60)
            logger.info("CAR OPTIMIZATION: Starting single CAR download for all data")
            logger.info(f"CAR OPTIMIZATION: DID = {did}")
            logger.info("=" * 60)

            import time as _time
            start = _time.time()
            car_data = self.car_client.get_all_data(did)
            elapsed = _time.time() - start

            car_size = car_data.get('car_size_bytes', 0)
            counts = car_data.get('counts', {})

            logger.info("=" * 60)
            logger.info("CAR OPTIMIZATION: Download complete!")
            logger.info(f"CAR OPTIMIZATION: Size = {car_size:,} bytes ({car_size/1024/1024:.2f} MB)")
            logger.info(f"CAR OPTIMIZATION: Time = {elapsed:.2f} seconds")
            logger.info(f"CAR OPTIMIZATION: Records found:")
            logger.info(f"  - Follows:  {counts.get('app.bsky.graph.follow', 0):,}")
            logger.info(f"  - Likes:    {counts.get('app.bsky.feed.like', 0):,}")
            logger.info(f"  - Posts:    {counts.get('app.bsky.feed.post', 0):,}")
            logger.info(f"  - Blocks:   {counts.get('app.bsky.graph.block', 0):,}")
            logger.info(f"  - Reposts:  {counts.get('app.bsky.feed.repost', 0):,}")
            logger.info("CAR OPTIMIZATION: This data will be reused (no more CAR downloads needed)")
            logger.info("=" * 60)

            return car_data
        except Exception as e:
            logger.error(f"CAR OPTIMIZATION: Failed to fetch CAR data: {e}")
            raise

    def fetch_all_followers(self):
        """Fetch all followers using PUBLIC API (no auth needed)"""
        try:
            logger.info("Fetching followers via public API...")
            raw_followers = self.public_api.get_all_followers(Config.BLUESKY_HANDLE)

            followers = []
            for follower in raw_followers:
                followers.append({
                    "did": follower.get("did"),
                    "handle": follower.get("handle"),
                    "display_name": follower.get("displayName", ""),
                    "avatar_url": follower.get("avatar", ""),
                    "bio": follower.get("description", ""),
                })

            logger.info(f"Fetched {len(followers)} followers via public API")
            return followers

        except Exception as e:
            logger.error(f"Error fetching followers: {e}")
            return []

    def fetch_following_from_car(self, did, car_data=None):
        """
        Fetch following list using HYBRID approach:
        - Public API for profile info (handles, display names, avatars)
        - CAR file for timestamps (when the follow happened)
        No auth required!

        Args:
            did: User's DID
            car_data: Pre-fetched CAR data from fetch_car_data(). If None, will download.
        """
        try:
            logger.info("Fetching following via hybrid approach (API + CAR)...")

            # Get profile info from public API
            api_follows = self.public_api.get_all_following(Config.BLUESKY_HANDLE)
            logger.info(f"Got {len(api_follows)} following from public API")

            # Get timestamps from CAR data (use pre-fetched if available)
            if car_data:
                car_follows = car_data.get("follows", [])
                logger.info(f"CAR REUSE: Using pre-fetched follows data ({len(car_follows)} records) - NO DOWNLOAD")
            else:
                logger.warning("CAR FALLBACK: No pre-fetched data, downloading CAR file...")
                car_follows = self.car_client.get_follows_with_timestamps(did)
                logger.info(f"Got {len(car_follows)} following timestamps from CAR")

            # Create a DID -> timestamp map from CAR data
            timestamp_map = {}
            for follow in car_follows:
                follow_did = follow.get("did") or follow.get("subject_did")
                if follow_did:
                    timestamp_map[follow_did] = follow.get("created_at")

            # Merge: API profiles + CAR timestamps
            following = []
            for follow in api_follows:
                follow_did = follow.get("did")
                following.append({
                    "did": follow_did,
                    "handle": follow.get("handle", ""),
                    "display_name": follow.get("displayName", ""),
                    "avatar_url": follow.get("avatar", ""),
                    "bio": follow.get("description", ""),
                    "followed_at": timestamp_map.get(follow_did),  # From CAR
                })

            logger.info(f"Merged {len(following)} following with timestamps")
            return following

        except Exception as e:
            logger.error(f"Error fetching following: {e}")
            return []

    def fetch_blocks_from_car(self, did, car_data=None):
        """
        Fetch blocks from CAR file (no auth needed!).
        Unlike the getBlocks API, this doesn't require authentication.
        Enriches with profile info from public API where possible.

        Args:
            did: User's DID
            car_data: Pre-fetched CAR data from fetch_car_data(). If None, will download.
        """
        try:
            logger.info("Fetching blocks via CAR file (no auth needed)...")

            # Get blocks from CAR data (use pre-fetched if available)
            if car_data:
                blocks = car_data.get("blocks", [])
                logger.info(f"CAR REUSE: Using pre-fetched blocks data ({len(blocks)} records) - NO DOWNLOAD")
            else:
                logger.warning("CAR FALLBACK: No pre-fetched data, downloading CAR file...")
                blocks = self.car_client.get_blocks_from_repo(did)

            blocked = []
            for block in blocks:
                block_did = block.get("did") or block.get("subject_did")
                handle = ""
                display_name = ""
                avatar_url = ""
                bio = ""

                # Try to get profile info from public API
                try:
                    profile = self.public_api.get_profile(block_did)
                    handle = profile.get("handle", "")
                    display_name = profile.get("displayName", "")
                    avatar_url = profile.get("avatar", "")
                    bio = profile.get("description", "")
                except Exception:
                    # Profile might not be accessible, use DID as fallback
                    handle = block_did.split(":")[-1] if block_did else ""

                blocked.append({
                    "did": block_did,
                    "handle": handle,
                    "display_name": display_name,
                    "avatar_url": avatar_url,
                    "bio": bio,
                    "blocked_at": block.get("created_at"),
                })

            logger.info(f"Fetched {len(blocked)} blocks from CAR file")
            return blocked

        except Exception as e:
            logger.error(f"Error fetching blocks from CAR: {e}")
            return []

    def fetch_likes_given_from_car(self, did, car_data=None):
        """
        Fetch likes given from CAR file (outgoing engagement).
        Returns list with URIs and timestamps of all likes you've given.

        Args:
            did: User's DID
            car_data: Pre-fetched CAR data from fetch_car_data(). If None, will download.
        """
        try:
            logger.info("Fetching likes given via CAR file...")

            # Get likes from CAR data (use pre-fetched if available)
            if car_data:
                likes = car_data.get("likes", [])
                logger.info(f"CAR REUSE: Using pre-fetched likes data ({len(likes)} records) - NO DOWNLOAD")
            else:
                logger.warning("CAR FALLBACK: No pre-fetched data, downloading CAR file...")
                likes = self.car_client.get_likes_with_timestamps(did)

            likes_data = []
            for like in likes:
                subject_uri = like.get("subject_uri", "")
                # Extract author DID from URI (at://did:plc:xxx/app.bsky.feed.post/xxx)
                author_did = like.get("author_did")  # Already extracted in get_all_data
                if not author_did and subject_uri.startswith("at://"):
                    parts = subject_uri[5:].split("/")
                    if parts:
                        author_did = parts[0]

                likes_data.append({
                    "liked_post_uri": subject_uri,
                    "liked_author_did": author_did,
                    "liked_at": like.get("created_at"),
                    "rkey": like.get("rkey"),
                })

            logger.info(f"Fetched {len(likes_data)} likes given from CAR file")
            return likes_data

        except Exception as e:
            logger.error(f"Error fetching likes from CAR: {e}")
            return []

    def fetch_reposts_given_from_car(self, did, car_data=None):
        """
        Fetch reposts given from CAR file (outgoing engagement).
        Returns list with URIs and timestamps of all reposts you've made.

        Args:
            did: User's DID
            car_data: Pre-fetched CAR data from fetch_car_data(). If None, will download.
        """
        try:
            logger.info("Fetching reposts given via CAR file...")

            # Get reposts from CAR data (use pre-fetched if available)
            if car_data:
                reposts = car_data.get("reposts", [])
                logger.info(f"CAR REUSE: Using pre-fetched reposts data ({len(reposts)} records) - NO DOWNLOAD")
            else:
                logger.warning("CAR FALLBACK: No pre-fetched data, downloading CAR file...")
                all_data = self.car_client.get_all_data(did)
                reposts = all_data.get("reposts", [])

            reposts_data = []
            for repost in reposts:
                subject_uri = repost.get("subject_uri", "")
                # Extract author DID from URI
                author_did = repost.get("author_did")  # Already extracted in get_all_data
                if not author_did and subject_uri.startswith("at://"):
                    parts = subject_uri[5:].split("/")
                    if parts:
                        author_did = parts[0]

                reposts_data.append({
                    "reposted_uri": subject_uri,
                    "reposted_author_did": author_did,
                    "reposted_at": repost.get("created_at"),
                    "rkey": repost.get("rkey"),
                })

            logger.info(f"Fetched {len(reposts_data)} reposts given from CAR file")
            return reposts_data

        except Exception as e:
            logger.error(f"Error fetching reposts from CAR: {e}")
            return []

    def fetch_posts_from_car(self, did, car_data=None):
        """
        Fetch full post history from CAR file.
        Returns complete history, not just last 50 posts.

        Args:
            did: User's DID
            car_data: Pre-fetched CAR data from fetch_car_data(). If None, will download.
        """
        try:
            logger.info("Fetching full post history via CAR file...")

            # Get posts from CAR data (use pre-fetched if available)
            if car_data:
                posts = car_data.get("posts", [])
                logger.info(f"CAR REUSE: Using pre-fetched posts data ({len(posts)} records) - NO DOWNLOAD")
            else:
                logger.warning("CAR FALLBACK: No pre-fetched data, downloading CAR file...")
                all_data = self.car_client.get_all_data(did)
                posts = all_data.get("posts", [])

            posts_data = []
            for post in posts:
                # get_all_data returns processed posts with direct keys
                reply = post.get("reply_to")
                reply_uri = None
                if reply and isinstance(reply, dict):
                    parent = reply.get("parent", {})
                    if isinstance(parent, dict):
                        reply_uri = parent.get("uri")

                posts_data.append({
                    "post_uri": post.get("cid"),  # Use CID as unique identifier
                    "text": post.get("text", ""),
                    "post_created_at": post.get("created_at_str"),  # Use string timestamp
                    "is_reply": post.get("is_reply", False),
                    "reply_to_uri": reply_uri,
                    "has_embed": post.get("has_embed", False),
                    "langs": ",".join(post.get("langs", [])) if post.get("langs") else None,
                })

            logger.info(f"Fetched {len(posts_data)} posts from CAR file (full history)")
            return posts_data

        except Exception as e:
            logger.error(f"Error fetching posts from CAR: {e}")
            return []

    def fetch_engagement_data(self):
        """Fetch post engagement data using PUBLIC API (no auth needed)"""
        try:
            logger.info("Fetching engagement via public API...")
            posts = self.public_api.get_recent_posts(
                Config.BLUESKY_HANDLE,
                limit=50,
                include_replies=True
            )

            engagement = []
            for post in posts:
                engagement.append({
                    "uri": post.get("uri"),
                    "text": post.get("text", ""),
                    "created_at": post.get("created_at"),
                    "like_count": post.get("like_count", 0),
                    "repost_count": post.get("repost_count", 0),
                    "reply_count": post.get("reply_count", 0),
                    "quote_count": post.get("quote_count", 0),
                    "bookmark_count": 0,  # Not available in public API
                })

            logger.info(f"Collected engagement data for {len(engagement)} posts")
            return engagement

        except Exception as e:
            logger.error(f"Error fetching engagement data: {e}")
            return []

    def fetch_profile_counts(self):
        """Fetch profile counts using PUBLIC API (no auth needed)"""
        try:
            logger.info("Fetching profile via public API...")
            profile = self.public_api.get_profile_with_counts(Config.BLUESKY_HANDLE)

            profile_followers = profile.get("followers_count", 0)
            profile_following = profile.get("following_count", 0)

            logger.info(
                f"Profile counts: {profile_followers} followers, {profile_following} following"
            )
            return {"followers": profile_followers, "following": profile_following}

        except Exception as e:
            logger.error(f"Error fetching profile counts: {e}")
            return {"followers": 0, "following": 0}

    def fetch_interactions(self):
        """
        Fetch interaction data from notifications API.
        REQUIRES AUTHENTICATION - skip if not authenticated.
        """
        if not self.auth_enabled:
            logger.info("Skipping interactions - auth not configured")
            return []

        if not self.access_token:
            logger.info("Skipping interactions - not authenticated")
            return []

        try:
            # Fetch notifications (last 100)
            response = requests.get(
                f"{Config.BLUESKY_API_URL}/xrpc/app.bsky.notification.listNotifications",
                params={"limit": 100},
                headers=self.get_auth_headers(),
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            # Aggregate by user
            user_interactions = {}

            for notif in data.get("notifications", []):
                author = notif.get("author", {})
                did = author.get("did")
                if not did:
                    continue

                # Initialize user if not seen
                if did not in user_interactions:
                    user_interactions[did] = {
                        "did": did,
                        "handle": author.get("handle", ""),
                        "display_name": author.get("displayName", ""),
                        "avatar": author.get("avatar", ""),
                        "bio": author.get("description", ""),
                        "likes": 0,
                        "replies": 0,
                        "reposts": 0,
                        "quotes": 0,
                        "follows": 0,
                        "last_interaction": notif.get("indexedAt", ""),
                    }

                # Count interaction types
                reason = notif.get("reason", "")
                if reason == "like":
                    user_interactions[did]["likes"] += 1
                elif reason == "reply":
                    user_interactions[did]["replies"] += 1
                elif reason == "repost":
                    user_interactions[did]["reposts"] += 1
                elif reason == "quote":
                    user_interactions[did]["quotes"] += 1
                elif reason == "follow":
                    user_interactions[did]["follows"] += 1

                # Update last interaction time (most recent)
                notif_time = notif.get("indexedAt", "")
                if notif_time > user_interactions[did]["last_interaction"]:
                    user_interactions[did]["last_interaction"] = notif_time

            # Calculate interaction scores (weighted)
            interactions_list = []
            for user in user_interactions.values():
                # Score: replies=5, quotes=4, reposts=2, likes=1, follows=3
                score = (
                    user["likes"] * 1
                    + user["reposts"] * 2
                    + user["follows"] * 3
                    + user["quotes"] * 4
                    + user["replies"] * 5
                )
                user["score"] = score
                interactions_list.append(user)

            # Sort by score
            interactions_list.sort(key=lambda x: x["score"], reverse=True)

            logger.info(
                f"Collected interaction data for {len(interactions_list)} users"
            )
            return interactions_list

        except Exception as e:
            logger.error(f"Error fetching interactions: {e}")
            return []

    def backfill_historical_data(self):
        """
        Backfill historical data from CAR file.
        Downloads the full repository and extracts all historical records.
        Call this once to populate historical timestamps.
        """
        start_time = time.time()
        did = self.resolve_did()

        try:
            logger.info(f"Starting CAR backfill for {did}...")

            # Download and parse CAR file in ONE call (optimized)
            all_data = self.car_client.get_all_data(did)
            car_size = all_data.get("car_size_bytes", 0)
            logger.info(f"Downloaded CAR file: {car_size:,} bytes")

            stats = {
                "follows": len(all_data.get("follows", [])),
                "posts": len(all_data.get("posts", [])),
                "likes": len(all_data.get("likes", [])),
                "reposts": len(all_data.get("reposts", [])),
                "blocks": len(all_data.get("blocks", [])),
            }

            logger.info(f"Parsed CAR: {stats}")

            # Save following with timestamps
            follows = all_data.get("follows", [])
            following_data = []
            for follow in follows:
                following_data.append({
                    "did": follow.get("did"),
                    "handle": "",
                    "followed_at": follow.get("created_at"),
                })
            self.db.save_following_with_timestamps(date.today(), following_data)

            # Save likes given
            likes = all_data.get("likes", [])
            likes_data = []
            for like in likes:
                subject_uri = like.get("subject_uri", "")
                author_did = None
                if subject_uri.startswith("at://"):
                    parts = subject_uri[5:].split("/")
                    if parts:
                        author_did = parts[0]

                likes_data.append({
                    "liked_post_uri": subject_uri,
                    "liked_author_did": author_did,
                    "liked_at": like.get("created_at"),
                    "rkey": like.get("rkey"),
                })
            self.db.save_likes_given(likes_data)

            # Save reposts given
            reposts = all_data.get("reposts", [])
            reposts_data = []
            for repost in reposts:
                subject_uri = repost.get("subject_uri", "")
                author_did = None
                if subject_uri.startswith("at://"):
                    parts = subject_uri[5:].split("/")
                    if parts:
                        author_did = parts[0]

                reposts_data.append({
                    "reposted_uri": subject_uri,
                    "reposted_author_did": author_did,
                    "reposted_at": repost.get("created_at"),
                    "rkey": repost.get("rkey"),
                })
            self.db.save_reposts_given(reposts_data)

            # Save posts (using keys from _process_posts() output)
            posts = all_data.get("posts", [])
            posts_data = []
            for post in posts:
                reply_to = post.get("reply_to")
                reply_uri = None
                if reply_to and isinstance(reply_to, dict):
                    parent = reply_to.get("parent", {})
                    if isinstance(parent, dict):
                        reply_uri = parent.get("uri")

                posts_data.append({
                    "post_uri": post.get("cid"),  # Use CID as unique identifier
                    "text": post.get("text", ""),
                    "post_created_at": post.get("created_at_str"),
                    "is_reply": post.get("is_reply", False),
                    "reply_to_uri": reply_uri,
                    "has_embed": post.get("has_embed", False),
                    "langs": ",".join(post.get("langs", [])) if post.get("langs") else None,
                })
            self.db.save_posts_from_car(posts_data)

            # Save blocks with timestamps
            blocks = all_data.get("blocks", [])
            blocks_data = []
            for block in blocks:
                blocks_data.append({
                    "did": block.get("did"),
                    "handle": "",
                    "blocked_at": block.get("created_at"),
                })
            self.db.save_blocks_with_timestamps(date.today(), blocks_data)

            # Log backfill
            duration = time.time() - start_time
            self.db.log_backfill(did, car_size, stats, duration, "success")

            logger.info(f"Backfill complete in {duration:.1f}s")
            return {
                "status": "success",
                "did": did,
                "car_size_bytes": car_size,
                "stats": stats,
                "duration_seconds": duration,
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Backfill failed: {e}")
            self.db.log_backfill(did, 0, {}, duration, f"error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "duration_seconds": duration,
            }

    def collect(self):
        """
        Main collection job - run daily.

        Uses hybrid approach:
        - CAR file for following/blocks/likes/reposts/posts (ONE download, with timestamps)
        - Public API for followers/profile/engagement (no auth needed)
        - Authenticated API only for interactions (if auth enabled)
        """
        start_time = datetime.now()
        collection_date = date.today()

        try:
            logger.info(f"Starting collection for {collection_date}")
            logger.info(f"Tracking: {Config.BLUESKY_HANDLE}")
            logger.info(f"Auth enabled: {self.auth_enabled}")

            # 1. Resolve DID first (needed for CAR file)
            did = self.resolve_did()

            # 2. Fetch profile counts (PUBLIC API - no auth)
            profile_counts = self.fetch_profile_counts()

            # 3. Fetch followers (PUBLIC API - no auth)
            followers = self.fetch_all_followers()
            logger.info(
                f"Collected {len(followers)} followers (API) vs {profile_counts['followers']} (profile)"
            )

            # 4. Download CAR file ONCE (optimized - single download for all CAR data)
            car_data = self.fetch_car_data(did)

            # 5. Fetch following with timestamps from CAR data (no additional download!)
            following = self.fetch_following_from_car(did, car_data=car_data)
            logger.info(
                f"Collected {len(following)} following (CAR with timestamps) vs {profile_counts['following']} (profile)"
            )

            # 6. Fetch blocks from CAR data (no additional download!)
            blocked = self.fetch_blocks_from_car(did, car_data=car_data)

            # 7. Fetch engagement data (PUBLIC API - no auth)
            engagement_data = self.fetch_engagement_data()

            # 8. Fetch outgoing engagement from CAR data (no additional downloads!)
            likes_given = self.fetch_likes_given_from_car(did, car_data=car_data)
            reposts_given = self.fetch_reposts_given_from_car(did, car_data=car_data)
            posts_full = self.fetch_posts_from_car(did, car_data=car_data)

            # 9. Save all data
            # Save followers/following snapshot (following now has timestamps)
            self.db.save_snapshot(
                collection_date, followers, following, profile_counts, None, blocked
            )

            # Save following with timestamps separately
            self.db.save_following_with_timestamps(collection_date, following)

            # Save blocks with timestamps
            self.db.save_blocks_with_timestamps(collection_date, blocked)

            # Save engagement data
            if engagement_data:
                self.db.save_engagement_data(collection_date, engagement_data)

            # Save outgoing engagement
            if likes_given:
                self.db.save_likes_given(likes_given)
            if reposts_given:
                self.db.save_reposts_given(reposts_given)
            if posts_full:
                self.db.save_posts_from_car(posts_full)

            # 10. Auth-only features (interactions)
            if self.auth_enabled:
                self.authenticate()
                interactions = self.fetch_interactions()
                if interactions:
                    self.db.save_interactions(collection_date, interactions)
            else:
                logger.info("Auth disabled - skipping interactions feature")

            # 11. Detect and record changes
            self.db.detect_changes(collection_date)

            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            self.db.log_collection(
                collection_date,
                "success",
                len(followers),
                len(following),
                None,
                duration,
            )

            logger.info(f"Collection complete in {duration:.1f}s")
            return True

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Collection failed: {e}")
            self.db.log_collection(
                collection_date, "failed", None, None, str(e), duration
            )
            return False
