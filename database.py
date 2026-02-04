import sqlite3
from datetime import date, datetime, timedelta, timezone
from contextlib import contextmanager
from config import Config
from time_utils import format_sqlite_date, maybe_format_sqlite_datetime
import logging

logger = logging.getLogger(__name__)


def _verify_still_follows(follower_did: str, user_did: str) -> bool:
    """
    Verify if follower_did still follows user_did by checking their following list.

    This helps filter out false unfollower detections caused by API pagination issues.
    Returns True if they still follow, False if they don't.
    """
    # Import here to avoid circular imports
    from public_api import PublicAPIClient

    try:
        client = PublicAPIClient()
        # Fetch the potential unfollower's following list
        following = client.get_all_following(follower_did)
        # Check if user_did is in their following list
        for account in following:
            if account.get("did") == user_did:
                return True
        return False
    except Exception as e:
        logger.warning(f"Failed to verify if {follower_did} still follows: {e}")
        # On error, assume they did unfollow (don't block the detection)
        return False


class Database:
    def __init__(self, db_path=Config.DATABASE_PATH):
        self.db_path = db_path
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        """Create tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Daily snapshots of followers
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS followers_snapshot (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    collection_date DATE NOT NULL,
                    did TEXT NOT NULL,
                    handle TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    display_name TEXT,
                    avatar_url TEXT,
                    bio TEXT,
                    UNIQUE(collection_date, did)
                )
            """
            )

            # Daily snapshots of following
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS following_snapshot (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    collection_date DATE NOT NULL,
                    did TEXT NOT NULL,
                    handle TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    display_name TEXT,
                    avatar_url TEXT,
                    bio TEXT,
                    UNIQUE(collection_date, did)
                )
            """
            )

            # Change events (with unique constraint to prevent duplicates)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS follower_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    change_date DATE NOT NULL,
                    change_type TEXT NOT NULL,
                    did TEXT NOT NULL,
                    handle TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(change_date, change_type, did)
                )
            """
            )

            # Daily metrics
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_date DATE NOT NULL UNIQUE,
                    follower_count INTEGER NOT NULL,
                    following_count INTEGER NOT NULL,
                    unfollower_count INTEGER DEFAULT 0,
                    new_follower_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Daily counts for tracking profile vs API discrepancies
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_counts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    collection_date DATE NOT NULL UNIQUE,
                    profile_followers INTEGER DEFAULT 0,
                    profile_following INTEGER DEFAULT 0,
                    api_followers INTEGER DEFAULT 0,
                    api_following INTEGER DEFAULT 0,
                    hidden_followers INTEGER DEFAULT 0,
                    hidden_following INTEGER DEFAULT 0,
                    muted_count INTEGER DEFAULT 0,
                    blocked_count INTEGER DEFAULT 0,
                    suspected_blocks_or_suspensions INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Collection log
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS collection_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL,
                    followers_collected INTEGER,
                    following_collected INTEGER,
                    error_message TEXT,
                    duration_seconds REAL
                )
            """
            )

            # Muted accounts snapshot (requires authentication)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS muted_snapshot (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    collection_date DATE NOT NULL,
                    did TEXT NOT NULL,
                    handle TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    display_name TEXT,
                    avatar_url TEXT,
                    bio TEXT,
                    UNIQUE(collection_date, did)
                )
            """
            )

            # Blocked accounts snapshot (requires authentication)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS blocked_snapshot (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    collection_date DATE NOT NULL,
                    did TEXT NOT NULL,
                    handle TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    display_name TEXT,
                    avatar_url TEXT,
                    bio TEXT,
                    UNIQUE(collection_date, did)
                )
            """
            )

            # Post engagement metrics
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS post_engagement (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    collection_date DATE NOT NULL,
                    post_uri TEXT NOT NULL,
                    post_text TEXT,
                    created_at TEXT,
                    like_count INTEGER DEFAULT 0,
                    repost_count INTEGER DEFAULT 0,
                    reply_count INTEGER DEFAULT 0,
                    quote_count INTEGER DEFAULT 0,
                    bookmark_count INTEGER DEFAULT 0,
                    indirect_likes INTEGER DEFAULT 0,
                    indirect_reposts INTEGER DEFAULT 0,
                    indirect_replies INTEGER DEFAULT 0,
                    indirect_bookmarks INTEGER DEFAULT 0,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(collection_date, post_uri)
                )
            """
            )

            # Daily engagement metrics aggregates
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_engagement_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_date DATE NOT NULL UNIQUE,
                    total_posts INTEGER DEFAULT 0,
                    posts_with_engagement INTEGER DEFAULT 0,
                    total_likes INTEGER DEFAULT 0,
                    total_reposts INTEGER DEFAULT 0,
                    total_replies INTEGER DEFAULT 0,
                    total_quotes INTEGER DEFAULT 0,
                    total_bookmarks INTEGER DEFAULT 0,
                    total_indirect_likes INTEGER DEFAULT 0,
                    total_indirect_reposts INTEGER DEFAULT 0,
                    total_indirect_replies INTEGER DEFAULT 0,
                    total_indirect_bookmarks INTEGER DEFAULT 0,
                    avg_engagement_per_post REAL DEFAULT 0,
                    engagement_rate REAL DEFAULT 0,
                    best_post_uri TEXT,
                    best_post_engagement INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Follower velocity tracking
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS follower_velocity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_date DATE NOT NULL UNIQUE,
                    new_followers INTEGER DEFAULT 0,
                    lost_followers INTEGER DEFAULT 0,
                    new_following INTEGER DEFAULT 0,
                    lost_following INTEGER DEFAULT 0,
                    net_follower_change INTEGER DEFAULT 0,
                    net_following_change INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Indexes
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_followers_date ON followers_snapshot(collection_date)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_following_date ON following_snapshot(collection_date)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_changes_date ON follower_changes(change_date)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_changes_type ON follower_changes(change_type)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_metrics_date ON daily_metrics(metric_date)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_daily_counts_date ON daily_counts(collection_date)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_muted_date ON muted_snapshot(collection_date)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_blocked_date ON blocked_snapshot(collection_date)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_post_engagement_date ON post_engagement(collection_date)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_post_engagement_uri ON post_engagement(post_uri)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_engagement_metrics_date ON daily_engagement_metrics(metric_date)"
            )

            # ===== NEW TABLES FOR CAR FILE DATA =====

            # Likes given (outgoing engagement from CAR file)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS likes_given (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    liked_post_uri TEXT NOT NULL UNIQUE,
                    liked_author_did TEXT,
                    liked_at TIMESTAMP NOT NULL,
                    rkey TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Reposts given (outgoing engagement from CAR file)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS reposts_given (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reposted_uri TEXT NOT NULL UNIQUE,
                    reposted_author_did TEXT,
                    reposted_at TIMESTAMP NOT NULL,
                    rkey TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Full post history (from CAR file - not just recent 50)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS posts_full (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_uri TEXT NOT NULL UNIQUE,
                    text TEXT,
                    post_created_at TIMESTAMP NOT NULL,
                    is_reply BOOLEAN DEFAULT 0,
                    is_self_reply BOOLEAN DEFAULT 0,
                    reply_to_uri TEXT,
                    has_embed BOOLEAN DEFAULT 0,
                    langs TEXT,
                    source TEXT DEFAULT 'car',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Backfill log (track CAR file backfill runs)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS backfill_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    did TEXT NOT NULL,
                    car_size_bytes INTEGER,
                    follows_count INTEGER DEFAULT 0,
                    posts_count INTEGER DEFAULT 0,
                    likes_count INTEGER DEFAULT 0,
                    reposts_count INTEGER DEFAULT 0,
                    blocks_count INTEGER DEFAULT 0,
                    duration_seconds REAL,
                    status TEXT NOT NULL
                )
            """
            )

            # Interactions (who interacts with you)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    collection_date DATE NOT NULL,
                    user_did TEXT NOT NULL,
                    user_handle TEXT NOT NULL,
                    user_display_name TEXT,
                    user_avatar TEXT,
                    user_bio TEXT,
                    likes_received INTEGER DEFAULT 0,
                    replies_received INTEGER DEFAULT 0,
                    reposts_received INTEGER DEFAULT 0,
                    quotes_received INTEGER DEFAULT 0,
                    follows_received INTEGER DEFAULT 0,
                    interaction_score INTEGER DEFAULT 0,
                    last_interaction_date TEXT,
                    UNIQUE(collection_date, user_did)
                )
            """
            )

            # Indexes for new tables
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_likes_given_author ON likes_given(liked_author_did)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_likes_given_date ON likes_given(liked_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_reposts_given_author ON reposts_given(reposted_author_did)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_reposts_given_date ON reposts_given(reposted_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_posts_full_date ON posts_full(post_created_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_backfill_log_did ON backfill_log(did)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_interactions_date ON interactions(collection_date)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_interactions_user ON interactions(user_did)"
            )

            # Add new columns to existing tables (SQLite ADD COLUMN is safe if column exists)
            try:
                cursor.execute(
                    "ALTER TABLE following_snapshot ADD COLUMN followed_at TIMESTAMP"
                )
            except sqlite3.OperationalError:
                pass  # Column already exists

            try:
                cursor.execute(
                    "ALTER TABLE following_snapshot ADD COLUMN source TEXT DEFAULT 'api'"
                )
            except sqlite3.OperationalError:
                pass

            try:
                cursor.execute(
                    "ALTER TABLE blocked_snapshot ADD COLUMN blocked_at TIMESTAMP"
                )
            except sqlite3.OperationalError:
                pass

            logger.info("Database initialized successfully")

    def save_snapshot(
        self,
        collection_date,
        followers,
        following,
        profile_counts=None,
        muted=None,
        blocked=None,
    ):
        """Save daily snapshot of followers, following, and counts"""
        collection_date = format_sqlite_date(collection_date)
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Save followers
            for follower in followers:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO followers_snapshot 
                    (collection_date, did, handle, display_name, avatar_url, bio)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        collection_date,
                        follower["did"],
                        follower["handle"],
                        follower.get("display_name", ""),
                        follower.get("avatar_url", ""),
                        follower.get("bio", ""),
                    ),
                )

            # Save following
            for follow in following:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO following_snapshot 
                    (collection_date, did, handle, display_name, avatar_url, bio)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        collection_date,
                        follow["did"],
                        follow["handle"],
                        follow.get("display_name", ""),
                        follow.get("avatar_url", ""),
                        follow.get("bio", ""),
                    ),
                )

            logger.info(
                f"Saved snapshot: {len(followers)} followers, {len(following)} following"
            )

            # Save muted accounts if provided
            if muted is not None:
                for account in muted:
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO muted_snapshot 
                        (collection_date, did, handle, display_name, avatar_url, bio)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (
                            collection_date,
                            account["did"],
                            account["handle"],
                            account.get("display_name", ""),
                            account.get("avatar_url", ""),
                            account.get("bio", ""),
                        ),
                    )
                logger.info(f"Saved {len(muted)} muted accounts")

            # Save blocked accounts if provided
            if blocked is not None:
                for account in blocked:
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO blocked_snapshot 
                        (collection_date, did, handle, display_name, avatar_url, bio)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (
                            collection_date,
                            account["did"],
                            account["handle"],
                            account.get("display_name", ""),
                            account.get("avatar_url", ""),
                            account.get("bio", ""),
                        ),
                    )
                logger.info(f"Saved {len(blocked)} blocked accounts")

            # Save daily counts if profile counts provided
            if profile_counts:
                api_followers = len(followers)
                api_following = len(following)
                hidden_followers = profile_counts["followers"] - api_followers
                hidden_following = profile_counts["following"] - api_following

                muted_count = len(muted) if muted else 0
                blocked_count = len(blocked) if blocked else 0

                # Calculate suspected blocks or suspensions
                # (hidden accounts that are NOT in our mute/block lists)
                suspected = max(0, hidden_followers - muted_count - blocked_count)

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO daily_counts 
                    (collection_date, profile_followers, profile_following, 
                     api_followers, api_following, hidden_followers, hidden_following,
                     muted_count, blocked_count, suspected_blocks_or_suspensions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        collection_date,
                        profile_counts["followers"],
                        profile_counts["following"],
                        api_followers,
                        api_following,
                        hidden_followers,
                        hidden_following,
                        muted_count,
                        blocked_count,
                        suspected,
                    ),
                )

                logger.info(
                    f"Saved daily counts - Hidden: {hidden_followers} followers ({muted_count} muted, {blocked_count} blocked, {suspected} suspected blocks/suspensions)"
                )

    def detect_changes(self, collection_date, user_did: str = None):
        """
        Compare with previous day to detect changes.

        Args:
            collection_date: The date of the current collection
            user_did: The DID of the tracked user. If provided, unfollowers will be
                      verified by checking if they still follow this user (prevents
                      false positives from API pagination issues).
        """
        collection_date = format_sqlite_date(collection_date)
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get previous collection date
            cursor.execute(
                """
                SELECT DISTINCT collection_date
                FROM followers_snapshot
                WHERE collection_date < ?
                ORDER BY collection_date DESC
                LIMIT 1
            """,
                (collection_date,),
            )

            prev_row = cursor.fetchone()
            if not prev_row:
                logger.info("No previous data to compare")
                # Save metrics for first run
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM followers_snapshot WHERE collection_date = ?
                """,
                    (collection_date,),
                )
                follower_count = cursor.fetchone()[0]

                cursor.execute(
                    """
                    SELECT COUNT(*) FROM following_snapshot WHERE collection_date = ?
                """,
                    (collection_date,),
                )
                following_count = cursor.fetchone()[0]

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO daily_metrics
                    (metric_date, follower_count, following_count, unfollower_count, new_follower_count)
                    VALUES (?, ?, ?, 0, 0)
                """,
                    (collection_date, follower_count, following_count),
                )
                return

            prev_date = prev_row[0]

            # Detect potential unfollowers (in previous but not in current)
            # First SELECT them, then verify before inserting
            cursor.execute(
                """
                SELECT prev.did, prev.handle
                FROM followers_snapshot prev
                LEFT JOIN followers_snapshot curr
                    ON prev.did = curr.did AND curr.collection_date = ?
                WHERE prev.collection_date = ? AND curr.did IS NULL
            """,
                (collection_date, prev_date),
            )
            potential_unfollowers = cursor.fetchall()

            # Verify and insert unfollowers
            unfollower_count = 0
            for row in potential_unfollowers:
                unfollower_did = row[0]
                unfollower_handle = row[1]

                # If user_did provided, verify the unfollow before recording
                if user_did:
                    if _verify_still_follows(unfollower_did, user_did):
                        logger.info(
                            f"False positive: {unfollower_handle} still follows (API pagination issue)"
                        )
                        continue

                # Verified unfollower - insert into follower_changes
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO follower_changes (change_date, change_type, did, handle)
                    VALUES (?, 'unfollowed', ?, ?)
                """,
                    (collection_date, unfollower_did, unfollower_handle),
                )
                if cursor.rowcount > 0:
                    unfollower_count += 1
                    logger.info(f"Verified unfollower: {unfollower_handle}")

            # Detect new followers
            # Use INSERT OR IGNORE to prevent duplicates if detect_changes runs multiple times
            cursor.execute(
                """
                INSERT OR IGNORE INTO follower_changes (change_date, change_type, did, handle)
                SELECT ?, 'new_follower', curr.did, curr.handle
                FROM followers_snapshot curr
                LEFT JOIN followers_snapshot prev
                    ON curr.did = prev.did AND prev.collection_date = ?
                WHERE curr.collection_date = ? AND prev.did IS NULL
            """,
                (collection_date, prev_date, collection_date),
            )
            new_follower_count = cursor.rowcount

            # Get current counts
            cursor.execute(
                "SELECT COUNT(*) FROM followers_snapshot WHERE collection_date = ?",
                (collection_date,),
            )
            follower_count = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM following_snapshot WHERE collection_date = ?",
                (collection_date,),
            )
            following_count = cursor.fetchone()[0]

            # Save metrics
            cursor.execute(
                """
                INSERT OR REPLACE INTO daily_metrics
                (metric_date, follower_count, following_count, unfollower_count, new_follower_count)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    collection_date,
                    follower_count,
                    following_count,
                    unfollower_count,
                    new_follower_count,
                ),
            )

            logger.info(
                f"Changes detected: {unfollower_count} unfollowers, {new_follower_count} new followers"
            )

    def get_user_profile(self):
        """Get the tracked user's profile (basic info from config)"""
        # Profile is configured, not stored in DB
        # Avatar could be fetched from public API if needed
        return None

    def get_stats(self, days=30):
        """Get stats for widget display"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get latest metrics
            cursor.execute(
                """
                SELECT follower_count, following_count, metric_date
                FROM daily_metrics
                ORDER BY metric_date DESC
                LIMIT 1
            """
            )
            row = cursor.fetchone()

            if not row:
                return {
                    "follower_count": 0,
                    "following_count": 0,
                    "unfollowers_30d": 0,
                    "new_followers_30d": 0,
                    "non_mutual_following": 0,
                    "followers_only": 0,
                }

            follower_count = row[0]
            following_count = row[1]
            latest_date = row[2]

            # Unfollowers in last N days
            cutoff_date = (
                datetime.strptime(latest_date, "%Y-%m-%d").date() - timedelta(days=days)
            ).isoformat()
            cursor.execute(
                """
                SELECT COUNT(*) FROM follower_changes
                WHERE change_type = 'unfollowed' AND change_date > ?
            """,
                (cutoff_date,),
            )
            unfollowers_30d = cursor.fetchone()[0]

            # New followers in last N days
            cursor.execute(
                """
                SELECT COUNT(*) FROM follower_changes
                WHERE change_type = 'new_follower' AND change_date > ?
            """,
                (cutoff_date,),
            )
            new_followers_30d = cursor.fetchone()[0]

            # Non-mutual following (you follow but they don't follow back)
            cursor.execute(
                """
                SELECT COUNT(*) FROM following_snapshot f
                LEFT JOIN followers_snapshot fo ON f.did = fo.did AND fo.collection_date = f.collection_date
                WHERE f.collection_date = ? AND fo.did IS NULL
            """,
                (latest_date,),
            )
            non_mutual_following = cursor.fetchone()[0]

            # Followers only (they follow you but you don't follow back)
            cursor.execute(
                """
                SELECT COUNT(*) FROM followers_snapshot fo
                LEFT JOIN following_snapshot f ON fo.did = f.did AND f.collection_date = fo.collection_date
                WHERE fo.collection_date = ? AND f.did IS NULL
            """,
                (latest_date,),
            )
            followers_only = cursor.fetchone()[0]

            return {
                "follower_count": follower_count,
                "following_count": following_count,
                "unfollowers_30d": unfollowers_30d,
                "new_followers_30d": new_followers_30d,
                "non_mutual_following": non_mutual_following,
                "followers_only": followers_only,
            }

    def get_unfollowers(self, days=30):
        """
        Get list of unfollowers in last N days.

        Deduplicates by DID - if the same person unfollowed multiple times,
        only shows the most recent unfollow event.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cutoff_date = (date.today() - timedelta(days=days)).isoformat()
            # Use GROUP BY to deduplicate by DID, keeping only the most recent unfollow
            cursor.execute(
                """
                SELECT handle, did, MAX(change_date) as change_date
                FROM follower_changes
                WHERE change_type = 'unfollowed' AND change_date > ?
                GROUP BY did
                ORDER BY change_date DESC
            """,
                (cutoff_date,),
            )
            return [
                {"handle": row[0], "did": row[1], "date": row[2]}
                for row in cursor.fetchall()
            ]

    def get_non_mutual_following(self):
        """Get people you follow but don't follow back (with profile data)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get latest collection date
            cursor.execute("SELECT MAX(collection_date) FROM followers_snapshot")
            latest_date = cursor.fetchone()[0]

            if not latest_date:
                return []

            # Find accounts in following but not in followers
            cursor.execute(
                """
                SELECT DISTINCT 
                    fw.did, fw.handle, fw.display_name, fw.avatar_url, fw.bio
                FROM following_snapshot fw
                LEFT JOIN followers_snapshot f
                    ON fw.did = f.did AND f.collection_date = ?
                WHERE fw.collection_date = ? AND f.did IS NULL
                ORDER BY fw.handle
            """,
                (latest_date, latest_date),
            )

            return [
                {
                    "did": row[0],
                    "handle": row[1],
                    "display_name": row[2],
                    "avatar_url": row[3],
                    "bio": row[4],
                }
                for row in cursor.fetchall()
            ]

    def get_followers_only(self):
        """Get people who follow you but you don't follow back (with profile data)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get latest collection date
            cursor.execute("SELECT MAX(collection_date) FROM followers_snapshot")
            latest_date = cursor.fetchone()[0]

            if not latest_date:
                return []

            # Find accounts in followers but not in following
            cursor.execute(
                """
                SELECT DISTINCT 
                    f.did, f.handle, f.display_name, f.avatar_url, f.bio
                FROM followers_snapshot f
                LEFT JOIN following_snapshot fw
                    ON f.did = fw.did AND fw.collection_date = ?
                WHERE f.collection_date = ? AND fw.did IS NULL
                ORDER BY f.handle
            """,
                (latest_date, latest_date),
            )

            return [
                {
                    "did": row[0],
                    "handle": row[1],
                    "display_name": row[2],
                    "avatar_url": row[3],
                    "bio": row[4],
                }
                for row in cursor.fetchall()
            ]

    def log_collection(
        self,
        collection_date,
        status,
        followers_collected,
        following_collected,
        error_message,
        duration,
    ):
        """Log collection run"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO collection_log 
                (run_date, status, followers_collected, following_collected, error_message, duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    maybe_format_sqlite_datetime(datetime.now(timezone.utc)),
                    status,
                    followers_collected,
                    following_collected,
                    error_message,
                    duration,
                ),
            )

    def save_engagement_data(self, collection_date, engagement_data):
        """Save post engagement metrics"""
        collection_date = format_sqlite_date(collection_date)
        with self.get_connection() as conn:
            cursor = conn.cursor()

            for post in engagement_data:
                created_at = maybe_format_sqlite_datetime(post.get("created_at"))
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO post_engagement
                    (collection_date, post_uri, post_text, created_at, like_count, repost_count, reply_count, quote_count,
                     bookmark_count, indirect_likes, indirect_reposts, indirect_replies, indirect_bookmarks)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        collection_date,
                        post.get("uri"),
                        post.get("text"),
                        created_at,
                        post.get("like_count", 0),
                        post.get("repost_count", 0),
                        post.get("reply_count", 0),
                        post.get("quote_count", 0),
                        post.get("bookmark_count", 0),
                        post.get("indirect_likes", 0),
                        post.get("indirect_reposts", 0),
                        post.get("indirect_replies", 0),
                        post.get("indirect_bookmarks", 0),
                    ),
                )

            logger.info(f"Saved engagement data for {len(engagement_data)} posts")

    def get_engagement_stats(self, days=30):
        """Get engagement statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='post_engagement'"
            )
            if not cursor.fetchone():
                return None

            # Get latest collection date
            cursor.execute("SELECT MAX(collection_date) FROM post_engagement")
            latest_date = cursor.fetchone()[0]
            if not latest_date:
                return None

            # Total engagement metrics
            cursor.execute(
                """
                SELECT 
                    SUM(like_count) as total_likes,
                    SUM(repost_count) as total_reposts,
                    SUM(reply_count) as total_replies,
                    SUM(quote_count) as total_quotes,
                    COUNT(*) as post_count
                FROM post_engagement
                WHERE collection_date = ?
            """,
                (latest_date,),
            )

            row = cursor.fetchone()

            # Top posts
            cursor.execute(
                """
                SELECT post_uri, post_text, like_count, repost_count, reply_count
                FROM post_engagement
                WHERE collection_date = ?
                ORDER BY (like_count + repost_count * 2) DESC
                LIMIT 5
            """,
                (latest_date,),
            )

            top_posts = [
                {
                    "uri": r[0],
                    "text": r[1],
                    "likes": r[2],
                    "reposts": r[3],
                    "replies": r[4],
                }
                for r in cursor.fetchall()
            ]

            return {
                "total_likes": row[0] or 0,
                "total_reposts": row[1] or 0,
                "total_replies": row[2] or 0,
                "total_quotes": row[3] or 0,
                "post_count": row[4] or 0,
                "top_posts": top_posts,
            }

    def get_hidden_follower_analytics(self, days=30):
        """Get analytics about hidden followers (blocks, mutes, suspensions)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='daily_counts'"
            )
            if not cursor.fetchone():
                return None

            # Get latest data
            cursor.execute(
                """
                SELECT 
                    profile_followers,
                    api_followers,
                    hidden_followers,
                    muted_count,
                    blocked_count,
                    suspected_blocks_or_suspensions
                FROM daily_counts
                ORDER BY collection_date DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            # Get historical trend
            cursor.execute(
                f"""
                SELECT 
                    collection_date,
                    profile_followers,
                    api_followers,
                    hidden_followers,
                    suspected_blocks_or_suspensions
                FROM daily_counts
                WHERE collection_date >= date('now', '-{days} days')
                ORDER BY collection_date DESC
            """
            )

            history = []
            for r in cursor.fetchall():
                history.append(
                    {
                        "date": r[0],
                        "profile_count": r[1],
                        "api_count": r[2],
                        "hidden": r[3],
                        "suspected_blocks": r[4],
                    }
                )

            return {
                "current": {
                    "profile_followers": row[0],
                    "api_followers": row[1],
                    "hidden_followers": row[2],
                    "muted_count": row[3],
                    "blocked_count": row[4],
                    "suspected_blocks_or_suspensions": row[5],
                },
                "history": history,
            }

    def get_follower_change_details(self, days=30):
        """Detect whether follower changes were unfollows or blocks/suspensions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get changes in both profile and API counts
            cursor.execute(
                f"""
                SELECT 
                    collection_date,
                    profile_followers - LAG(profile_followers) OVER (ORDER BY collection_date) as profile_change,
                    api_followers - LAG(api_followers) OVER (ORDER BY collection_date) as api_change,
                    suspected_blocks_or_suspensions - LAG(suspected_blocks_or_suspensions) OVER (ORDER BY collection_date) as suspected_change
                FROM daily_counts
                WHERE collection_date >= date('now', '-{days} days')
                ORDER BY collection_date DESC
            """
            )

            changes = []
            for row in cursor.fetchall():
                if row[1] is not None:  # Skip first row (no previous data)
                    change_type = "no_change"
                    if row[1] < 0 and row[2] < 0:
                        change_type = "real_unfollow"  # Both decreased = real unfollow
                    elif row[1] == 0 and row[2] < 0:
                        change_type = "blocked_or_suspended"  # Only API decreased = block/suspension
                    elif row[1] < 0 and row[2] == 0:
                        change_type = (
                            "cleanup"  # Only profile decreased = index cleanup
                        )

                    changes.append(
                        {
                            "date": row[0],
                            "profile_change": row[1],
                            "api_change": row[2],
                            "suspected_change": row[3] if row[3] else 0,
                            "type": change_type,
                        }
                    )

            return changes

    def get_mutual_follows(self):
        """Get accounts that are mutual follows (you follow each other)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get latest collection date
            cursor.execute("SELECT MAX(collection_date) FROM followers_snapshot")
            latest_date = cursor.fetchone()[0]

            if not latest_date:
                return []

            # Find mutual follows (in both followers and following)
            cursor.execute(
                """
                SELECT DISTINCT 
                    f.did, f.handle, f.display_name, f.avatar_url, f.bio
                FROM followers_snapshot f
                INNER JOIN following_snapshot fw
                    ON f.did = fw.did AND f.collection_date = fw.collection_date
                WHERE f.collection_date = ?
                ORDER BY f.handle
            """,
                (latest_date,),
            )

            return [
                {
                    "did": row[0],
                    "handle": row[1],
                    "display_name": row[2],
                    "avatar_url": row[3],
                    "bio": row[4],
                }
                for row in cursor.fetchall()
            ]

    def get_muted_accounts_with_profile(self):
        """Get muted accounts with full profile data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT MAX(collection_date) FROM muted_snapshot")
            latest_date = cursor.fetchone()[0]

            if not latest_date:
                return []

            cursor.execute(
                """
                SELECT did, handle, display_name, avatar_url, bio
                FROM muted_snapshot
                WHERE collection_date = ?
                ORDER BY handle
            """,
                (latest_date,),
            )

            return [
                {
                    "did": row[0],
                    "handle": row[1],
                    "display_name": row[2],
                    "avatar_url": row[3],
                    "bio": row[4],
                }
                for row in cursor.fetchall()
            ]

    def get_blocked_accounts_with_profile(self):
        """Get blocked accounts with full profile data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT MAX(collection_date) FROM blocked_snapshot")
            latest_date = cursor.fetchone()[0]

            if not latest_date:
                return []

            cursor.execute(
                """
                SELECT did, handle, display_name, avatar_url, bio
                FROM blocked_snapshot
                WHERE collection_date = ?
                ORDER BY handle
            """,
                (latest_date,),
            )

            return [
                {
                    "did": row[0],
                    "handle": row[1],
                    "display_name": row[2],
                    "avatar_url": row[3],
                    "bio": row[4],
                }
                for row in cursor.fetchall()
            ]

    def save_interactions(self, collection_date, interactions_data):
        """Save interaction data from notifications"""
        collection_date = format_sqlite_date(collection_date)
        with self.get_connection() as conn:
            cursor = conn.cursor()

            for interaction in interactions_data:
                last_interaction = maybe_format_sqlite_datetime(
                    interaction.get("last_interaction")
                )
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO interactions 
                    (collection_date, user_did, user_handle, user_display_name, user_avatar, user_bio,
                     likes_received, replies_received, reposts_received, quotes_received, follows_received,
                     interaction_score, last_interaction_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        collection_date,
                        interaction.get("did"),
                        interaction.get("handle"),
                        interaction.get("display_name", ""),
                        interaction.get("avatar", ""),
                        interaction.get("bio", ""),
                        interaction.get("likes", 0),
                        interaction.get("replies", 0),
                        interaction.get("reposts", 0),
                        interaction.get("quotes", 0),
                        interaction.get("follows", 0),
                        interaction.get("score", 0),
                        last_interaction,
                    ),
                )

            logger.info(f"Saved interaction data for {len(interactions_data)} users")

    def get_top_interactors(self, days=30, limit=20):
        """Get top people who interacted with you within the time period"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='interactions'"
            )
            if not cursor.fetchone():
                return []

            # Get latest date
            cursor.execute("SELECT MAX(collection_date) FROM interactions")
            latest_date = cursor.fetchone()[0]
            if not latest_date:
                return []

            # Get top interactors filtered by last_interaction_date within time period
            cursor.execute(
                """
                SELECT user_did, user_handle, user_display_name, user_avatar, user_bio,
                       likes_received, replies_received, reposts_received, quotes_received,
                       follows_received, interaction_score, last_interaction_date
                FROM interactions
                WHERE collection_date = ?
                AND DATE(last_interaction_date) >= DATE('now', '-' || ? || ' days')
                ORDER BY interaction_score DESC
                LIMIT ?
            """,
                (latest_date, days, limit),
            )

            interactors = []
            for row in cursor.fetchall():
                interactors.append(
                    {
                        "did": row[0],
                        "handle": row[1],
                        "display_name": row[2] or row[1],
                        "avatar": row[3],
                        "bio": row[4],
                        "likes": row[5],
                        "replies": row[6],
                        "reposts": row[7],
                        "quotes": row[8],
                        "follows": row[9],
                        "score": row[10],
                        "last_interaction": row[11],
                    }
                )

            return interactors

    def get_advanced_metrics(self):
        """Get advanced analytics metrics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if we have engagement data
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='post_engagement'"
            )
            if not cursor.fetchone():
                return None

            # Get latest date
            cursor.execute("SELECT MAX(collection_date) FROM post_engagement")
            latest_date = cursor.fetchone()[0]

            if not latest_date:
                return None

            # Calculate engagement rate
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as post_count,
                    AVG(like_count) as avg_likes,
                    AVG(repost_count) as avg_reposts,
                    AVG(reply_count) as avg_replies,
                    MAX(like_count) as max_likes,
                    SUM(like_count) as total_likes,
                    SUM(repost_count) as total_reposts,
                    SUM(reply_count) as total_replies
                FROM post_engagement
                WHERE collection_date = ?
            """,
                (latest_date,),
            )

            row = cursor.fetchone()

            if not row or not row[0]:
                return None

            # Get follower growth (if we have historical data)
            cursor.execute(
                """
                SELECT 
                    collection_date,
                    api_followers
                FROM daily_counts
                ORDER BY collection_date DESC
                LIMIT 30
            """
            )

            follower_history = []
            for r in cursor.fetchall():
                follower_history.append({"date": r[0], "followers": r[1]})

            # Calculate growth rate
            growth_rate = 0
            if len(follower_history) >= 2:
                oldest = follower_history[-1]["followers"]
                newest = follower_history[0]["followers"]
                if oldest > 0:
                    growth_rate = ((newest - oldest) / oldest) * 100

            return {
                "post_count": row[0],
                "avg_likes": round(row[1], 2) if row[1] else 0,
                "avg_reposts": round(row[2], 2) if row[2] else 0,
                "avg_replies": round(row[3], 2) if row[3] else 0,
                "max_likes": row[4],
                "total_likes": row[5],
                "total_reposts": row[6],
                "total_replies": row[7],
                "engagement_rate": round(
                    (row[1] + row[2] * 2 + row[3]) if row[1] else 0, 2
                ),
                "follower_growth_30d": round(growth_rate, 2),
                "follower_history": follower_history,
            }

    # ===== CAR FILE DATA METHODS =====

    def save_likes_given(self, likes_data):
        """Save outgoing likes from CAR file data.

        Args:
            likes_data: List of dicts with keys:
                - liked_post_uri: URI of the liked post
                - liked_author_did: DID of the post author (optional)
                - liked_at: Timestamp when like was created
                - rkey: Record key (optional)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            inserted = 0
            for like in likes_data:
                try:
                    liked_at = maybe_format_sqlite_datetime(like.get("liked_at"))
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO likes_given
                        (liked_post_uri, liked_author_did, liked_at, rkey)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            like.get("liked_post_uri"),
                            like.get("liked_author_did"),
                            liked_at,
                            like.get("rkey"),
                        ),
                    )
                    if cursor.rowcount > 0:
                        inserted += 1
                except sqlite3.Error as e:
                    logger.warning(f"Error saving like: {e}")

            logger.info(f"Saved {inserted} new likes (out of {len(likes_data)} total)")
            return inserted

    def save_reposts_given(self, reposts_data):
        """Save outgoing reposts from CAR file data.

        Args:
            reposts_data: List of dicts with keys:
                - reposted_uri: URI of the reposted post
                - reposted_author_did: DID of the post author (optional)
                - reposted_at: Timestamp when repost was created
                - rkey: Record key (optional)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            inserted = 0
            for repost in reposts_data:
                try:
                    reposted_at = maybe_format_sqlite_datetime(repost.get("reposted_at"))
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO reposts_given
                        (reposted_uri, reposted_author_did, reposted_at, rkey)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            repost.get("reposted_uri"),
                            repost.get("reposted_author_did"),
                            reposted_at,
                            repost.get("rkey"),
                        ),
                    )
                    if cursor.rowcount > 0:
                        inserted += 1
                except sqlite3.Error as e:
                    logger.warning(f"Error saving repost: {e}")

            logger.info(f"Saved {inserted} new reposts (out of {len(reposts_data)} total)")
            return inserted

    def save_posts_from_car(self, posts_data):
        """Save full post history from CAR file data.

        Args:
            posts_data: List of dicts with keys:
                - post_uri: Unique post URI
                - text: Post text content
                - post_created_at: Timestamp when post was created
                - is_reply: Boolean whether post is a reply
                - is_self_reply: Boolean whether post is a reply to own post (thread)
                - reply_to_uri: URI of parent post if reply
                - has_embed: Boolean whether post has embeds
                - langs: Language tags (comma-separated)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            inserted = 0
            for post in posts_data:
                try:
                    post_created_at = maybe_format_sqlite_datetime(post.get("post_created_at"))
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO posts_full
                        (post_uri, text, post_created_at, is_reply, is_self_reply, reply_to_uri, has_embed, langs, source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'car')
                        """,
                        (
                            post.get("post_uri"),
                            post.get("text"),
                            post_created_at,
                            1 if post.get("is_reply") else 0,
                            1 if post.get("is_self_reply") else 0,
                            post.get("reply_to_uri"),
                            1 if post.get("has_embed") else 0,
                            post.get("langs"),
                        ),
                    )
                    if cursor.rowcount > 0:
                        inserted += 1
                except sqlite3.Error as e:
                    logger.warning(f"Error saving post: {e}")

            logger.info(f"Saved {inserted} new posts (out of {len(posts_data)} total)")
            return inserted

    def save_following_with_timestamps(self, collection_date, following_data):
        """Save following list with CAR timestamps (followed_at).

        Args:
            collection_date: Date of collection
            following_data: List of dicts with keys:
                - did: User DID
                - handle: User handle
                - followed_at: Timestamp when follow was created (from CAR)
                - display_name, avatar_url, bio: Profile info (optional)
        """
        collection_date = format_sqlite_date(collection_date)
        with self.get_connection() as conn:
            cursor = conn.cursor()

            for follow in following_data:
                followed_at = maybe_format_sqlite_datetime(follow.get("followed_at"))
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO following_snapshot
                    (collection_date, did, handle, display_name, avatar_url, bio, followed_at, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'car')
                    """,
                    (
                        collection_date,
                        follow["did"],
                        follow.get("handle", ""),
                        follow.get("display_name", ""),
                        follow.get("avatar_url", ""),
                        follow.get("bio", ""),
                        followed_at,
                    ),
                )

            logger.info(f"Saved {len(following_data)} following with timestamps")

    def save_blocks_with_timestamps(self, collection_date, blocks_data):
        """Save blocks with CAR timestamps (blocked_at).

        Args:
            collection_date: Date of collection
            blocks_data: List of dicts with keys:
                - did: Blocked user DID
                - handle: Blocked user handle
                - blocked_at: Timestamp when block was created (from CAR)
        """
        collection_date = format_sqlite_date(collection_date)
        with self.get_connection() as conn:
            cursor = conn.cursor()

            for block in blocks_data:
                blocked_at = maybe_format_sqlite_datetime(block.get("blocked_at"))
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO blocked_snapshot
                    (collection_date, did, handle, display_name, avatar_url, bio, blocked_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        collection_date,
                        block["did"],
                        block.get("handle", ""),
                        block.get("display_name", ""),
                        block.get("avatar_url", ""),
                        block.get("bio", ""),
                        blocked_at,
                    ),
                )

            logger.info(f"Saved {len(blocks_data)} blocks with timestamps")

    def log_backfill(self, did, car_size_bytes, stats, duration_seconds, status):
        """Log a CAR file backfill run.

        Args:
            did: User DID that was backfilled
            car_size_bytes: Size of CAR file in bytes
            stats: Dict with counts (follows, posts, likes, reposts, blocks)
            duration_seconds: Time taken for backfill
            status: 'success' or 'error'
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO backfill_log
                (did, car_size_bytes, follows_count, posts_count, likes_count,
                 reposts_count, blocks_count, duration_seconds, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    did,
                    car_size_bytes,
                    stats.get("follows", 0),
                    stats.get("posts", 0),
                    stats.get("likes", 0),
                    stats.get("reposts", 0),
                    stats.get("blocks", 0),
                    duration_seconds,
                    status,
                ),
            )
            logger.info(f"Logged backfill run for {did}: {status}")

    def get_likes_given_stats(self, days=None):
        """Get statistics about outgoing likes.

        Args:
            days: Optional - only count likes within last N days

        Returns:
            Dict with total_likes, top_liked_accounts, recent_likes
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Total likes
            if days:
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM likes_given
                    WHERE liked_at >= datetime('now', '-' || ? || ' days')
                    """,
                    (days,),
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM likes_given")
            total_likes = cursor.fetchone()[0]

            # Top liked accounts (by DID)
            if days:
                cursor.execute(
                    """
                    SELECT liked_author_did, COUNT(*) as like_count
                    FROM likes_given
                    WHERE liked_author_did IS NOT NULL
                    AND liked_at >= datetime('now', '-' || ? || ' days')
                    GROUP BY liked_author_did
                    ORDER BY like_count DESC
                    LIMIT 10
                    """,
                    (days,),
                )
            else:
                cursor.execute(
                    """
                    SELECT liked_author_did, COUNT(*) as like_count
                    FROM likes_given
                    WHERE liked_author_did IS NOT NULL
                    GROUP BY liked_author_did
                    ORDER BY like_count DESC
                    LIMIT 10
                    """
                )
            top_accounts = [
                {"did": row[0], "like_count": row[1]}
                for row in cursor.fetchall()
            ]

            # Recent likes (last 10)
            cursor.execute(
                """
                SELECT liked_post_uri, liked_author_did, liked_at
                FROM likes_given
                ORDER BY liked_at DESC
                LIMIT 10
                """
            )
            recent_likes = [
                {"uri": row[0], "author_did": row[1], "liked_at": row[2]}
                for row in cursor.fetchall()
            ]

            return {
                "total_likes": total_likes,
                "top_liked_accounts": top_accounts,
                "recent_likes": recent_likes,
            }

    def get_reposts_given_stats(self, days=None):
        """Get statistics about outgoing reposts.

        Args:
            days: Optional - only count reposts within last N days

        Returns:
            Dict with total_reposts, top_reposted_accounts, recent_reposts
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Total reposts
            if days:
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM reposts_given
                    WHERE reposted_at >= datetime('now', '-' || ? || ' days')
                    """,
                    (days,),
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM reposts_given")
            total_reposts = cursor.fetchone()[0]

            # Top reposted accounts
            if days:
                cursor.execute(
                    """
                    SELECT reposted_author_did, COUNT(*) as repost_count
                    FROM reposts_given
                    WHERE reposted_author_did IS NOT NULL
                    AND reposted_at >= datetime('now', '-' || ? || ' days')
                    GROUP BY reposted_author_did
                    ORDER BY repost_count DESC
                    LIMIT 10
                    """,
                    (days,),
                )
            else:
                cursor.execute(
                    """
                    SELECT reposted_author_did, COUNT(*) as repost_count
                    FROM reposts_given
                    WHERE reposted_author_did IS NOT NULL
                    GROUP BY reposted_author_did
                    ORDER BY repost_count DESC
                    LIMIT 10
                    """
                )
            top_accounts = [
                {"did": row[0], "repost_count": row[1]}
                for row in cursor.fetchall()
            ]

            # Recent reposts
            cursor.execute(
                """
                SELECT reposted_uri, reposted_author_did, reposted_at
                FROM reposts_given
                ORDER BY reposted_at DESC
                LIMIT 10
                """
            )
            recent_reposts = [
                {"uri": row[0], "author_did": row[1], "reposted_at": row[2]}
                for row in cursor.fetchall()
            ]

            return {
                "total_reposts": total_reposts,
                "top_reposted_accounts": top_accounts,
                "recent_reposts": recent_reposts,
            }

    def get_posts_full_stats(self, days=None):
        """Get statistics about full post history.

        Args:
            days: Optional - only count posts within last N days

        Returns:
            Dict with total_posts, original_count, thread_count,
            replies_to_others_count, etc.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            where_clause = ""
            params = ()
            if days:
                where_clause = "WHERE post_created_at >= datetime('now', '-' || ? || ' days')"
                params = (days,)

            # Total posts and detailed breakdown
            cursor.execute(
                f"""
                SELECT
                    COUNT(*) as total_posts,
                    SUM(CASE WHEN is_reply = 0 THEN 1 ELSE 0 END) as original_count,
                    SUM(CASE WHEN is_reply = 1 AND is_self_reply = 1 THEN 1 ELSE 0 END) as thread_count,
                    SUM(CASE WHEN is_reply = 1 AND is_self_reply = 0 THEN 1 ELSE 0 END) as replies_to_others_count,
                    SUM(CASE WHEN has_embed = 1 THEN 1 ELSE 0 END) as with_embed_count
                FROM posts_full
                {where_clause}
                """,
                params,
            )
            row = cursor.fetchone()

            total_posts = row[0] or 0
            original_count = row[1] or 0
            thread_count = row[2] or 0
            replies_to_others_count = row[3] or 0
            with_embed_count = row[4] or 0

            # Recent posts
            cursor.execute(
                """
                SELECT post_uri, text, post_created_at, is_reply, is_self_reply
                FROM posts_full
                ORDER BY post_created_at DESC
                LIMIT 10
                """
            )
            recent_posts = [
                {
                    "uri": row[0],
                    "text": row[1][:100] if row[1] else "",
                    "created_at": row[2],
                    "is_reply": bool(row[3]),
                    "is_self_reply": bool(row[4]),
                }
                for row in cursor.fetchall()
            ]

            return {
                "total_posts": total_posts,
                "original_count": original_count,
                "thread_count": thread_count,
                "replies_to_others_count": replies_to_others_count,
                "with_embed_count": with_embed_count,
                "engagement_ratio": round(replies_to_others_count / total_posts, 2) if total_posts > 0 else 0,
                "recent_posts": recent_posts,
            }

    def get_following_with_timestamps(self):
        """Get following list with follow timestamps from CAR data."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get latest collection date
            cursor.execute("SELECT MAX(collection_date) FROM following_snapshot")
            latest_date = cursor.fetchone()[0]

            if not latest_date:
                return []

            cursor.execute(
                """
                SELECT did, handle, display_name, avatar_url, bio, followed_at, source
                FROM following_snapshot
                WHERE collection_date = ?
                ORDER BY followed_at DESC NULLS LAST
                """,
                (latest_date,),
            )

            return [
                {
                    "did": row[0],
                    "handle": row[1],
                    "display_name": row[2],
                    "avatar_url": row[3],
                    "bio": row[4],
                    "followed_at": row[5],
                    "source": row[6],
                }
                for row in cursor.fetchall()
            ]

    def get_engagement_balance(self, days=None, user_did=None):
        """Get comparison of engagement given vs received.

        Args:
            days: Optional number of days to filter by
            user_did: Deprecated - no longer needed (is_self_reply column used instead)

        Returns dict with:
            - given: {likes, reposts, replies}
            - received: {likes, reposts, replies}
            - ratio: given/received (< 1 means receiving more)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Likes given
            if days:
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM likes_given
                    WHERE liked_at >= datetime('now', '-' || ? || ' days')
                    """,
                    (days,),
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM likes_given")
            likes_given = cursor.fetchone()[0] or 0

            # Reposts given
            if days:
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM reposts_given
                    WHERE reposted_at >= datetime('now', '-' || ? || ' days')
                    """,
                    (days,),
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM reposts_given")
            reposts_given = cursor.fetchone()[0] or 0

            # Replies given (only replies to OTHER users, excluding self-replies/threads)
            # Uses is_self_reply column for clean filtering
            if days:
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM posts_full
                    WHERE is_reply = 1 AND is_self_reply = 0
                    AND post_created_at >= datetime('now', '-' || ? || ' days')
                    """,
                    (days,),
                )
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM posts_full
                    WHERE is_reply = 1 AND is_self_reply = 0
                """)
            replies_given = cursor.fetchone()[0] or 0

            # Received engagement - use same logic as engagement timeline
            # This calculates engagement received within the time period
            if days:
                # Sum engagement from posts within the time period using same query as timeline
                cursor.execute(
                    """
                    SELECT
                        COALESCE(SUM(total_likes), 0),
                        COALESCE(SUM(total_reposts), 0),
                        COALESCE(SUM(total_replies), 0)
                    FROM (
                        -- Part 1: Initial engagement from first collection -> use post creation date
                        SELECT
                            DATE(pe.created_at) as engagement_date,
                            pe.like_count + COALESCE(pe.indirect_likes, 0) as total_likes,
                            pe.repost_count + COALESCE(pe.indirect_reposts, 0) as total_reposts,
                            pe.reply_count + COALESCE(pe.indirect_replies, 0) as total_replies
                        FROM post_engagement pe
                        WHERE pe.created_at IS NOT NULL
                        AND pe.collection_date = (
                            SELECT MIN(pe2.collection_date)
                            FROM post_engagement pe2
                            WHERE pe2.post_uri = pe.post_uri
                        )

                        UNION ALL

                        -- Part 2: Engagement deltas from subsequent collections -> use collection date
                        SELECT
                            curr.collection_date as engagement_date,
                            MAX(0, (curr.like_count + COALESCE(curr.indirect_likes, 0)) -
                                (prev.like_count + COALESCE(prev.indirect_likes, 0))) as total_likes,
                            MAX(0, (curr.repost_count + COALESCE(curr.indirect_reposts, 0)) -
                                (prev.repost_count + COALESCE(prev.indirect_reposts, 0))) as total_reposts,
                            MAX(0, (curr.reply_count + COALESCE(curr.indirect_replies, 0)) -
                                (prev.reply_count + COALESCE(prev.indirect_replies, 0))) as total_replies
                        FROM post_engagement curr
                        INNER JOIN post_engagement prev
                            ON curr.post_uri = prev.post_uri
                            AND prev.collection_date = (
                                SELECT MAX(p.collection_date)
                                FROM post_engagement p
                                WHERE p.post_uri = curr.post_uri
                                AND p.collection_date < curr.collection_date
                            )
                        WHERE curr.collection_date > (
                            SELECT MIN(pe3.collection_date)
                            FROM post_engagement pe3
                            WHERE pe3.post_uri = curr.post_uri
                        )
                    ) subquery
                    WHERE engagement_date >= date('now', '-' || ? || ' days')
                    """,
                    (days,),
                )
            else:
                # All time - just sum latest snapshot
                cursor.execute("SELECT MAX(collection_date) FROM post_engagement")
                latest_date = cursor.fetchone()[0]
                if latest_date:
                    cursor.execute(
                        """
                        SELECT
                            COALESCE(SUM(like_count + COALESCE(indirect_likes, 0)), 0),
                            COALESCE(SUM(repost_count + COALESCE(indirect_reposts, 0)), 0),
                            COALESCE(SUM(reply_count + COALESCE(indirect_replies, 0)), 0)
                        FROM post_engagement
                        WHERE collection_date = ?
                        """,
                        (latest_date,),
                    )
                else:
                    cursor.execute("SELECT 0, 0, 0")

            row = cursor.fetchone()
            likes_received = row[0] or 0
            reposts_received = row[1] or 0
            replies_received = row[2] or 0

            # Calculate totals and ratio
            total_given = likes_given + reposts_given + replies_given
            total_received = likes_received + reposts_received + replies_received

            ratio = 0
            if total_received > 0:
                ratio = round(total_given / total_received, 2)

            return {
                "given": {
                    "likes": likes_given,
                    "reposts": reposts_given,
                    "replies": replies_given,
                    "total": total_given,
                },
                "received": {
                    "likes": likes_received,
                    "reposts": reposts_received,
                    "replies": replies_received,
                    "total": total_received,
                },
                "ratio": ratio,
                "balance_type": "giver" if ratio > 1 else "receiver" if ratio < 1 else "balanced",
            }

    def get_backfill_history(self, limit=10):
        """Get recent backfill run history."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT run_date, did, car_size_bytes, follows_count, posts_count,
                       likes_count, reposts_count, blocks_count, duration_seconds, status
                FROM backfill_log
                ORDER BY run_date DESC
                LIMIT ?
                """,
                (limit,),
            )

            return [
                {
                    "run_date": row[0],
                    "did": row[1],
                    "car_size_bytes": row[2],
                    "follows_count": row[3],
                    "posts_count": row[4],
                    "likes_count": row[5],
                    "reposts_count": row[6],
                    "blocks_count": row[7],
                    "duration_seconds": row[8],
                    "status": row[9],
                }
                for row in cursor.fetchall()
            ]

    def cleanup_duplicate_posts(self):
        """Remove duplicate posts from posts_full table.

        Duplicates are identified by matching text + post_created_at.
        Keeps only the first occurrence (lowest id) of each unique post.

        Returns:
            dict with cleanup statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Count before cleanup
            cursor.execute("SELECT COUNT(*) FROM posts_full")
            total_before = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT DISTINCT text, post_created_at FROM posts_full
                )
            """)
            unique_count = cursor.fetchone()[0]

            duplicates_to_remove = total_before - unique_count

            if duplicates_to_remove > 0:
                # Delete duplicates, keeping the row with the lowest id for each unique combination
                cursor.execute("""
                    DELETE FROM posts_full
                    WHERE id NOT IN (
                        SELECT MIN(id)
                        FROM posts_full
                        GROUP BY text, post_created_at
                    )
                """)
                conn.commit()

            # Count after cleanup
            cursor.execute("SELECT COUNT(*) FROM posts_full")
            total_after = cursor.fetchone()[0]

            logger.info(f"Cleanup: removed {duplicates_to_remove} duplicate posts ({total_before} -> {total_after})")

            return {
                "total_before": total_before,
                "total_after": total_after,
                "duplicates_removed": duplicates_to_remove,
                "unique_posts": unique_count,
            }
