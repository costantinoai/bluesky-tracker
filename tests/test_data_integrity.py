"""
Data integrity tests for the CAR parsing and transformation pipeline.

These tests verify that:
1. CAR data is parsed correctly with all required fields
2. Data transformation preserves integrity (no NULL unique keys)
3. Deduplication works correctly (no duplicate rows)
4. Engagement counts are accurate (excluding self-replies)

These tests would have caught the bug where:
- post_uri was NULL (missing cid from _process_posts)
- Self-replies were counted as engagement
- Duplicate posts inflated counts by 11x
"""

import pytest
import os
import sys
import tempfile
from datetime import datetime, date
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Database
from car_utils import CARClient

# Import from fixtures (relative to tests directory)
from tests.fixtures.mock_car_data import (
    get_mock_car_records,
    get_mock_processed_car_data,
    TEST_USER_DID,
    OTHER_USER_DIDS,
    EXPECTED_COUNTS,
)


class TestCARParsing:
    """Test CAR file parsing produces correct output format"""

    def test_process_posts_includes_cid(self):
        """Ensure _process_posts includes CID for uniqueness - THIS WOULD CATCH THE BUG"""
        client = CARClient()
        records = get_mock_car_records().get('app.bsky.feed.post', [])

        posts = client._process_posts(records)

        assert len(posts) == EXPECTED_COUNTS['total_posts']

        for post in posts:
            assert 'cid' in post, "Posts must include CID for deduplication"
            assert post['cid'] is not None, "CID must not be None"
            assert post['cid'] != "", "CID must not be empty string"

    def test_process_posts_reply_detection(self):
        """Ensure replies are correctly detected"""
        client = CARClient()
        records = get_mock_car_records().get('app.bsky.feed.post', [])

        posts = client._process_posts(records)

        replies = [p for p in posts if p['is_reply']]
        originals = [p for p in posts if not p['is_reply']]

        # Expected: 3 original + 2 thread + 4 replies to others = 9 total
        # 6 are replies (2 thread + 4 to others), 3 are originals
        assert len(replies) == 6, f"Expected 6 replies, got {len(replies)}"
        assert len(originals) == 3, f"Expected 3 originals, got {len(originals)}"

        # All replies must have reply_to info
        for reply in replies:
            assert reply['reply_to'] is not None, "Reply must have reply_to info"

    def test_process_likes_includes_author_did(self):
        """Ensure likes include the author DID from URI"""
        client = CARClient()
        records = get_mock_car_records().get('app.bsky.feed.like', [])

        likes = client._process_likes(records)

        assert len(likes) == EXPECTED_COUNTS['likes']

        for like in likes:
            assert 'subject_uri' in like
            assert 'author_did' in like
            # Author DID should be extracted from URI
            if like['subject_uri'].startswith('at://'):
                assert like['author_did'] is not None

    def test_process_reposts_structure(self):
        """Ensure reposts have correct structure"""
        client = CARClient()
        records = get_mock_car_records().get('app.bsky.feed.repost', [])

        reposts = client._process_reposts(records)

        assert len(reposts) == EXPECTED_COUNTS['reposts']

        for repost in reposts:
            assert 'subject_uri' in repost
            assert 'created_at_str' in repost


class TestDataTransformation:
    """Test data transformation from CAR to database format"""

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

    def test_posts_saved_with_valid_uri(self, test_db):
        """Ensure posts are saved with non-NULL post_uri - THIS WOULD CATCH THE BUG"""
        mock_data = get_mock_processed_car_data()

        # Transform posts data as collector.run_backfill() does
        posts_data = []
        for post in mock_data['posts']:
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

        # Save posts
        test_db.save_posts_from_car(posts_data)

        # Verify no NULL post_uri values
        with test_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM posts_full WHERE post_uri IS NULL")
            null_count = cursor.fetchone()[0]

            assert null_count == 0, f"Found {null_count} posts with NULL post_uri - deduplication will fail!"

    def test_no_duplicate_posts_after_multiple_saves(self, test_db):
        """Ensure saving posts multiple times doesn't create duplicates - THIS WOULD CATCH THE BUG"""
        mock_data = get_mock_processed_car_data()

        # Transform posts data
        posts_data = []
        for post in mock_data['posts']:
            reply_to = post.get("reply_to")
            reply_uri = None
            if reply_to and isinstance(reply_to, dict):
                parent = reply_to.get("parent", {})
                if isinstance(parent, dict):
                    reply_uri = parent.get("uri")

            posts_data.append({
                "post_uri": post.get("cid"),
                "text": post.get("text", ""),
                "post_created_at": post.get("created_at_str"),
                "is_reply": post.get("is_reply", False),
                "reply_to_uri": reply_uri,
                "has_embed": post.get("has_embed", False),
                "langs": ",".join(post.get("langs", [])) if post.get("langs") else None,
            })

        # Save posts TWICE (simulating multiple collection runs)
        test_db.save_posts_from_car(posts_data)
        test_db.save_posts_from_car(posts_data)
        test_db.save_posts_from_car(posts_data)

        # Verify no duplicates
        with test_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM posts_full")
            total = cursor.fetchone()[0]

            # Should be exactly the number of unique posts, not 3x
            assert total == EXPECTED_COUNTS['total_posts'], \
                f"Expected {EXPECTED_COUNTS['total_posts']} unique posts, got {total} (duplicates exist!)"

    def test_likes_saved_correctly(self, test_db):
        """Ensure likes are saved with correct structure"""
        mock_data = get_mock_processed_car_data()

        # Transform likes data as collector does
        likes_data = []
        for like in mock_data['likes']:
            subject_uri = like.get("subject_uri", "")
            author_did = like.get("author_did")

            likes_data.append({
                "liked_post_uri": subject_uri,
                "liked_author_did": author_did,
                "liked_at": like.get("created_at_str"),
                "rkey": None,
            })

        test_db.save_likes_given(likes_data)

        with test_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM likes_given")
            count = cursor.fetchone()[0]

            assert count == EXPECTED_COUNTS['likes']


class TestEngagementBalance:
    """Test engagement balance calculations"""

    @pytest.fixture
    def db_with_test_data(self):
        """Create DB with known test data"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        db = Database(db_path=db_path)

        mock_data = get_mock_processed_car_data()

        # Save posts
        posts_data = []
        for post in mock_data['posts']:
            reply_to = post.get("reply_to")
            reply_uri = None
            if reply_to and isinstance(reply_to, dict):
                parent = reply_to.get("parent", {})
                if isinstance(parent, dict):
                    reply_uri = parent.get("uri")

            posts_data.append({
                "post_uri": post.get("cid"),
                "text": post.get("text", ""),
                "post_created_at": post.get("created_at_str"),
                "is_reply": post.get("is_reply", False),
                "reply_to_uri": reply_uri,
                "has_embed": post.get("has_embed", False),
                "langs": ",".join(post.get("langs", [])) if post.get("langs") else None,
            })
        db.save_posts_from_car(posts_data)

        # Save likes
        likes_data = []
        for like in mock_data['likes']:
            likes_data.append({
                "liked_post_uri": like.get("subject_uri", ""),
                "liked_author_did": like.get("author_did"),
                "liked_at": like.get("created_at_str"),
                "rkey": None,
            })
        db.save_likes_given(likes_data)

        # Save reposts
        reposts_data = []
        for repost in mock_data['reposts']:
            reposts_data.append({
                "reposted_uri": repost.get("subject_uri", ""),
                "reposted_author_did": repost.get("author_did"),
                "reposted_at": repost.get("created_at_str"),
                "rkey": None,
            })
        db.save_reposts_given(reposts_data)

        yield db

        try:
            os.unlink(db_path)
        except:
            pass

    def test_replies_excludes_self_replies(self, db_with_test_data):
        """Ensure self-replies (threads) are NOT counted as engagement - THIS WOULD CATCH THE BUG"""
        db = db_with_test_data

        # Get engagement balance, passing the user's DID
        balance = db.get_engagement_balance(user_did=TEST_USER_DID)

        # Should be 4 (replies to others), NOT 6 (all replies including self-replies)
        assert balance['given']['replies'] == EXPECTED_COUNTS['replies_to_others'], \
            f"Expected {EXPECTED_COUNTS['replies_to_others']} replies to others, " \
            f"got {balance['given']['replies']} (self-replies may be included!)"

    def test_likes_count_correct(self, db_with_test_data):
        """Ensure likes count is accurate"""
        db = db_with_test_data
        balance = db.get_engagement_balance(user_did=TEST_USER_DID)

        assert balance['given']['likes'] == EXPECTED_COUNTS['likes']

    def test_reposts_count_correct(self, db_with_test_data):
        """Ensure reposts count is accurate"""
        db = db_with_test_data
        balance = db.get_engagement_balance(user_did=TEST_USER_DID)

        assert balance['given']['reposts'] == EXPECTED_COUNTS['reposts']

    def test_total_engagement_correct(self, db_with_test_data):
        """Ensure total engagement calculation is correct"""
        db = db_with_test_data
        balance = db.get_engagement_balance(user_did=TEST_USER_DID)

        expected_total = (
            EXPECTED_COUNTS['likes'] +
            EXPECTED_COUNTS['reposts'] +
            EXPECTED_COUNTS['replies_to_others']
        )

        assert balance['given']['total'] == expected_total, \
            f"Expected total {expected_total}, got {balance['given']['total']}"


class TestDatabaseCleanup:
    """Test database cleanup functionality"""

    @pytest.fixture
    def db_with_duplicates(self):
        """Create DB with intentional duplicates"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        db = Database(db_path=db_path)

        # Manually insert duplicate posts (simulating the bug)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            for i in range(5):  # Insert same post 5 times
                cursor.execute("""
                    INSERT INTO posts_full
                    (post_uri, text, post_created_at, is_reply, reply_to_uri)
                    VALUES (NULL, 'Duplicate post', '2024-01-15T12:00:00Z', 0, NULL)
                """)
            conn.commit()

        yield db

        try:
            os.unlink(db_path)
        except:
            pass

    def test_cleanup_removes_duplicates(self, db_with_duplicates):
        """Ensure cleanup removes duplicate posts"""
        db = db_with_duplicates

        # Verify we have duplicates before cleanup
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM posts_full")
            before = cursor.fetchone()[0]
            assert before == 5, "Should have 5 duplicate rows before cleanup"

        # Run cleanup
        result = db.cleanup_duplicate_posts()

        assert result['total_before'] == 5
        assert result['total_after'] == 1
        assert result['duplicates_removed'] == 4

        # Verify only 1 row remains
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM posts_full")
            after = cursor.fetchone()[0]
            assert after == 1
