import sqlite3
from datetime import date, datetime, timedelta
from contextlib import contextmanager
from config import Config
import logging

logger = logging.getLogger(__name__)


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

            # Change events
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS follower_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    change_date DATE NOT NULL,
                    change_type TEXT NOT NULL,
                    did TEXT NOT NULL,
                    handle TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

    def detect_changes(self, collection_date):
        """Compare with previous day to detect changes"""
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

            # Detect unfollowers (in previous but not in current)
            cursor.execute(
                """
                INSERT INTO follower_changes (change_date, change_type, did, handle)
                SELECT ?, 'unfollowed', prev.did, prev.handle
                FROM followers_snapshot prev
                LEFT JOIN followers_snapshot curr 
                    ON prev.did = curr.did AND curr.collection_date = ?
                WHERE prev.collection_date = ? AND curr.did IS NULL
            """,
                (collection_date, collection_date, prev_date),
            )
            unfollower_count = cursor.rowcount

            # Detect new followers
            cursor.execute(
                """
                INSERT INTO follower_changes (change_date, change_type, did, handle)
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
                "non_mutual_following": non_mutual_following,
                "followers_only": followers_only,
            }

    def get_unfollowers(self, days=30):
        """Get list of unfollowers in last N days"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cutoff_date = (date.today() - timedelta(days=days)).isoformat()
            cursor.execute(
                """
                SELECT handle, did, change_date FROM follower_changes
                WHERE change_type = 'unfollowed' AND change_date > ?
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
                    datetime.now(),
                    status,
                    followers_collected,
                    following_collected,
                    error_message,
                    duration,
                ),
            )

    def save_engagement_data(self, collection_date, engagement_data):
        """Save post engagement metrics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Create engagement table if not exists
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
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(collection_date, post_uri)
                )
            """
            )

            for post in engagement_data:
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
                        post.get("created_at"),
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
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Create interactions table
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

            for interaction in interactions_data:
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
                        interaction.get("last_interaction", ""),
                    ),
                )

            logger.info(f"Saved interaction data for {len(interactions_data)} users")

    def get_top_interactors(self, days=30, limit=20):
        """Get top people who interacted with you"""
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

            # Get top interactors
            cursor.execute(
                """
                SELECT user_did, user_handle, user_display_name, user_avatar, user_bio,
                       likes_received, replies_received, reposts_received, quotes_received,
                       follows_received, interaction_score, last_interaction_date
                FROM interactions
                WHERE collection_date = ?
                ORDER BY interaction_score DESC
                LIMIT ?
            """,
                (latest_date, limit),
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
