"""
Mock CAR data fixtures for testing.

Provides realistic test data that matches the structure returned by
car_utils.py after parsing a CAR file. This allows testing the full
data transformation pipeline without needing network access or real CAR files.

Test User DID: did:plc:testuser000
"""

from datetime import datetime, timedelta

# Test user's DID (the account being tracked)
TEST_USER_DID = "did:plc:testuser000"

# Other users' DIDs (for interactions)
OTHER_USER_DIDS = [
    "did:plc:otheruser001",
    "did:plc:otheruser002",
    "did:plc:otheruser003",
    "did:plc:otheruser004",
    "did:plc:otheruser005",
]


def get_mock_car_records():
    """
    Returns mock records as they would appear from car_utils.parse_car().

    Structure matches: { collection_type: [{ cid, value }, ...] }
    """
    base_time = datetime(2024, 1, 15, 12, 0, 0)

    return {
        "app.bsky.feed.post": [
            # Original posts (3)
            {
                "cid": "bafyreig_original_post_1",
                "value": {
                    "$type": "app.bsky.feed.post",
                    "text": "This is my first original post for testing",
                    "createdAt": (base_time + timedelta(hours=1)).isoformat() + "Z",
                    "langs": ["en"],
                }
            },
            {
                "cid": "bafyreig_original_post_2",
                "value": {
                    "$type": "app.bsky.feed.post",
                    "text": "Second original post with some content",
                    "createdAt": (base_time + timedelta(hours=2)).isoformat() + "Z",
                    "langs": ["en"],
                    "embed": {"$type": "app.bsky.embed.images"}
                }
            },
            {
                "cid": "bafyreig_original_post_3",
                "value": {
                    "$type": "app.bsky.feed.post",
                    "text": "Third original post here",
                    "createdAt": (base_time + timedelta(hours=3)).isoformat() + "Z",
                }
            },
            # Thread posts - replies to SELF (2) - should NOT count as engagement
            {
                "cid": "bafyreig_thread_post_1",
                "value": {
                    "$type": "app.bsky.feed.post",
                    "text": "Continuing my own thread here",
                    "createdAt": (base_time + timedelta(hours=4)).isoformat() + "Z",
                    "reply": {
                        "root": {
                            "uri": f"at://{TEST_USER_DID}/app.bsky.feed.post/root123",
                            "cid": "bafyreig_original_post_1"
                        },
                        "parent": {
                            "uri": f"at://{TEST_USER_DID}/app.bsky.feed.post/parent123",
                            "cid": "bafyreig_original_post_1"
                        }
                    }
                }
            },
            {
                "cid": "bafyreig_thread_post_2",
                "value": {
                    "$type": "app.bsky.feed.post",
                    "text": "Another part of my thread",
                    "createdAt": (base_time + timedelta(hours=5)).isoformat() + "Z",
                    "reply": {
                        "root": {
                            "uri": f"at://{TEST_USER_DID}/app.bsky.feed.post/root123",
                            "cid": "bafyreig_original_post_1"
                        },
                        "parent": {
                            "uri": f"at://{TEST_USER_DID}/app.bsky.feed.post/thread1",
                            "cid": "bafyreig_thread_post_1"
                        }
                    }
                }
            },
            # Actual replies to OTHER users (4) - SHOULD count as engagement
            {
                "cid": "bafyreig_reply_to_other_1",
                "value": {
                    "$type": "app.bsky.feed.post",
                    "text": "Great post! I totally agree.",
                    "createdAt": (base_time + timedelta(hours=6)).isoformat() + "Z",
                    "reply": {
                        "root": {
                            "uri": f"at://{OTHER_USER_DIDS[0]}/app.bsky.feed.post/their123",
                            "cid": "bafyreig_their_post_1"
                        },
                        "parent": {
                            "uri": f"at://{OTHER_USER_DIDS[0]}/app.bsky.feed.post/their123",
                            "cid": "bafyreig_their_post_1"
                        }
                    }
                }
            },
            {
                "cid": "bafyreig_reply_to_other_2",
                "value": {
                    "$type": "app.bsky.feed.post",
                    "text": "Interesting perspective!",
                    "createdAt": (base_time + timedelta(hours=7)).isoformat() + "Z",
                    "reply": {
                        "root": {
                            "uri": f"at://{OTHER_USER_DIDS[1]}/app.bsky.feed.post/post456",
                            "cid": "bafyreig_their_post_2"
                        },
                        "parent": {
                            "uri": f"at://{OTHER_USER_DIDS[1]}/app.bsky.feed.post/post456",
                            "cid": "bafyreig_their_post_2"
                        }
                    }
                }
            },
            {
                "cid": "bafyreig_reply_to_other_3",
                "value": {
                    "$type": "app.bsky.feed.post",
                    "text": "Thanks for sharing this.",
                    "createdAt": (base_time + timedelta(hours=8)).isoformat() + "Z",
                    "reply": {
                        "root": {
                            "uri": f"at://{OTHER_USER_DIDS[2]}/app.bsky.feed.post/post789",
                            "cid": "bafyreig_their_post_3"
                        },
                        "parent": {
                            "uri": f"at://{OTHER_USER_DIDS[2]}/app.bsky.feed.post/post789",
                            "cid": "bafyreig_their_post_3"
                        }
                    }
                }
            },
            {
                "cid": "bafyreig_reply_to_other_4",
                "value": {
                    "$type": "app.bsky.feed.post",
                    "text": "I have a question about this.",
                    "createdAt": (base_time + timedelta(hours=9)).isoformat() + "Z",
                    "reply": {
                        "root": {
                            "uri": f"at://{OTHER_USER_DIDS[3]}/app.bsky.feed.post/postabc",
                            "cid": "bafyreig_their_post_4"
                        },
                        "parent": {
                            "uri": f"at://{OTHER_USER_DIDS[3]}/app.bsky.feed.post/postabc",
                            "cid": "bafyreig_their_post_4"
                        }
                    }
                }
            },
        ],
        "app.bsky.feed.like": [
            # 7 likes to other users' posts
            {
                "cid": "bafyreig_like_1",
                "value": {
                    "$type": "app.bsky.feed.like",
                    "subject": {
                        "uri": f"at://{OTHER_USER_DIDS[0]}/app.bsky.feed.post/liked1",
                        "cid": "bafyreig_liked_post_1"
                    },
                    "createdAt": (base_time + timedelta(hours=1)).isoformat() + "Z"
                }
            },
            {
                "cid": "bafyreig_like_2",
                "value": {
                    "$type": "app.bsky.feed.like",
                    "subject": {
                        "uri": f"at://{OTHER_USER_DIDS[1]}/app.bsky.feed.post/liked2",
                        "cid": "bafyreig_liked_post_2"
                    },
                    "createdAt": (base_time + timedelta(hours=2)).isoformat() + "Z"
                }
            },
            {
                "cid": "bafyreig_like_3",
                "value": {
                    "$type": "app.bsky.feed.like",
                    "subject": {
                        "uri": f"at://{OTHER_USER_DIDS[2]}/app.bsky.feed.post/liked3",
                        "cid": "bafyreig_liked_post_3"
                    },
                    "createdAt": (base_time + timedelta(hours=3)).isoformat() + "Z"
                }
            },
            {
                "cid": "bafyreig_like_4",
                "value": {
                    "$type": "app.bsky.feed.like",
                    "subject": {
                        "uri": f"at://{OTHER_USER_DIDS[0]}/app.bsky.feed.post/liked4",
                        "cid": "bafyreig_liked_post_4"
                    },
                    "createdAt": (base_time + timedelta(hours=4)).isoformat() + "Z"
                }
            },
            {
                "cid": "bafyreig_like_5",
                "value": {
                    "$type": "app.bsky.feed.like",
                    "subject": {
                        "uri": f"at://{OTHER_USER_DIDS[1]}/app.bsky.feed.post/liked5",
                        "cid": "bafyreig_liked_post_5"
                    },
                    "createdAt": (base_time + timedelta(hours=5)).isoformat() + "Z"
                }
            },
            {
                "cid": "bafyreig_like_6",
                "value": {
                    "$type": "app.bsky.feed.like",
                    "subject": {
                        "uri": f"at://{OTHER_USER_DIDS[3]}/app.bsky.feed.post/liked6",
                        "cid": "bafyreig_liked_post_6"
                    },
                    "createdAt": (base_time + timedelta(hours=6)).isoformat() + "Z"
                }
            },
            {
                "cid": "bafyreig_like_7",
                "value": {
                    "$type": "app.bsky.feed.like",
                    "subject": {
                        "uri": f"at://{OTHER_USER_DIDS[4]}/app.bsky.feed.post/liked7",
                        "cid": "bafyreig_liked_post_7"
                    },
                    "createdAt": (base_time + timedelta(hours=7)).isoformat() + "Z"
                }
            },
        ],
        "app.bsky.feed.repost": [
            # 3 reposts
            {
                "cid": "bafyreig_repost_1",
                "value": {
                    "$type": "app.bsky.feed.repost",
                    "subject": {
                        "uri": f"at://{OTHER_USER_DIDS[0]}/app.bsky.feed.post/reposted1",
                        "cid": "bafyreig_reposted_post_1"
                    },
                    "createdAt": (base_time + timedelta(hours=2)).isoformat() + "Z"
                }
            },
            {
                "cid": "bafyreig_repost_2",
                "value": {
                    "$type": "app.bsky.feed.repost",
                    "subject": {
                        "uri": f"at://{OTHER_USER_DIDS[1]}/app.bsky.feed.post/reposted2",
                        "cid": "bafyreig_reposted_post_2"
                    },
                    "createdAt": (base_time + timedelta(hours=4)).isoformat() + "Z"
                }
            },
            {
                "cid": "bafyreig_repost_3",
                "value": {
                    "$type": "app.bsky.feed.repost",
                    "subject": {
                        "uri": f"at://{OTHER_USER_DIDS[2]}/app.bsky.feed.post/reposted3",
                        "cid": "bafyreig_reposted_post_3"
                    },
                    "createdAt": (base_time + timedelta(hours=6)).isoformat() + "Z"
                }
            },
        ],
        "app.bsky.graph.follow": [
            # 5 follows
            {
                "cid": "bafyreig_follow_1",
                "value": {
                    "$type": "app.bsky.graph.follow",
                    "subject": OTHER_USER_DIDS[0],
                    "createdAt": (base_time - timedelta(days=30)).isoformat() + "Z"
                }
            },
            {
                "cid": "bafyreig_follow_2",
                "value": {
                    "$type": "app.bsky.graph.follow",
                    "subject": OTHER_USER_DIDS[1],
                    "createdAt": (base_time - timedelta(days=20)).isoformat() + "Z"
                }
            },
            {
                "cid": "bafyreig_follow_3",
                "value": {
                    "$type": "app.bsky.graph.follow",
                    "subject": OTHER_USER_DIDS[2],
                    "createdAt": (base_time - timedelta(days=10)).isoformat() + "Z"
                }
            },
            {
                "cid": "bafyreig_follow_4",
                "value": {
                    "$type": "app.bsky.graph.follow",
                    "subject": OTHER_USER_DIDS[3],
                    "createdAt": (base_time - timedelta(days=5)).isoformat() + "Z"
                }
            },
            {
                "cid": "bafyreig_follow_5",
                "value": {
                    "$type": "app.bsky.graph.follow",
                    "subject": OTHER_USER_DIDS[4],
                    "createdAt": (base_time - timedelta(days=1)).isoformat() + "Z"
                }
            },
        ],
        "app.bsky.graph.block": [
            # 1 block
            {
                "cid": "bafyreig_block_1",
                "value": {
                    "$type": "app.bsky.graph.block",
                    "subject": "did:plc:blockeduser001",
                    "createdAt": (base_time - timedelta(days=15)).isoformat() + "Z"
                }
            },
        ],
    }


def get_mock_processed_car_data():
    """
    Returns mock data as it would appear from car_utils.get_all_data().

    This is the processed format that collector.py receives.
    """
    records = get_mock_car_records()

    # Process posts (simulating _process_posts)
    posts = []
    for record in records.get("app.bsky.feed.post", []):
        value = record["value"]
        reply_info = value.get("reply")
        posts.append({
            "cid": record.get("cid"),
            "text": value.get("text", ""),
            "created_at_str": value.get("createdAt"),
            "is_reply": reply_info is not None,
            "reply_to": reply_info,
            "has_embed": value.get("embed") is not None,
            "langs": value.get("langs"),
        })

    # Process likes (simulating _process_likes)
    likes = []
    for record in records.get("app.bsky.feed.like", []):
        value = record["value"]
        subject = value.get("subject", {})
        uri = subject.get("uri", "")
        author_did = None
        if uri.startswith("at://"):
            parts = uri.split("/")
            if len(parts) >= 3:
                author_did = parts[2]
        likes.append({
            "subject_uri": uri,
            "subject_cid": subject.get("cid"),
            "author_did": author_did,
            "created_at_str": value.get("createdAt"),
        })

    # Process reposts (simulating _process_reposts)
    reposts = []
    for record in records.get("app.bsky.feed.repost", []):
        value = record["value"]
        subject = value.get("subject", {})
        uri = subject.get("uri", "")
        author_did = None
        if uri.startswith("at://"):
            parts = uri.split("/")
            if len(parts) >= 3:
                author_did = parts[2]
        reposts.append({
            "subject_uri": uri,
            "subject_cid": subject.get("cid"),
            "author_did": author_did,
            "created_at_str": value.get("createdAt"),
        })

    # Process follows
    follows = []
    for record in records.get("app.bsky.graph.follow", []):
        value = record["value"]
        follows.append({
            "subject_did": value.get("subject"),
            "did": value.get("subject"),
            "created_at_str": value.get("createdAt"),
        })

    # Process blocks
    blocks = []
    for record in records.get("app.bsky.graph.block", []):
        value = record["value"]
        blocks.append({
            "subject_did": value.get("subject"),
            "did": value.get("subject"),
            "created_at_str": value.get("createdAt"),
        })

    return {
        "did": TEST_USER_DID,
        "car_size_bytes": 12345,
        "posts": posts,
        "likes": likes,
        "reposts": reposts,
        "follows": follows,
        "blocks": blocks,
    }


# Expected values for assertions
EXPECTED_COUNTS = {
    "total_posts": 9,
    "original_posts": 3,
    "thread_posts": 2,  # Self-replies (should NOT count as engagement)
    "replies_to_others": 4,  # SHOULD count as engagement
    "likes": 7,
    "reposts": 3,
    "follows": 5,
    "blocks": 1,
}
