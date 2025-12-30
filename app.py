from flask import Flask, jsonify, request
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from datetime import datetime
import logging

from config import Config
from database import Database
from templates import get_report_html
from collector import BlueskyCollector

# Validate configuration before starting
Config.validate()

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
db = Database()
collector = BlueskyCollector()

# Prometheus metrics
follower_count = Gauge("bluesky_follower_count", "Current follower count")
following_count = Gauge("bluesky_following_count", "Current following count")
unfollowers_30d = Gauge("bluesky_unfollowers_30d", "Unfollowers in last 30 days")
non_mutual_following = Gauge(
    "bluesky_non_mutual_following", "People you follow who dont follow back"
)
followers_only = Gauge(
    "bluesky_followers_only", "People who follow you but you dont follow back"
)
api_requests = Counter(
    "bluesky_api_requests_total", "Total API requests", ["endpoint", "status"]
)
collection_duration = Histogram(
    "bluesky_collection_duration_seconds", "Collection job duration"
)

# Scheduler
scheduler = BackgroundScheduler(timezone=timezone(Config.TIMEZONE))


def scheduled_collection():
    """Run collection job"""
    logger.info("Starting scheduled collection")
    with collection_duration.time():
        success = collector.collect()

    if success:
        update_metrics()


def update_metrics():
    """Update Prometheus metrics from database"""
    try:
        stats = db.get_stats()
        follower_count.set(stats["follower_count"])
        following_count.set(stats["following_count"])
        unfollowers_30d.set(stats["unfollowers_30d"])
        non_mutual_following.set(stats["non_mutual_following"])
        followers_only.set(stats["followers_only"])
        logger.info("Metrics updated successfully")
    except Exception as e:
        logger.error(f"Failed to update metrics: {e}")


# API Endpoints


@app.route("/api/stats")
def api_stats():
    """Homepage widget summary"""
    try:
        stats = db.get_stats(days=Config.WIDGET_DAYS)
        api_requests.labels(endpoint="/api/stats", status="success").inc()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"/api/stats error: {e}")
        api_requests.labels(endpoint="/api/stats", status="error").inc()
        return jsonify({"error": "Internal error"}), 500


@app.route("/api/unfollowers")
def api_unfollowers():
    """List of recent unfollowers"""
    try:
        days = int(request.args.get("days", Config.WIDGET_DAYS))
        unfollowers = db.get_unfollowers(days=days)
        api_requests.labels(endpoint="/api/unfollowers", status="success").inc()
        return jsonify({"unfollowers": unfollowers, "days": days})
    except Exception as e:
        logger.error(f"/api/unfollowers error: {e}")
        api_requests.labels(endpoint="/api/unfollowers", status="error").inc()
        return jsonify({"error": "Internal error"}), 500


@app.route("/api/non-mutual")
def api_non_mutual():
    """People you follow but dont follow back"""
    try:
        accounts = db.get_non_mutual_following()
        api_requests.labels(endpoint="/api/non-mutual", status="success").inc()
        return jsonify({"accounts": accounts, "count": len(accounts)})
    except Exception as e:
        logger.error(f"/api/non-mutual error: {e}")
        api_requests.labels(endpoint="/api/non-mutual", status="error").inc()
        return jsonify({"error": "Internal error"}), 500


@app.route("/api/followers-only")
def api_followers_only():
    """People who follow you but you dont follow back"""
    try:
        accounts = db.get_followers_only()
        api_requests.labels(endpoint="/api/followers-only", status="success").inc()
        return jsonify({"accounts": accounts, "count": len(accounts)})
    except Exception as e:
        logger.error(f"/api/followers-only error: {e}")
        api_requests.labels(endpoint="/api/followers-only", status="error").inc()
        return jsonify({"error": "Internal error"}), 500


@app.route("/api/collect", methods=["POST"])
def api_collect():
    """Trigger manual data collection"""
    try:
        logger.info("Manual collection triggered via API")
        success = collector.collect()

        if success:
            update_metrics()
            api_requests.labels(endpoint="/api/collect", status="success").inc()
            return jsonify({"success": True, "message": "Data collected successfully"})
        else:
            api_requests.labels(endpoint="/api/collect", status="error").inc()
            return jsonify({"success": False, "message": "Collection failed"}), 500
    except Exception as e:
        logger.error(f"/api/collect error: {e}")
        api_requests.labels(endpoint="/api/collect", status="error").inc()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/report")
def report():
    """Comprehensive HTML report page with all analytics"""
    try:
        # Get last collection time
        from datetime import datetime
        import sqlite3

        last_updated = "Never"
        try:
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT MAX(run_date) FROM collection_log WHERE status = "success"'
            )
            last_run = cursor.fetchone()[0]
            if last_run:
                last_updated = datetime.fromisoformat(last_run).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            conn.close()
        except Exception:
            pass

        # Gather all data
        stats = db.get_stats(days=30)
        unfollowers = db.get_unfollowers(days=30)
        non_mutual = db.get_non_mutual_following()
        followers_only = db.get_followers_only()
        hidden_analytics = db.get_hidden_follower_analytics(days=30)
        if hidden_analytics is None:
            hidden_analytics = {}
        change_history = db.get_follower_change_details(days=30)
        mutual_follows = db.get_mutual_follows()
        advanced_metrics = db.get_advanced_metrics()
        if advanced_metrics is None:
            advanced_metrics = {}
        top_interactors = db.get_top_interactors(days=30, limit=20)
        muted_accounts = db.get_muted_accounts_with_profile()
        blocked_accounts = db.get_blocked_accounts_with_profile()
        hidden_categories = {
            "muted": {"accounts": muted_accounts, "count": len(muted_accounts)},
            "blocked": {"accounts": blocked_accounts, "count": len(blocked_accounts)},
        }

        # Get top posts by engagement
        top_posts = []
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM post_engagement LIMIT 1")
            if cursor.fetchone():
                cursor.execute(
                    """
                    SELECT post_uri, post_text, like_count, repost_count, reply_count, quote_count,
                           bookmark_count, created_at, indirect_likes, indirect_reposts, indirect_replies, indirect_bookmarks
                    FROM post_engagement
                    ORDER BY (like_count + repost_count * 2 + reply_count * 3 + bookmark_count * 2) DESC
                    LIMIT 10
                """
                )
                for row in cursor.fetchall():
                    top_posts.append(
                        {
                            "uri": row[0],
                            "text": row[1],
                            "likes": row[2],
                            "reposts": row[3],
                            "replies": row[4],
                            "quotes": row[5],
                            "bookmarks": row[6],
                            "created_at": row[7],
                            "indirect_likes": row[8] or 0,
                            "indirect_reposts": row[9] or 0,
                            "indirect_replies": row[10] or 0,
                            "indirect_bookmarks": row[11] or 0,
                        }
                    )

        # Prepare data for template
        data = {
            "last_updated": last_updated,
            "stats": stats,
            "unfollowers": unfollowers,
            "non_mutual": non_mutual,
            "followers_only": followers_only,
            "mutual_follows": mutual_follows,
            "hidden_analytics": hidden_analytics,
            "hidden_categories": hidden_categories,
            "change_history": change_history,
            "top_posts": top_posts,
            "advanced_metrics": advanced_metrics,
            "top_interactors": top_interactors,
            "bluesky_handle": Config.BLUESKY_HANDLE,
        }

        # Render template
        html = get_report_html(data)
        return html

    except Exception as e:
        logger.error(f"/report error: {e}")
        import traceback

        error_html = (
            "<h1>Error loading report</h1><p>"
            + str(e)
            + "</p><pre>"
            + traceback.format_exc()
            + "</pre>"
        )
        return error_html, 500


@app.route("/api/hidden-analytics")
def api_hidden_analytics():
    """Hidden follower analytics (blocks, mutes, suspensions)"""
    try:
        days = int(request.args.get("days", Config.WIDGET_DAYS))
        analytics = db.get_hidden_follower_analytics(days=days)
        api_requests.labels(endpoint="/api/hidden-analytics", status="success").inc()

        if not analytics:
            return jsonify({"message": "No data available yet"}), 200

        return jsonify(analytics)
    except Exception as e:
        logger.error(f"/api/hidden-analytics error: {e}")
        api_requests.labels(endpoint="/api/hidden-analytics", status="error").inc()
        return jsonify({"error": "Internal error"}), 500


@app.route("/api/change-history")
def api_change_history():
    """Follower change history with type detection (unfollow vs block)"""
    try:
        days = int(request.args.get("days", Config.WIDGET_DAYS))
        changes = db.get_follower_change_details(days=days)
        api_requests.labels(endpoint="/api/change-history", status="success").inc()
        return jsonify({"changes": changes, "days": days})
    except Exception as e:
        logger.error(f"/api/change-history error: {e}")
        api_requests.labels(endpoint="/api/change-history", status="error").inc()
        return jsonify({"error": "Internal error"}), 500


@app.route("/api/mutual-follows")
def api_mutual_follows():
    """Get mutual follows (people who follow each other)"""
    try:
        mutual = db.get_mutual_follows()
        api_requests.labels(endpoint="/api/mutual-follows", status="success").inc()
        return jsonify({"accounts": mutual, "count": len(mutual)})
    except Exception as e:
        logger.error(f"/api/mutual-follows error: {e}")
        api_requests.labels(endpoint="/api/mutual-follows", status="error").inc()
        return jsonify({"error": "Internal error"}), 500


@app.route("/api/hidden-categories")
def api_hidden_categories():
    """Get detailed breakdown of who is in each hidden category"""
    try:
        muted = db.get_muted_accounts_with_profile()
        blocked = db.get_blocked_accounts_with_profile()

        api_requests.labels(endpoint="/api/hidden-categories", status="success").inc()
        return jsonify(
            {
                "muted": {"accounts": muted, "count": len(muted)},
                "blocked": {"accounts": blocked, "count": len(blocked)},
            }
        )
    except Exception as e:
        logger.error(f"/api/hidden-categories error: {e}")
        api_requests.labels(endpoint="/api/hidden-categories", status="error").inc()
        return jsonify({"error": "Internal error"}), 500


@app.route("/api/advanced-metrics")
def api_advanced_metrics():
    """Get advanced analytics metrics"""
    try:
        metrics = db.get_advanced_metrics()
        api_requests.labels(endpoint="/api/advanced-metrics", status="success").inc()

        if not metrics:
            return jsonify({"message": "No metrics available yet"}), 200

        return jsonify(metrics)
    except Exception as e:
        logger.error(f"/api/advanced-metrics error: {e}")
        api_requests.labels(endpoint="/api/advanced-metrics", status="error").inc()
        return jsonify({"error": "Internal error"}), 500


@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


@app.route("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {"Content-Type": "text/plain; charset=utf-8"}


# Startup

# ======================================================================
# GRAPH API ENDPOINTS
# ======================================================================

# GRAPH API ENDPOINTS


@app.route("/api/graphs/follower-growth")
def api_follower_growth():
    """Follower and following growth over time"""
    try:
        days = int(request.args.get("days", 30))

        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Get daily metrics
            cursor.execute(
                """
                SELECT metric_date, follower_count, following_count
                FROM daily_metrics
                ORDER BY metric_date DESC
                LIMIT ?
            """,
                (days,),
            )

            rows = cursor.fetchall()

            # Reverse to chronological order
            rows = list(reversed(rows))

            data = {
                "dates": [row[0] for row in rows],
                "followers": [row[1] for row in rows],
                "following": [row[2] for row in rows],
            }

        api_requests.labels(
            endpoint="/api/graphs/follower-growth", status="success"
        ).inc()
        return jsonify(data)

    except Exception as e:
        logger.error(f"/api/graphs/follower-growth error: {e}")
        api_requests.labels(
            endpoint="/api/graphs/follower-growth", status="error"
        ).inc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/graphs/net-growth")
def api_net_growth():
    """Net daily follower/following changes"""
    try:
        days = int(request.args.get("days", 30))

        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Calculate net changes from follower_changes table
            cursor.execute(
                """
                SELECT
                    change_date,
                    SUM(CASE WHEN change_type = 'new_follower' THEN 1 ELSE 0 END) -
                    SUM(CASE WHEN change_type = 'unfollower' THEN 1 ELSE 0 END) as net_followers,
                    SUM(CASE WHEN change_type = 'new_following' THEN 1 ELSE 0 END) -
                    SUM(CASE WHEN change_type = 'unfollowing' THEN 1 ELSE 0 END) as net_following
                FROM follower_changes
                WHERE change_date >= date('now', '-' || ? || ' days')
                GROUP BY change_date
                ORDER BY change_date ASC
            """,
                (days,),
            )

            rows = cursor.fetchall()

            data = {
                "dates": [row[0] for row in rows],
                "netFollowers": [row[1] for row in rows],
                "netFollowing": [row[2] for row in rows],
            }

        api_requests.labels(endpoint="/api/graphs/net-growth", status="success").inc()
        return jsonify(data)

    except Exception as e:
        logger.error(f"/api/graphs/net-growth error: {e}")
        api_requests.labels(endpoint="/api/graphs/net-growth", status="error").inc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/graphs/engagement-timeline")
def api_engagement_timeline():
    """Engagement metrics over time (stacked)"""
    try:
        days = int(request.args.get("days", 30))

        with db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    engagement_date,
                    SUM(total_likes) as likes,
                    SUM(total_reposts) as reposts,
                    SUM(total_replies) as replies,
                    SUM(total_quotes) as quotes,
                    SUM(total_bookmarks) as bookmarks
                FROM (
                    SELECT
                        CASE
                            WHEN pe.collection_date = (SELECT MIN(collection_date) FROM post_engagement)
                            THEN DATE(pe.created_at)
                            ELSE pe.collection_date
                        END as engagement_date,
                        pe.like_count + COALESCE(pe.indirect_likes, 0) as total_likes,
                        pe.repost_count + COALESCE(pe.indirect_reposts, 0) as total_reposts,
                        pe.reply_count + COALESCE(pe.indirect_replies, 0) as total_replies,
                        pe.quote_count as total_quotes,
                        pe.bookmark_count + COALESCE(pe.indirect_bookmarks, 0) as total_bookmarks
                    FROM post_engagement pe
                    WHERE pe.created_at IS NOT NULL
                ) subquery
                GROUP BY engagement_date
                ORDER BY engagement_date ASC
                LIMIT ?
            """,
                (days,),
            )
            rows = cursor.fetchall()

            data = {
                "dates": [row[0] for row in rows],
                "likes": [row[1] or 0 for row in rows],
                "reposts": [row[2] or 0 for row in rows],
                "replies": [row[3] or 0 for row in rows],
                "quotes": [row[4] or 0 for row in rows],
                "bookmarks": [row[5] or 0 for row in rows],
            }

        # Convert to cumulative sums
        cumulative_data = {
            "dates": data["dates"],
            "likes": [],
            "reposts": [],
            "replies": [],
            "quotes": [],
            "bookmarks": [],
        }

        for i in range(len(data["dates"])):
            cumulative_data["likes"].append(sum(data["likes"][: i + 1]))
            cumulative_data["reposts"].append(sum(data["reposts"][: i + 1]))
            cumulative_data["replies"].append(sum(data["replies"][: i + 1]))
            cumulative_data["quotes"].append(sum(data["quotes"][: i + 1]))
            cumulative_data["bookmarks"].append(sum(data["bookmarks"][: i + 1]))

        api_requests.labels(
            endpoint="/api/graphs/engagement-timeline", status="success"
        ).inc()
        return jsonify({"daily": data, "cumulative": cumulative_data})

    except Exception as e:
        logger.error(f"/api/graphs/engagement-timeline error: {e}")
        api_requests.labels(
            endpoint="/api/graphs/engagement-timeline", status="error"
        ).inc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/graphs/posting-frequency")
def api_posting_frequency():
    """Posts per day"""
    try:
        days = int(request.args.get("days", 30))

        with db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT DATE(created_at) as post_date, COUNT(*) as post_count
                FROM post_engagement
                WHERE created_at IS NOT NULL
                GROUP BY DATE(created_at)
                ORDER BY collection_date DESC
                LIMIT ?
            """,
                (days,),
            )

            rows = cursor.fetchall()
            rows = list(reversed(rows))

            data = {
                "dates": [row[0] for row in rows],
                "posts": [row[1] for row in rows],
            }

        api_requests.labels(
            endpoint="/api/graphs/posting-frequency", status="success"
        ).inc()
        return jsonify(data)

    except Exception as e:
        logger.error(f"/api/graphs/posting-frequency error: {e}")
        api_requests.labels(
            endpoint="/api/graphs/posting-frequency", status="error"
        ).inc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/graphs/engagement-breakdown")
def api_engagement_breakdown():
    """Total engagement by type (for pie chart)"""
    try:
        days = int(request.args.get("days", 30))

        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Get totals for the time period - aggregate directly from post_engagement
            cursor.execute(
                """
                SELECT
                    SUM(like_count + indirect_likes) as likes,
                    SUM(repost_count + indirect_reposts) as reposts,
                    SUM(reply_count + indirect_replies) as replies,
                    SUM(quote_count) as quotes,
                    SUM(bookmark_count + indirect_bookmarks) as bookmarks
                FROM post_engagement
                WHERE collection_date >= date('now', '-' || ? || ' days')
            """,
                (days,),
            )

            row = cursor.fetchone()

            data = {
                "labels": ["Likes", "Reposts", "Replies", "Quotes", "Bookmarks"],
                "values": [
                    row[0] or 0,
                    row[1] or 0,
                    row[2] or 0,
                    row[3] or 0,
                    row[4] or 0,
                ],
            }

        api_requests.labels(
            endpoint="/api/graphs/engagement-breakdown", status="success"
        ).inc()
        return jsonify(data)

    except Exception as e:
        logger.error(f"/api/graphs/engagement-breakdown error: {e}")
        api_requests.labels(
            endpoint="/api/graphs/engagement-breakdown", status="error"
        ).inc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/graphs/stats-summary")
def api_stats_summary():
    """Summary statistics for time period"""
    try:
        days = int(request.args.get("days", 30))

        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Get metrics for the period
            cursor.execute(
                """
                SELECT
                    COUNT(DISTINCT metric_date) as days_tracked,
                    MAX(follower_count) - MIN(follower_count) as follower_change,
                    AVG(follower_count) as avg_followers
                FROM daily_metrics
                WHERE metric_date >= date('now', '-' || ? || ' days')
            """,
                (days,),
            )

            metrics_row = cursor.fetchone()

            # Get engagement totals - aggregate directly from post_engagement
            cursor.execute(
                """
                SELECT
                    COUNT(DISTINCT post_uri) as total_posts,
                    SUM(like_count + repost_count + reply_count + quote_count + bookmark_count) as total_engagement,
                    SUM(indirect_likes + indirect_reposts + indirect_replies + indirect_bookmarks) as total_indirect
                FROM post_engagement
                WHERE collection_date >= date('now', '-' || ? || ' days')
            """,
                (days,),
            )

            engagement_row = cursor.fetchone()
            total_posts = engagement_row[0] or 0
            total_engagement = (engagement_row[1] or 0) + (engagement_row[2] or 0)
            avg_engagement = (
                round(total_engagement / total_posts, 1) if total_posts > 0 else 0
            )

            data = {
                "daysTracked": metrics_row[0] or 0,
                "followerChange": metrics_row[1] or 0,
                "avgFollowers": int(metrics_row[2] or 0),
                "totalEngagement": total_engagement,
                "avgEngagementPerPost": avg_engagement,
                "totalPosts": total_posts,
            }

        api_requests.labels(
            endpoint="/api/graphs/stats-summary", status="success"
        ).inc()
        return jsonify(data)

    except Exception as e:
        logger.error(f"/api/graphs/stats-summary error: {e}")
        api_requests.labels(endpoint="/api/graphs/stats-summary", status="error").inc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    logger.info("Bluesky Tracker initializing...")

    # Initialize metrics on startup
    try:
        update_metrics()
    except Exception as e:
        logger.warning(f"Could not initialize metrics (database may be empty): {e}")

    # Schedule daily collection at 6 AM
    scheduler.add_job(
        scheduled_collection,
        trigger=CronTrigger(hour=6, minute=0, timezone=Config.TIMEZONE),
        id="daily_collection",
        name="Daily Bluesky collection",
        replace_existing=True,
    )
    scheduler.start()

    logger.info(f"Bluesky Tracker starting on port {Config.PORT}")
    logger.info(f"Tracking: {Config.BLUESKY_HANDLE}")
    logger.info(
        f"Scheduled collection: daily at {Config.COLLECTION_TIME} {Config.TIMEZONE}"
    )

    # Run Flask
    app.run(host="0.0.0.0", port=Config.PORT, threaded=True)
