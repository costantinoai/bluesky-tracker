import time
import requests
from datetime import date, datetime
from config import Config
from database import Database
import logging

logger = logging.getLogger(__name__)


class BlueskyCollector:
    def __init__(self):
        self.db = Database()
        self.session = None
        self.access_token = None

    def authenticate(self):
        """Authenticate with Bluesky using app password"""
        try:
            # SECURITY: Never log the password
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
            logger.info(f"✓ Authenticated successfully as {data.get('handle')}")
            return True

        except Exception as e:
            # SECURITY: Don't log password in error messages
            error_msg = str(e).replace(Config.BLUESKY_APP_PASSWORD, "***")
            logger.error(f"❌ Authentication failed: {error_msg}")
            logger.error("Collection cannot proceed without authentication")
            raise Exception(f"Authentication failed: {error_msg}")

    def get_auth_headers(self):
        """Get authentication headers if available"""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}

    def fetch_all_followers(self):
        """Fetch all followers"""
        followers = []
        cursor = None

        while True:
            try:
                params = {"actor": Config.BLUESKY_HANDLE, "limit": 100}
                if cursor:
                    params["cursor"] = cursor

                response = requests.get(
                    f"{Config.BLUESKY_API_URL}/xrpc/app.bsky.graph.getFollowers",
                    params=params,
                    headers=self.get_auth_headers(),
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

                for follower in data.get("followers", []):
                    followers.append(
                        {
                            "did": follower.get("did"),
                            "handle": follower.get("handle"),
                            "display_name": follower.get("displayName", ""),
                            "avatar_url": follower.get("avatar", ""),
                            "bio": follower.get("description", ""),
                        }
                    )

                cursor = data.get("cursor")
                if not cursor:
                    break

                time.sleep(Config.REQUEST_DELAY)

            except Exception as e:
                logger.error(f"Error fetching followers: {e}")
                break

        return followers

    def fetch_all_following(self):
        """Fetch all following"""
        following = []
        cursor = None

        while True:
            try:
                params = {"actor": Config.BLUESKY_HANDLE, "limit": 100}
                if cursor:
                    params["cursor"] = cursor

                response = requests.get(
                    f"{Config.BLUESKY_API_URL}/xrpc/app.bsky.graph.getFollows",
                    params=params,
                    headers=self.get_auth_headers(),
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

                for follow in data.get("follows", []):
                    following.append(
                        {
                            "did": follow.get("did"),
                            "handle": follow.get("handle"),
                            "display_name": follow.get("displayName", ""),
                            "avatar_url": follow.get("avatar", ""),
                            "bio": follow.get("description", ""),
                        }
                    )

                cursor = data.get("cursor")
                if not cursor:
                    break

                time.sleep(Config.REQUEST_DELAY)

            except Exception as e:
                logger.error(f"Error fetching following: {e}")
                break

        return following

    def fetch_engagement_data(self):
        """Fetch post engagement data"""
        try:
            # Get user's posts with engagement metrics
            response = requests.get(
                f"{Config.BLUESKY_API_URL}/xrpc/app.bsky.feed.getAuthorFeed",
                params={
                    "actor": Config.BLUESKY_HANDLE,
                    "limit": 50,
                    "filter": "posts_with_replies",
                },
                headers=self.get_auth_headers(),
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            engagement = []
            for item in data.get("feed", []):
                # Skip reposts - only include original posts
                if "reason" in item:
                    reason_type = item.get("reason", {}).get("$type", "")
                    if "reasonRepost" in reason_type:
                        continue

                post = item.get("post", {})
                # Also skip if author is not us (additional safety check)
                if post.get("author", {}).get("handle") != Config.BLUESKY_HANDLE:
                    continue

                engagement.append(
                    {
                        "uri": post.get("uri"),
                        "text": post.get("record", {}).get("text", ""),
                        "created_at": post.get("record", {}).get("createdAt"),
                        "like_count": post.get("likeCount", 0),
                        "repost_count": post.get("repostCount", 0),
                        "reply_count": post.get("replyCount", 0),
                        "quote_count": post.get("quoteCount", 0),
                        "bookmark_count": post.get("bookmarkCount", 0),
                    }
                )

            # Fetch indirect engagement for each post
            logger.info(f"Collected direct engagement for {len(engagement)} posts")
            logger.info("Fetching indirect engagement from quote posts...")

            for post_data in engagement:
                indirect = self.fetch_indirect_engagement(post_data["uri"])
                post_data["indirect_likes"] = indirect["likes"]
                post_data["indirect_reposts"] = indirect["reposts"]
                post_data["indirect_replies"] = indirect["replies"]
                post_data["indirect_bookmarks"] = indirect["bookmarks"]

            logger.info(
                f"Collected engagement data for {len(engagement)} posts (including indirect)"
            )
            return engagement

        except Exception as e:
            logger.error(f"Error fetching engagement data: {e}")
            return []

    def fetch_indirect_engagement(self, post_uri):
        """
        Fetch indirect engagement for a post.
        Indirect engagement = engagement on posts that quoted this post.
        """
        try:
            # Use getQuotes endpoint to find posts that quoted this post
            response = requests.get(
                f"{Config.BLUESKY_API_URL}/xrpc/app.bsky.feed.getQuotes",
                params={"uri": post_uri, "limit": 50},
                headers=self.get_auth_headers(),
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            # Sum up engagement from all quote posts
            total_likes = 0
            total_reposts = 0
            total_replies = 0
            total_bookmarks = 0

            for quote_post_item in data.get("posts", []):
                total_likes += quote_post_item.get("likeCount", 0)
                total_reposts += quote_post_item.get("repostCount", 0)
                total_replies += quote_post_item.get("replyCount", 0)
                total_bookmarks += quote_post_item.get("bookmarkCount", 0)

            quote_count = len(data.get("posts", []))
            if quote_count > 0:
                logger.info(
                    f"Found {quote_count} quote posts with {total_likes} likes, {total_reposts} reposts, {total_replies} replies, {total_bookmarks} bookmarks"
                )

            return {
                "likes": total_likes,
                "reposts": total_reposts,
                "replies": total_replies,
                "bookmarks": total_bookmarks,
            }

        except Exception as e:
            logger.debug(f"Error fetching indirect engagement for {post_uri}: {e}")
            return {"likes": 0, "reposts": 0, "replies": 0, "bookmarks": 0}

    def fetch_profile_counts(self):
        """Fetch profile counts (includes ALL followers/following, even hidden ones)"""
        try:
            response = requests.get(
                f"{Config.BLUESKY_API_URL}/xrpc/app.bsky.actor.getProfile",
                params={"actor": Config.BLUESKY_HANDLE},
                headers=self.get_auth_headers(),
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            profile_followers = data.get("followersCount", 0)
            profile_following = data.get("followsCount", 0)

            logger.info(
                f"Profile counts: {profile_followers} followers, {profile_following} following"
            )
            return {"followers": profile_followers, "following": profile_following}

        except Exception as e:
            logger.error(f"Error fetching profile counts: {e}")
            return {"followers": 0, "following": 0}

    def fetch_muted_accounts(self):
        """Fetch list of accounts we muted"""
        try:
            muted = []
            cursor = None

            while True:
                params = {"limit": 100}
                if cursor:
                    params["cursor"] = cursor

                response = requests.get(
                    f"{Config.BLUESKY_API_URL}/xrpc/app.bsky.graph.getMutes",
                    params=params,
                    headers=self.get_auth_headers(),
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

                for account in data.get("mutes", []):
                    muted.append(
                        {
                            "did": account.get("did"),
                            "handle": account.get("handle"),
                            "display_name": account.get("displayName", ""),
                            "avatar_url": account.get("avatar", ""),
                            "bio": account.get("description", ""),
                        }
                    )

                cursor = data.get("cursor")
                if not cursor:
                    break

                time.sleep(Config.REQUEST_DELAY)

            logger.info(f"Collected {len(muted)} muted accounts")
            return muted

        except Exception as e:
            logger.error(f"Error fetching muted accounts: {e}")
            return []

    def fetch_blocked_accounts(self):
        """Fetch list of accounts we blocked"""
        try:
            blocked = []
            cursor = None

            while True:
                params = {"limit": 100}
                if cursor:
                    params["cursor"] = cursor

                response = requests.get(
                    f"{Config.BLUESKY_API_URL}/xrpc/app.bsky.graph.getBlocks",
                    params=params,
                    headers=self.get_auth_headers(),
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

                for account in data.get("blocks", []):
                    blocked.append(
                        {
                            "did": account.get("did"),
                            "handle": account.get("handle"),
                            "display_name": account.get("displayName", ""),
                            "avatar_url": account.get("avatar", ""),
                            "bio": account.get("description", ""),
                        }
                    )

                cursor = data.get("cursor")
                if not cursor:
                    break

                time.sleep(Config.REQUEST_DELAY)

            logger.info(f"Collected {len(blocked)} blocked accounts")
            return blocked

        except Exception as e:
            logger.error(f"Error fetching blocked accounts: {e}")
            return []

    def fetch_interactions(self):
        """Fetch interaction data from notifications API"""
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
                # Skip if not indexed (old notification)
                if not notif.get("isRead") is not None:
                    continue

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

    def collect(self):
        """Main collection job - run daily at 6 AM"""
        start_time = datetime.now()
        collection_date = date.today()

        try:
            # Authenticate (required)
            self.authenticate()

            logger.info(f"Starting collection for {collection_date}")
            logger.info(f"Tracking: {Config.BLUESKY_HANDLE}")

            # Fetch profile counts (includes ALL followers, even hidden)
            profile_counts = self.fetch_profile_counts()

            # Fetch actual accessible followers/following lists
            followers = self.fetch_all_followers()
            logger.info(
                f"Collected {len(followers)} followers (API) vs {profile_counts['followers']} (profile)"
            )

            following = self.fetch_all_following()
            logger.info(
                f"Collected {len(following)} following (API) vs {profile_counts['following']} (profile)"
            )

            # Calculate hidden counts
            hidden_followers = profile_counts["followers"] - len(followers)
            hidden_following = profile_counts["following"] - len(following)
            logger.info(
                f"Hidden: {hidden_followers} followers, {hidden_following} following"
            )

            # Fetch authenticated data
            muted = self.fetch_muted_accounts()
            blocked = self.fetch_blocked_accounts()
            engagement_data = self.fetch_engagement_data()

            # Save snapshot with profile counts
            self.db.save_snapshot(
                collection_date, followers, following, profile_counts, muted, blocked
            )

            # Save engagement data if available
            if engagement_data:
                self.db.save_engagement_data(collection_date, engagement_data)

            # Fetch and save interaction data
            interactions = self.fetch_interactions()
            if interactions:
                self.db.save_interactions(collection_date, interactions)

            # Detect and record changes
            self.db.detect_changes(collection_date)

            # Calculate metrics
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
