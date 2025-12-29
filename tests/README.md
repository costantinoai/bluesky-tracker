# Test Suite

This test suite focuses on **real user workflows** using **real SQLite databases** to ensure the application works as expected in production.

## Philosophy

**We test REAL workflows, not mocks.**

The tests use temporary SQLite databases with known test data to verify that:
- Data is stored correctly
- Analytics queries return expected results
- The complete user workflow works end-to-end

We avoid excessive mocking because:
- Mocks don't catch real integration issues
- Over-mocked tests give false confidence
- Real database tests catch schema issues, SQL errors, and data integrity problems

## What We Test

### 1. Collection & Storage Workflow (`test_full_collection_and_storage_workflow`)
**What it does:** Simulates collecting follower/following data from Bluesky and storing it in the database.

**Coverage:**
- Saving follower snapshots
- Saving following snapshots
- Database schema correctness
- Data retrieval via `get_stats()`

**Why it matters:** This is the core workflow users run daily via the scheduler.

---

### 2. Unfollower Detection (`test_unfollower_detection_workflow`)
**What it does:** Simulates two collection runs across different days to verify unfollower detection.

**Coverage:**
- Detecting who unfollowed between runs
- Change tracking (`detect_changes()`)
- Querying unfollowers by date range
- Stats aggregation for unfollowers

**Why it matters:** Users need accurate unfollower tracking to understand follower churn.

---

### 3. Analytics Queries (`test_analytics_query_workflow`)
**What it does:** Saves known test data and verifies analytics queries return correct results.

**Coverage:**
- Mutual follows (people who follow you back)
- Followers only (people who follow you but you don't follow)
- Non-mutual following (people you follow who don't follow back)
- Stats calculations

**Why it matters:** These are the primary analytics endpoints users query.

---

### 4. Engagement Tracking (`test_engagement_tracking_workflow`)
**What it does:** Saves post engagement data and verifies it's stored correctly.

**Coverage:**
- Saving engagement data (likes, reposts, replies, quotes, bookmarks)
- Querying engagement data from database
- Data integrity checks

**Why it matters:** Users track post performance over time.

---

### 5. Collection Logging (`test_collection_logging_workflow`)
**What it does:** Verifies that collection runs are logged properly.

**Coverage:**
- Logging successful collections
- Storing metadata (follower count, following count, duration)
- Querying collection history

**Why it matters:** Users need to know when data was last collected and troubleshoot failures.

---

### 6. Database Initialization (`test_database_initialization_workflow`)
**What it does:** Verifies the database creates all required tables on initialization.

**Coverage:**
- Schema validation
- Table existence checks
- Database structure

**Why it matters:** Ensures the database initializes correctly on first run.

---

## What We DON'T Test

We intentionally **do not** test:

### Flask API Endpoints
**Why not:** Testing Flask endpoints properly would create a "mock pyramid" problem.

Each endpoint depends on multiple components:
- Flask app initialization
- Database connections
- Config validation
- Scheduler (needs to be mocked to not start)
- Prometheus metrics registry (needs cleanup between tests)
- Environment variables (need to be set before import)

**The problem with mocking all of this:**
```python
# This is what we'd need to do for EACH test:
@patch('app.scheduler.start')
@patch('app.Database')
@patch('app.db.get_stats')
@patch('app.db.get_unfollowers')
@patch('app.db.get_connection')
# ... 10 more patches ...
def test_stats_endpoint(mock1, mock2, mock3, ...):
    mock_db.get_stats.return_value = {'follower_count': 100}
    # This test now verifies mocks, not real behavior!
```

**What this tests:** Whether our mocks are configured correctly.
**What this doesn't test:** Whether the actual database methods work.

**What we do instead:**
- Our database tests use **REAL SQLite databases** with known data
- They test the actual `get_stats()`, `get_unfollowers()`, etc. methods
- These are what the Flask endpoints call, so if those work, the endpoints work

**Bottom line:** The Flask endpoints are thin wrappers around database methods. Testing the database methods with real data is more valuable than testing Flask routing with mocked data.

If you want to test the endpoints, consider **integration tests** with a real Flask app + real database (similar to our current database tests).

---

### Configuration Validation
**Why not:** Simple conditional logic that doesn't involve complex workflows.

The config validation just checks:
- Is `BLUESKY_HANDLE` set?
- Is `BLUESKY_APP_PASSWORD` set?

This is 5 lines of if-statements. Not worth the test overhead.

---

### Bluesky API Calls
**Why not:** We can't control external API responses.

To test Bluesky API calls, we'd need to:
1. Mock HTTP responses (not testing real behavior)
2. Use VCR cassettes (breaks when API changes)
3. Hit the real API (slow, requires credentials, rate limits)

None of these are practical for CI/CD.

---

### Scheduler Behavior
**Why not:** Time-based testing is complex and not critical for data integrity.

Testing the scheduler would require:
- Mocking time/dates
- Waiting for scheduled tasks
- Verifying APScheduler behavior (well-tested library)

The scheduler just calls our collector at 6 AM. If the collector works (which we test), the scheduler works.

---

**Could we add these tests later?** Yes, but they add complexity without proportional value. The current tests cover the critical data workflows that users depend on.

## Running Tests

### Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test
```bash
pytest tests/test_workflows.py::TestCompleteWorkflow::test_unfollower_detection_workflow -v
```

### Run with Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

## Test Output

### Expected Output
```
============================= test session starts ==============================
collected 6 items

tests/test_workflows.py::TestCompleteWorkflow::test_full_collection_and_storage_workflow PASSED [ 16%]
tests/test_workflows.py::TestCompleteWorkflow::test_unfollower_detection_workflow PASSED [ 33%]
tests/test_workflows.py::TestCompleteWorkflow::test_analytics_query_workflow PASSED [ 50%]
tests/test_workflows.py::TestCompleteWorkflow::test_engagement_tracking_workflow PASSED [ 66%]
tests/test_workflows.py::TestCompleteWorkflow::test_collection_logging_workflow PASSED [ 83%]
tests/test_workflows.py::TestCompleteWorkflow::test_database_initialization_workflow PASSED [100%]

======================== 6 passed, 42 warnings in 2.21s ========================
```

### About the Warnings (Now Silenced!)

~~You used to see **42 warnings** like this:~~
```
DeprecationWarning: The default date adapter is deprecated as of Python 3.12;
see the sqlite3 documentation for suggested replacement recipes
```

**What this means:**
- Python 3.12 deprecated the default way SQLite handles `date` and `datetime` objects
- Our code uses the old (but still working) method
- This is **not critical** - the code works perfectly fine

**What we did:**
- Created `pytest.ini` to silence these specific warnings
- The warnings are now suppressed during test runs
- The code still works exactly the same

**Why we haven't fixed the underlying issue:**
- The old method still works in Python 3.12 and will for the foreseeable future
- Fixing it requires rewriting all date handling in `database.py`
- The warnings don't affect functionality
- It's a deprecation notice, not a breaking change

**For a long-term fix:**
- Update `database.py` to use timezone-aware datetime objects per Python 3.12 recommendations
- See: https://docs.python.org/3/library/sqlite3.html#default-adapters-and-converters-deprecated

## Test Coverage Summary

| Component | Coverage | Notes |
|-----------|----------|-------|
| **Database Operations** | ✅ High | All core methods tested with real DB |
| **Data Collection** | ✅ High | End-to-end workflow tested |
| **Analytics Queries** | ✅ High | All user-facing queries tested |
| **Change Detection** | ✅ High | Unfollower/follower tracking tested |
| **Collection Logging** | ✅ Medium | Basic logging tested |
| **API Endpoints** | ❌ Not covered | Would require excessive mocking |
| **Configuration** | ❌ Not covered | Simple validation logic |
| **Bluesky API** | ❌ Not covered | External dependency |

## Adding New Tests

When adding tests, follow these principles:

1. **Test real workflows** - Simulate what users actually do
2. **Use real databases** - Create temporary SQLite files
3. **Use known test data** - Define exact input and expected output
4. **Avoid excessive mocking** - Only mock external APIs (Bluesky)
5. **Clean up after yourself** - Delete temporary files in fixtures

### Example Test Structure
```python
def test_new_workflow(self, test_db):
    """Test description"""

    # 1. Set up known test data
    test_db.save_snapshot(...)

    # 2. Run the workflow
    result = test_db.some_method(...)

    # 3. Assert expected results
    assert result['expected_field'] == expected_value
```

## CI/CD Integration

These tests run automatically in GitHub Actions on every commit:

- `.github/workflows/test.yml` runs the full test suite
- Tests must pass before Docker images are built
- Coverage reports are uploaded to Codecov (optional)

## Troubleshooting

### Tests failing locally but passing in CI
- Check your Python version (tests are run on 3.11 and 3.12)
- Ensure you're using a fresh virtual environment
- Delete `.pytest_cache/` and `__pycache__/` directories

### Database locked errors
- Make sure no other process is using the test database
- The test cleanup happens automatically - don't interrupt tests

### Import errors
- Verify `requirements-dev.txt` is installed
- Check that you're running pytest from the repository root

---

**Last updated:** 2025-12-30
**Test count:** 6 passing
**Execution time:** ~2 seconds
