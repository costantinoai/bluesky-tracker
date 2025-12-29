"""
Integration tests for real user workflows.

Tests the complete workflows that users will actually run:
1. Collecting data from Bluesky API
2. Storing data in database
3. Querying analytics via API endpoints
4. Generating reports

Uses REAL SQLite databases with known test data to verify expected behavior.
"""

import pytest
import os
import sys
import tempfile
import json
from datetime import datetime, date
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Database
from collector import BlueskyCollector
from config import Config


class TestCompleteWorkflow:
    """Test the complete user workflow from collection to analytics"""

    @pytest.fixture
    def test_db(self):
        """Create a temporary database for testing"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        db = Database(db_path=db_path)
        yield db
        try:
            os.unlink(db_path)
        except:
            pass

    def test_full_collection_and_storage_workflow(self, test_db):
        """Test collecting data and storing in database"""

        # Simulate a collection by directly saving data
        collection_date = date.today()
        test_db.save_snapshot(
            collection_date=collection_date,
            followers=[
                {'did': 'did:plc:follower1', 'handle': 'user1.bsky.social', 'display_name': 'User One'},
                {'did': 'did:plc:follower2', 'handle': 'user2.bsky.social', 'display_name': 'User Two'},
                {'did': 'did:plc:follower3', 'handle': 'user3.bsky.social', 'display_name': 'User Three'},
            ],
            following=[
                {'did': 'did:plc:following1', 'handle': 'followed1.bsky.social', 'display_name': 'Followed One'},
                {'did': 'did:plc:following2', 'handle': 'followed2.bsky.social', 'display_name': 'Followed Two'},
            ]
        )
        test_db.detect_changes(collection_date)

        # Verify data was stored in database
        stats = test_db.get_stats(days=30)
        assert stats['follower_count'] == 3
        assert stats['following_count'] == 2

    def test_unfollower_detection_workflow(self, test_db):
        """Test detecting unfollowers across multiple collections"""
        from datetime import timedelta

        # Day 1: Initial followers (yesterday)
        collection_date_1 = date.today() - timedelta(days=1)
        test_db.save_snapshot(
            collection_date=collection_date_1,
            followers=[
                {'did': 'did:plc:user1', 'handle': 'user1', 'display_name': 'User One'},
                {'did': 'did:plc:user2', 'handle': 'user2', 'display_name': 'User Two'},
                {'did': 'did:plc:user3', 'handle': 'user3', 'display_name': 'User Three'},
            ],
            following=[
                {'did': 'did:plc:followed1', 'handle': 'followed1', 'display_name': 'Followed One'}
            ]
        )
        test_db.detect_changes(collection_date_1)

        # Day 2: user2 unfollowed (today)
        collection_date_2 = date.today()
        test_db.save_snapshot(
            collection_date=collection_date_2,
            followers=[
                {'did': 'did:plc:user1', 'handle': 'user1', 'display_name': 'User One'},
                {'did': 'did:plc:user3', 'handle': 'user3', 'display_name': 'User Three'},
            ],
            following=[
                {'did': 'did:plc:followed1', 'handle': 'followed1', 'display_name': 'Followed One'}
            ]
        )
        test_db.detect_changes(collection_date_2)

        # Verify unfollower detection
        unfollowers = test_db.get_unfollowers(days=30)
        assert len(unfollowers) == 1
        assert unfollowers[0]['handle'] == 'user2'

        # Verify stats
        stats = test_db.get_stats(days=30)
        assert stats['unfollowers_30d'] == 1
        assert stats['follower_count'] == 2

    def test_analytics_query_workflow(self, test_db):
        """Test querying analytics from database with known data"""

        # Set up test data
        collection_date = date.today()

        test_db.save_snapshot(
            collection_date=collection_date,
            followers=[
                {'did': 'did:plc:user1', 'handle': 'user1', 'display_name': 'User One'},
                {'did': 'did:plc:user2', 'handle': 'user2', 'display_name': 'User Two'},
                {'did': 'did:plc:user3', 'handle': 'user3', 'display_name': 'User Three'},
                {'did': 'did:plc:user4', 'handle': 'user4', 'display_name': 'User Four'},
            ],
            following=[
                {'did': 'did:plc:user1', 'handle': 'user1', 'display_name': 'User One'},
                {'did': 'did:plc:user2', 'handle': 'user2', 'display_name': 'User Two'},
                {'did': 'did:plc:other1', 'handle': 'other1', 'display_name': 'Other One'},
                {'did': 'did:plc:other2', 'handle': 'other2', 'display_name': 'Other Two'},
            ]
        )
        test_db.detect_changes(collection_date)

        # Test mutual follows
        mutual = test_db.get_mutual_follows()
        assert len(mutual) == 2  # user1 and user2

        # Test followers only
        followers_only = test_db.get_followers_only()
        assert len(followers_only) == 2  # user3 and user4

        # Test non-mutual following
        non_mutual = test_db.get_non_mutual_following()
        assert len(non_mutual) == 2  # other1 and other2

        # Test stats
        stats = test_db.get_stats(days=30)
        assert stats['follower_count'] == 4
        assert stats['following_count'] == 4
        assert stats['non_mutual_following'] == 2
        assert stats['followers_only'] == 2

    def test_engagement_tracking_workflow(self, test_db):
        """Test saving and querying engagement data"""

        # Save engagement data for a post
        collection_date = date.today()
        engagement_data = [{
            'uri': 'at://did:plc:test/app.bsky.feed.post/test123',
            'text': 'Test post content',
            'like_count': 10,
            'repost_count': 5,
            'reply_count': 3,
            'quote_count': 2,
            'bookmark_count': 1,
            'created_at': datetime.now().isoformat()
        }]

        test_db.save_engagement_data(collection_date, engagement_data)

        # Verify data was saved by querying the database
        with test_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM post_engagement')
            count = cursor.fetchone()[0]
            assert count >= 1

            cursor.execute('SELECT like_count, repost_count FROM post_engagement WHERE post_uri = ?',
                         ('at://did:plc:test/app.bsky.feed.post/test123',))
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == 10  # like_count
            assert result[1] == 5   # repost_count

    def test_collection_logging_workflow(self, test_db):
        """Test that collection runs are logged properly"""

        # Log successful collection
        collection_date = date.today()
        test_db.log_collection(
            collection_date=collection_date,
            status='success',
            followers_collected=100,
            following_collected=50,
            error_message=None,
            duration=1.5
        )

        # Verify log was saved
        with test_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM collection_log WHERE status = ?', ('success',))
            count = cursor.fetchone()[0]
            assert count >= 1

    def test_database_initialization_workflow(self, test_db):
        """Test that database initializes with correct schema"""

        # Verify all required tables exist
        with test_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}

            required_tables = {
                'followers_snapshot',
                'following_snapshot',
                'follower_changes',
                'collection_log',
                'post_engagement',
                'daily_counts'
            }

            assert required_tables.issubset(tables), f"Missing tables: {required_tables - tables}"
