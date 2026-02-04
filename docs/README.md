# Bluesky Analytics Tracker

**Last Updated:** 2025-12-31
**Status:** Operational (Authenticated Mode)
**Access:** http://10.8.0.1:8095/report (VPN) | http://192.168.129.3:8095/report (LAN)
**Image:** `ghcr.io/costantinoai/bluesky-tracker:latest`
**Auto-Updates:** Watchtower

---

## Quick Links

**📚 Documentation:**
- [[services/bluesky/api-reference|API Reference]] - Complete API endpoint documentation
- [[services/bluesky/configuration|Configuration Guide]] - Setup, authentication, and integration
- [[services/bluesky/troubleshooting|Troubleshooting]] - Common issues and solutions

**🔗 Related Services:**
- [[services/README|Services Overview]] - All Pi services
- [[services/grafana|Grafana & Monitoring]] - Dashboards and metrics
- [[services/uptime-kuma|Uptime Kuma]] - Service monitoring

**🛠️ Operations:**
- [[AGENTS|Agent Instructions]] - Operational playbook
- [[operations/progress-log|Progress Log]] - Change history

---

## Overview

The Bluesky Analytics Tracker is a custom-built Python Flask application that monitors your Bluesky social media account (@costantinoai.bsky.social). It tracks followers, following, unfollowers, post engagement, and hidden follower analytics (muted/blocked accounts). The service collects daily snapshots, detects changes, exposes Prometheus metrics, and provides both API endpoints and a comprehensive HTML report dashboard.

**Key Features:**
- Daily automated data collection at 6:00 AM (Europe/Brussels)
- Tracks follower/following changes with historical trends
- Detects unfollowers and identifies potential blocks vs natural unfollows
- Post engagement analytics with direct + indirect metrics (quote posts)
- Identifies non-mutual follows and followers-only accounts
- Muted and blocked account tracking (authenticated mode)
- Top interactors ranking based on weighted engagement
- Prometheus metrics for Grafana dashboards
- RESTful API for programmatic access
- Beautiful HTML report with all analytics in one view

---

## Service Details

| Property | Value |
|----------|-------|
| Container | `bluesky-tracker` |
| Image | `ghcr.io/costantinoai/bluesky-tracker:latest` |
| Source Repo | https://github.com/costantinoai/bluesky-tracker |
| Auto-Updates | Watchtower (daily check) |
| Network Mode | Bridge (connected to `homepage_default` and `monitoring_monitoring`) |
| Port | 8095 (exposed to LAN/VPN) |
| Data Directory | `/home/costantino_ai/docker/bluesky-tracker/data/` |
| Database | SQLite (`bluesky.db`) |
| Health Check | Healthy (curl localhost:8095/health every 30s) |
| Tracked Account | costantinoai.bsky.social |
| Collection Schedule | Daily at 6:00 AM Europe/Brussels |
| Run As User | `appuser` (UID 1000, non-root) |

---

## Docker Compose Configuration

```yaml
# /home/costantino_ai/docker/bluesky-tracker/docker-compose.yml
services:
  bluesky-tracker:
    image: ghcr.io/costantinoai/bluesky-tracker:latest
    container_name: bluesky-tracker
    hostname: bluesky-tracker
    restart: unless-stopped

    # Security hardening
    security_opt:
      - no-new-privileges:true

    ports:
      - "8095:8095"

    volumes:
      - ./data:/app/data

    env_file:
      - .env

    networks:
      - homepage_default         # For Homepage widget access
      - monitoring_monitoring    # For Prometheus metrics scraping

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8095/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

    # Resource limits
    mem_limit: 256m
    mem_reservation: 128m
    pids_limit: 50

    # Logging
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

networks:
  homepage_default:
    external: true
  monitoring_monitoring:
    external: true
```

**Deployment Workflow:**
1. Develop locally in `~/OneDrive.../GitHub/bluesky-tracker`
2. Push to GitHub → CI builds multi-arch image → publishes to GHCR
3. Watchtower auto-updates the Pi container (or manual: `docker compose pull && docker compose up -d`)

---

## Security Configuration

### Docker Security Hardening

| Security Feature | Status | Details |
|------------------|--------|---------|
| **no-new-privileges** | ✅ Enabled | Prevents privilege escalation |
| **Non-root user** | ✅ Enabled | Runs as `appuser` (UID 1000) |
| **Read-only root filesystem** | ❌ Not enabled | Application writes to `/app/data` volume |
| **Capability drop** | ❌ Not configured | No capabilities dropped (default Flask app) |
| **Memory limit** | ✅ 256MB | With 128MB reservation |
| **PID limit** | ✅ 50 processes | Prevents fork bombs |
| **Logging limits** | ✅ Configured | 10MB max size, 3 files rotation |

```bash
# Verify security configuration
ssh pi "docker inspect bluesky-tracker | jq '.[0].HostConfig | {SecurityOpt, Memory, PidsLimit}'"
```

**Security Assessment:** The container runs with moderate security hardening. The `no-new-privileges` flag is enabled and it runs as a non-root user. Consider adding `cap_drop: ALL` in future updates as the Flask application doesn't require special capabilities.

### Network Security

| Access Level | Source | Firewall Rules |
|--------------|--------|----------------|
| **VPN Clients** | 10.8.0.2, 10.8.0.3 | Allowed via UFW VPN rules |
| **Laptop (LAN)** | 192.168.129.8 | Allowed via UFW laptop rule |
| **Other LAN devices** | 192.168.128.0/23 | ❌ Blocked (no UFW rule for port 8095) |
| **Internet** | 0.0.0.0/0 | ❌ Blocked (default deny) |
| **Prometheus** | 172.20.0.9 (Docker bridge) | ✅ Allowed (same Docker network) |
| **Homepage** | 172.20.0.0/16 (Docker bridge) | ✅ Allowed (same Docker network) |

**Note:** Port 8095 is NOT explicitly allowed in UFW for general LAN access. Access is granted implicitly through the laptop's IP whitelist (192.168.129.8) which has full host access.

---

## Authentication Modes

The Bluesky Tracker supports two modes of operation:

### 1. Public API Mode (No Authentication)

**When:** No `BLUESKY_APP_PASSWORD` is set in `.env`

**Capabilities:**
- ✅ Follower/following counts
- ✅ Basic follower lists (visible accounts only)
- ✅ Unfollower detection
- ✅ Non-mutual follow analysis
- ❌ Post engagement metrics (likes, reposts, replies)
- ❌ Muted/blocked account tracking
- ❌ Hidden follower analytics
- ❌ Interaction rankings

**API Used:** `https://public.api.bsky.app` (Bluesky's public cached API)

**Privacy:** Your main Bluesky password is NEVER used or stored.

### 2. Authenticated Mode (App Password) ⭐ **CURRENT MODE**

**When:** `BLUESKY_APP_PASSWORD` is set in `.env`

**Capabilities:**
- ✅ All public API features
- ✅ Post engagement metrics (direct + indirect)
- ✅ Muted account tracking
- ✅ Blocked account tracking
- ✅ Hidden follower detection (accounts that blocked you)
- ✅ Top interactors ranking
- ✅ Full interaction history from notifications
- ✅ Accurate counts (bypasses privacy settings)

**API Used:** `https://bsky.social` (Bluesky's authenticated API)

**Current Configuration:**
```bash
BLUESKY_HANDLE=costantinoai.bsky.social
BLUESKY_APP_PASSWORD=7huh-mrhf-hcyq-oelo  # App password (not main password)
```

**Security Notes:**
- App passwords are generated at: https://bsky.app/settings/app-passwords
- They can be revoked anytime without affecting your main account password
- More secure than using your main password
- The password is stored in `.env` with 600 permissions (owner read/write only)
- NEVER logged in application logs (sanitized in error messages)

---

## API Endpoints

All endpoints return JSON unless specified otherwise.

### Core Analytics Endpoints

| Endpoint | Method | Purpose | Response Time |
|----------|--------|---------|---------------|
| `/api/stats` | GET | Summary statistics for Homepage widget | <100ms |
| `/api/unfollowers?days=30` | GET | List of recent unfollowers | <200ms |
| `/api/non-mutual` | GET | People you follow who don't follow back | <150ms |
| `/api/followers-only` | GET | People who follow you but you don't follow back | <150ms |
| `/api/mutual-follows` | GET | Mutual followers (follow each other) | <200ms |

### Advanced Analytics Endpoints (Authenticated Only)

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/api/hidden-analytics?days=30` | GET | Blocked/muted/suspended follower analytics | ✅ Yes |
| `/api/change-history?days=30` | GET | Follower changes with type detection | ✅ Yes |
| `/api/hidden-categories` | GET | Detailed muted/blocked account lists | ✅ Yes |
| `/api/advanced-metrics` | GET | Engagement metrics, post analytics | ✅ Yes |

### Utility Endpoints

| Endpoint | Method | Purpose | Notes |
|----------|--------|---------|-------|
| `/health` | GET | Health check | Returns `{"status": "ok", "timestamp": "..."}` |
| `/metrics` | GET | Prometheus metrics | Scraped every 30s by Prometheus |
| `/report` | GET | Full HTML analytics report | Beautiful UI with all data |
| `/api/collect` | POST | Trigger manual collection | Runs data collection immediately |

### Example API Calls

```bash
# Get summary stats (used by Homepage widget)
curl -s http://10.8.0.1:8095/api/stats
# Response: {"follower_count":96,"following_count":188,"unfollowers_30d":0,"non_mutual_following":110,"followers_only":18}

# Get recent unfollowers (last 7 days)
curl -s http://10.8.0.1:8095/api/unfollowers?days=7 | jq

# Get advanced engagement metrics
curl -s http://10.8.0.1:8095/api/advanced-metrics | jq
# Response: {"avg_likes":1.91,"avg_replies":0.88,"avg_reposts":0.35,"engagement_rate":3.5,"post_count":34,...}

# Manually trigger data collection
curl -X POST http://10.8.0.1:8095/api/collect
```

---

## Prometheus Metrics

The `/metrics` endpoint exposes the following Prometheus-compatible metrics:

### Bluesky-Specific Metrics

```promql
# Follower/Following Counts
bluesky_follower_count          # Current follower count
bluesky_following_count         # Current following count

# Change Metrics
bluesky_unfollowers_30d         # Unfollowers in last 30 days
bluesky_non_mutual_following    # People you follow who don't follow back
bluesky_followers_only          # People who follow you but you don't follow back

# API Performance
bluesky_api_requests_total{endpoint="/api/stats",status="success"}
bluesky_api_requests_total{endpoint="/api/stats",status="error"}

# Collection Job Performance
bluesky_collection_duration_seconds_bucket
bluesky_collection_duration_seconds_count
bluesky_collection_duration_seconds_sum
```

### Prometheus Configuration

```yaml
# /home/costantino_ai/docker/monitoring/prometheus/prometheus.yml
scrape_configs:
  - job_name: "bluesky"
    static_configs:
      - targets: ["bluesky-tracker:8095"]
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: "bluesky-tracker"
```

**Scrape Interval:** 30 seconds (Prometheus global default)

**Access Metrics Directly:**
```bash
# View current metrics
ssh pi "curl -s http://localhost:8095/metrics | grep bluesky"

# Check Prometheus is scraping
ssh pi "curl -s http://localhost:9091/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job==\"bluesky\")'"
```

---

## Homepage Integration

The Bluesky Tracker appears on the Homepage dashboard with a custom API widget.

### Homepage Configuration

```yaml
# /home/costantino_ai/docker/homepage/config/services.yaml
- Bluesky Tracker:
    href: http://10.8.0.1:8095/report
    description: Follower Analytics
    icon: mdi-butterfly
    container: bluesky-tracker
    server: local-docker
    widget:
      type: customapi
      url: http://bluesky-tracker:8095/api/stats
      refreshInterval: 300000  # 5 minutes
      mappings:
      - field: follower_count
        label: Followers
        format: number
      - field: following_count
        label: Following
        format: number
      - field: unfollowers_30d
        label: Unfollowed (30d)
        format: number
```

**Widget Display:**
- **Followers:** Current count (96)
- **Following:** Current count (188)
- **Unfollowed (30d):** Number of unfollowers in last 30 days

**Refresh Rate:** Every 5 minutes (300,000ms)

---

## Uptime Kuma Monitoring

**Status:** ✅ **MONITORED**

| Setting | Value |
|---------|-------|
| **Monitor ID** | 36 |
| **Monitor Type** | HTTP(s) |
| **Friendly Name** | Bluesky Tracker |
| **URL** | http://127.0.0.1:8095/health |
| **Heartbeat Interval** | 60 seconds |
| **Retries** | 2 |
| **Expected Status Code** | 200 |
| **Notification** | homelab-alerts (default) |

**View in Uptime Kuma:** http://10.8.0.1:3001

---

## Grafana Dashboards

**Status:** ❌ **NO DASHBOARD CONFIGURED**

No Grafana dashboard currently exists for Bluesky metrics, although Prometheus is actively scraping metrics from the `/metrics` endpoint.

### Recommended Dashboard Panels

Create a new Grafana dashboard with these panels:

**1. Follower Growth**
```promql
# Query
bluesky_follower_count

# Panel type: Time series
# Title: Follower Count Over Time
```

**2. Unfollower Rate**
```promql
# Query
bluesky_unfollowers_30d

# Panel type: Stat
# Title: Unfollowers (30 days)
```

**3. Following/Follower Ratio**
```promql
# Query
bluesky_following_count / bluesky_follower_count

# Panel type: Gauge
# Title: Following/Follower Ratio
# Thresholds: <0.5 (green), 0.5-2.0 (yellow), >2.0 (red)
```

**4. Non-Mutual Follows**
```promql
# Query
bluesky_non_mutual_following

# Panel type: Stat
# Title: Non-Mutual Follows
```

**5. API Request Rate**
```promql
# Query
rate(bluesky_api_requests_total[5m])

# Panel type: Time series
# Title: API Requests/sec
# Group by: endpoint, status
```

**6. Collection Job Duration**
```promql
# Query
histogram_quantile(0.95, rate(bluesky_collection_duration_seconds_bucket[5m]))

# Panel type: Stat
# Title: Collection Duration (p95)
# Unit: seconds
```

---

## Database Schema

The service uses SQLite with the following tables:

### Core Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `followers_snapshot` | Daily snapshots of followers | collection_date, did, handle, display_name |
| `following_snapshot` | Daily snapshots of following | collection_date, did, handle, display_name |
| `follower_changes` | Detected changes (new/unfollow) | change_date, change_type, did, handle |
| `daily_metrics` | Aggregated daily counts | metric_date, follower_count, unfollower_count |
| `collection_log` | Collection job history | run_date, status, duration_seconds |

### Authenticated Mode Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `post_engagement` | Post metrics (likes, reposts, etc.) | post_uri, like_count, repost_count, indirect_likes |
| `daily_counts` | Profile vs API counts | profile_followers, api_followers, hidden_followers |
| `muted_snapshot` | Accounts you muted | collection_date, did, handle |
| `blocked_snapshot` | Accounts you blocked | collection_date, did, handle |
| `hidden_accounts_identified` | Accounts that blocked you | did, handle, identified_date |
| `interactions` | User interaction rankings | did, likes, replies, reposts, score |

### Database Location

```
/home/costantino_ai/docker/bluesky-tracker/data/
├── bluesky.db          # SQLite database (96 snapshots collected)
└── bluesky.db-wal      # Write-ahead log (if active)
```

### Direct Database Queries

```bash
# Check collection history
ssh pi "sqlite3 ~/docker/bluesky-tracker/data/bluesky.db 'SELECT run_date, status, followers_collected, following_collected, duration_seconds FROM collection_log ORDER BY run_date DESC LIMIT 10;'"

# Count total snapshots
ssh pi "sqlite3 ~/docker/bluesky-tracker/data/bluesky.db 'SELECT COUNT(*) FROM followers_snapshot;'"

# Get recent unfollowers
ssh pi "sqlite3 ~/docker/bluesky-tracker/data/bluesky.db \"SELECT change_date, handle FROM follower_changes WHERE change_type='unfollower' ORDER BY change_date DESC LIMIT 10;\""

# Check post engagement (top posts)
ssh pi "sqlite3 ~/docker/bluesky-tracker/data/bluesky.db 'SELECT post_text, like_count, repost_count FROM post_engagement ORDER BY like_count DESC LIMIT 5;'"
```

---

## Data Collection Schedule

### Automated Daily Collection

**Schedule:** Every day at **6:00 AM Europe/Brussels** (CET/CEST)

**Scheduler:** APScheduler with CronTrigger
```python
scheduler.add_job(
    scheduled_collection,
    trigger=CronTrigger(hour=6, minute=0, timezone='Europe/Brussels'),
    id='daily_collection',
    name='Daily Bluesky collection'
)
```

**Collection Process:**
1. Authenticate with Bluesky API (if app password configured)
2. Fetch profile counts (includes hidden followers)
3. Fetch visible followers list
4. Fetch following list
5. Fetch muted accounts (authenticated mode)
6. Fetch blocked accounts (authenticated mode)
7. Fetch post engagement data (authenticated mode)
8. Fetch interaction data from notifications (authenticated mode)
9. Save all data to database
10. Detect changes since last collection
11. Update Prometheus metrics
12. Log collection result

**Average Duration:** ~8-27 seconds (depending on follower count and auth mode)

**Recent Collections:**
```
2025-12-29 16:29:54 | success | 96 followers | 187 following | 26.57s
2025-12-29 16:22:50 | success | 96 followers | 187 following | 26.64s
2025-12-29 16:17:02 | success | 96 followers | 187 following | 26.54s
2025-12-29 15:57:42 | success | 96 followers | 187 following | 8.08s
```

### Manual Collection

Trigger data collection manually via API:

```bash
# Trigger collection immediately
curl -X POST http://10.8.0.1:8095/api/collect

# Response (success):
{"success": true, "message": "Data collected successfully"}

# Monitor logs during collection
ssh pi "docker logs -f bluesky-tracker"
```

**Use Cases:**
- Testing after configuration changes
- Immediate update after major follower changes
- Debugging collection issues

---

## Access Methods

### Web Interfaces

| Interface | URL (VPN) | URL (LAN) | Purpose |
|-----------|-----------|-----------|---------|
| **HTML Report** | http://10.8.0.1:8095/report | http://192.168.129.3:8095/report | Full analytics dashboard |
| **Health Check** | http://10.8.0.1:8095/health | http://192.168.129.3:8095/health | Service status |
| **Prometheus Metrics** | http://10.8.0.1:8095/metrics | http://192.168.129.3:8095/metrics | Raw metrics |

### API Access

**From VPN:**
```bash
curl http://10.8.0.1:8095/api/stats
```

**From LAN (laptop only):**
```bash
curl http://192.168.129.3:8095/api/stats
```

**From Docker containers (same network):**
```bash
# From Homepage widget
curl http://bluesky-tracker:8095/api/stats

# From Prometheus scraper
curl http://bluesky-tracker:8095/metrics
```

### SSH Access to Pi

```bash
# View logs
ssh pi "docker logs bluesky-tracker --tail 100 -f"

# Check container status
ssh pi "docker ps | grep bluesky-tracker"

# Access database
ssh pi "sqlite3 ~/docker/bluesky-tracker/data/bluesky.db"

# View application code
ssh pi "cat ~/docker/bluesky-tracker/app.py"
```

---

## HTML Report Features

The `/report` endpoint provides a comprehensive analytics dashboard:

### Report Sections

| Section | Content | Authenticated Only |
|---------|---------|-------------------|
| **Summary Stats** | Follower/following counts, 30-day changes | No |
| **Unfollowers** | List with handles, display names, dates | No |
| **Non-Mutual Follows** | People you follow who don't follow back | No |
| **Followers Only** | People who follow you but you don't follow back | No |
| **Mutual Follows** | Two-way connections | No |
| **Hidden Analytics** | Muted/blocked/suspected blocks breakdown | ✅ Yes |
| **Change History** | Timeline of follower changes | ✅ Yes |
| **Top Posts** | Engagement-ranked posts with metrics | ✅ Yes |
| **Advanced Metrics** | Avg likes/replies, engagement rate | ✅ Yes |
| **Top Interactors** | Most engaged followers (weighted score) | ✅ Yes |
| **Muted Accounts** | Full list with profiles | ✅ Yes |
| **Blocked Accounts** | Full list with profiles | ✅ Yes |

**Authentication Indicator:** The report shows whether authenticated mode is active based on whether engagement data is available.

**Last Updated:** Displays timestamp of last successful collection.

---

## Application Architecture

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Language** | Python | 3.11.14 |
| **Web Framework** | Flask | Latest |
| **WSGI Server** | Gunicorn | 2 workers, 60s timeout |
| **Database** | SQLite | 3.x |
| **Scheduler** | APScheduler | CronTrigger |
| **Metrics** | prometheus_client | Latest |
| **HTTP Client** | requests | Latest |
| **Timezone** | pytz | Latest |

### Application Modules

```
/app/
├── app.py           # Flask application, routes, scheduler (13.5 KB)
├── collector.py     # Bluesky API client, data collection (21.2 KB)
├── database.py      # SQLite database operations (36.5 KB)
├── config.py        # Configuration settings (1.4 KB)
├── templates.py     # HTML report generation (44.7 KB)
└── data/
    └── bluesky.db   # SQLite database
```

### Container Image

The container image is built automatically via GitHub Actions CI/CD and published to GitHub Container Registry (GHCR).

**Image:** `ghcr.io/costantinoai/bluesky-tracker:latest`

**Supported Platforms:**
- `linux/amd64` (x86_64)
- `linux/arm64` (Raspberry Pi 4, Apple Silicon)
- `linux/arm/v7` (Raspberry Pi 3)

**Manual Update:**
```bash
ssh pi "cd ~/docker/bluesky-tracker && docker compose pull && docker compose up -d"
```

**Source Repository:** https://github.com/costantinoai/bluesky-tracker

---

## Configuration Files

### Environment Variables (.env)

```bash
# /home/costantino_ai/docker/bluesky-tracker/.env (chmod 600)

# Bluesky account to track (handle WITHOUT @ symbol)
BLUESKY_HANDLE=costantinoai.bsky.social

# App Password for authenticated access (OPTIONAL)
# Generate at: https://bsky.app/settings/app-passwords
# Leave empty for public API mode
BLUESKY_APP_PASSWORD=7huh-mrhf-hcyq-oelo
```

**File Permissions:**
```bash
ssh pi "ls -la ~/docker/bluesky-tracker/.env"
# Output: -rw------- 1 costantino_ai costantino_ai 375 Dec 29 13:01 .env
```

### Config Module (config.py)

```python
class Config:
    BLUESKY_HANDLE = os.getenv('BLUESKY_HANDLE', 'costantinoai.bsky.social')
    BLUESKY_APP_PASSWORD = os.getenv('BLUESKY_APP_PASSWORD', '').strip()
    HAS_AUTH = bool(BLUESKY_APP_PASSWORD)

    # API endpoints
    BLUESKY_API_URL = 'https://public.api.bsky.app'       # Public cached API
    BLUESKY_AUTH_API_URL = 'https://bsky.social'          # Authenticated API
    REQUEST_DELAY = 0.7  # Seconds between API calls

    # Collection schedule
    COLLECTION_TIME = '06:00'
    TIMEZONE = 'Europe/Brussels'

    # Flask server
    PORT = 8095

    # Widget display
    WIDGET_DAYS = 30  # Default lookback period
```

---

## Maintenance Commands

### Container Management

```bash
# Check container status
ssh pi "docker ps | grep bluesky-tracker"

# View real-time logs
ssh pi "docker logs -f bluesky-tracker"

# View recent logs
ssh pi "docker logs bluesky-tracker --tail 100"

# Restart container
ssh pi "cd ~/docker/bluesky-tracker && docker compose restart"

# Pull latest image and restart (after pushing to GitHub)
ssh pi "cd ~/docker/bluesky-tracker && docker compose pull && docker compose up -d"

# Stop container
ssh pi "cd ~/docker/bluesky-tracker && docker compose down"

# Check resource usage
ssh pi "docker stats bluesky-tracker --no-stream"
```

### Database Maintenance

```bash
# Backup database
ssh pi "cp ~/docker/bluesky-tracker/data/bluesky.db ~/docker/bluesky-tracker/data/bluesky.db.backup-$(date +%Y%m%d)"

# Check database size
ssh pi "du -h ~/docker/bluesky-tracker/data/bluesky.db"

# Vacuum database (reclaim space)
ssh pi "sqlite3 ~/docker/bluesky-tracker/data/bluesky.db 'VACUUM;'"

# Check integrity
ssh pi "sqlite3 ~/docker/bluesky-tracker/data/bluesky.db 'PRAGMA integrity_check;'"

# Get table sizes
ssh pi "sqlite3 ~/docker/bluesky-tracker/data/bluesky.db \"SELECT name, COUNT(*) FROM (SELECT 'followers_snapshot' as name UNION SELECT 'following_snapshot' UNION SELECT 'follower_changes' UNION SELECT 'post_engagement') t JOIN sqlite_master ON 1=1 GROUP BY name;\""
```

### Configuration Changes

```bash
# Edit environment variables
ssh pi "nano ~/docker/bluesky-tracker/.env"

# Verify file permissions (must be 600)
ssh pi "chmod 600 ~/docker/bluesky-tracker/.env"

# View current config (without exposing password)
ssh pi "grep -v PASSWORD ~/docker/bluesky-tracker/.env"

# Restart after config change
ssh pi "cd ~/docker/bluesky-tracker && docker compose restart"
```

### Manual Data Collection

```bash
# Trigger collection via API
curl -X POST http://10.8.0.1:8095/api/collect

# Watch collection in real-time
ssh pi "docker logs -f bluesky-tracker | grep -E 'collection|Collected|Authentication'"
```

---

## Troubleshooting

### Collection Failures

**Problem:** Collection job fails with authentication errors

**Solution:**
```bash
# Check if app password is set
ssh pi "grep BLUESKY_APP_PASSWORD ~/docker/bluesky-tracker/.env | sed 's/=.*$/=****/'"

# Regenerate app password at https://bsky.app/settings/app-passwords
# Update .env file
ssh pi "nano ~/docker/bluesky-tracker/.env"

# Restart container
ssh pi "cd ~/docker/bluesky-tracker && docker compose restart"

# Check logs for authentication success
ssh pi "docker logs bluesky-tracker --tail 50 | grep -i auth"
```

**Problem:** Collection takes too long or times out

**Diagnosis:**
```bash
# Check recent collection durations
ssh pi "sqlite3 ~/docker/bluesky-tracker/data/bluesky.db 'SELECT run_date, duration_seconds FROM collection_log ORDER BY run_date DESC LIMIT 10;'"

# Check network connectivity
ssh pi "docker exec bluesky-tracker curl -s -o /dev/null -w '%{time_total}\n' https://bsky.social"
```

**Solution:** Increase Gunicorn timeout in Dockerfile:
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8095", "--workers", "2", "--timeout", "120", ...]
```

### API Endpoint Not Responding

**Problem:** API returns 500 errors or timeouts

**Diagnosis:**
```bash
# Check container health
ssh pi "docker inspect bluesky-tracker | jq '.[0].State.Health'"

# Check application logs
ssh pi "docker logs bluesky-tracker --tail 100 | grep -i error"

# Test health endpoint
curl -v http://10.8.0.1:8095/health

# Check database accessibility
ssh pi "docker exec bluesky-tracker ls -la /app/data/"
```

**Solutions:**
1. Restart container: `ssh pi "cd ~/docker/bluesky-tracker && docker compose restart"`
2. Check database permissions: Data directory must be writable by appuser (UID 1000)
3. Verify network connectivity: Container must be on `homepage_default` and `monitoring_monitoring` networks

### Metrics Not Appearing in Prometheus

**Problem:** Prometheus not scraping Bluesky metrics

**Diagnosis:**
```bash
# Check Prometheus targets
ssh pi "curl -s http://localhost:9091/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job==\"bluesky\")'"

# Test metrics endpoint directly
ssh pi "curl -s http://bluesky-tracker:8095/metrics | grep bluesky_follower_count"

# Check Prometheus config
ssh pi "cat ~/docker/monitoring/prometheus/prometheus.yml | grep -A5 bluesky"
```

**Solutions:**
1. Verify container is on `monitoring_monitoring` network
2. Restart Prometheus: `ssh pi "cd ~/docker/monitoring && docker compose restart prometheus"`
3. Reload Prometheus config: `ssh pi "curl -X POST http://localhost:9091/-/reload"`

### Homepage Widget Not Updating

**Problem:** Widget shows stale data or errors

**Diagnosis:**
```bash
# Test API endpoint from Homepage container
ssh pi "docker exec homepage curl -s http://bluesky-tracker:8095/api/stats"

# Check Homepage logs
ssh pi "docker logs homepage --tail 50 | grep -i bluesky"
```

**Solutions:**
1. Verify container is on `homepage_default` network
2. Check API response is valid JSON: `curl -s http://bluesky-tracker:8095/api/stats | jq`
3. Restart Homepage: `ssh pi "cd ~/docker/homepage && docker compose restart"`
4. Clear Homepage cache (if applicable)

### Database Locked Errors

**Problem:** `database is locked` errors in logs

**Diagnosis:**
```bash
# Check for WAL mode
ssh pi "sqlite3 ~/docker/bluesky-tracker/data/bluesky.db 'PRAGMA journal_mode;'"

# Check for long-running transactions
ssh pi "lsof ~/docker/bluesky-tracker/data/bluesky.db" 2>/dev/null || ssh pi "docker exec bluesky-tracker lsof /app/data/bluesky.db"
```

**Solutions:**
1. Ensure WAL mode is enabled: `ssh pi "sqlite3 ~/docker/bluesky-tracker/data/bluesky.db 'PRAGMA journal_mode=WAL;'"`
2. Restart container to clear locks: `ssh pi "cd ~/docker/bluesky-tracker && docker compose restart"`
3. If persistent, check disk I/O performance

---

## Performance Metrics

### Current Statistics (as of 2025-12-29)

| Metric | Value |
|--------|-------|
| **Followers** | 96 |
| **Following** | 188 |
| **Unfollowers (30d)** | 0 |
| **Non-Mutual Following** | 110 |
| **Followers Only** | 18 |
| **Total Snapshots** | 96 |
| **Average Collection Time** | ~26 seconds (authenticated) |
| **Post Count Tracked** | 34 |
| **Average Likes per Post** | 1.91 |
| **Average Replies per Post** | 0.88 |
| **Engagement Rate** | 3.5% |

### Resource Usage

| Resource | Current | Limit | Percentage |
|----------|---------|-------|------------|
| **Memory** | ~43 MB | 256 MB | 16.8% |
| **CPU** | <1% | N/A | Minimal |
| **Disk (container)** | ~150 KB | N/A | Negligible |
| **Disk (database)** | ~150 KB | N/A | Growing slowly |
| **PIDs** | 5-7 | 50 | <14% |

```bash
# Check real-time resource usage
ssh pi "docker stats bluesky-tracker --no-stream"
```

---

## Future Enhancements

### Planned Features

- [ ] Add Uptime Kuma monitor for health checks
- [ ] Create Grafana dashboard for visualizing metrics over time
- [ ] Add `cap_drop: ALL` to Docker security configuration
- [ ] Implement read-only root filesystem with tmpfs for `/tmp`
- [ ] Add explicit UFW rule for port 8095 (currently relies on laptop whitelist)
- [ ] Email/ntfy alerts for significant follower changes (e.g., >5 unfollowers in one day)
- [ ] Export to CSV functionality for historical data analysis
- [ ] Integration with ntfy for daily summary notifications
- [ ] Follower growth rate predictions using linear regression
- [ ] Sentiment analysis of interactions (requires NLP library)

### Security Hardening Opportunities

```yaml
# Recommended additions to docker-compose.yml
cap_drop:
  - ALL
read_only: true
tmpfs:
  - /tmp
  - /app/.local  # For Python bytecode cache
```

---

## Documentation Index

### Bluesky Tracker Documentation
- **[[services/bluesky/README|This Document]]** - Complete service overview and reference
- **[[services/bluesky/api-reference|API Reference]]** - All API endpoints, parameters, responses, examples
- **[[services/bluesky/configuration|Configuration Guide]]** - Setup, authentication, Docker, integrations
- **[[services/bluesky/troubleshooting|Troubleshooting]]** - Common issues, diagnostics, solutions

### Related Documentation
- [[services/README|Services Overview]] - Complete service inventory
- [[services/grafana|Grafana & Monitoring]] - Metrics and dashboards
- [[services/uptime-kuma|Uptime Kuma]] - Service monitoring and API
- [[reference/docker-vpn-proxy-pattern|Docker VPN Proxy Pattern]] - Network architecture
- [[security/status|Security Status]] - Security hardening reference
- [[AGENTS|Agent Instructions]] - Operational playbook
- [[operations/progress-log|Progress Log]] - Change history

---

## External Links

- **Bluesky App Passwords:** https://bsky.app/settings/app-passwords
- **Bluesky API Documentation:** https://docs.bsky.app/
- **AT Protocol Specs:** https://atproto.com/specs/atp
- **Flask Documentation:** https://flask.palletsprojects.com/
- **Prometheus Client Python:** https://github.com/prometheus/client_python
- **Gunicorn Documentation:** https://docs.gunicorn.org/

---

*Last updated: 2025-12-31*
*Service deployed: 2025-12-29 (migrated to GHCR: 2025-12-31)*
*Documentation by: Claude Code*
