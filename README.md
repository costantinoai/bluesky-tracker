# Bluesky Analytics Tracker

Track your Bluesky follower growth, engagement metrics, and network analytics over time.

[![Tests](https://github.com/costantinoai/bluesky-tracker/actions/workflows/test.yml/badge.svg)](https://github.com/costantinoai/bluesky-tracker/actions/workflows/test.yml)
[![Docker Build](https://github.com/costantinoai/bluesky-tracker/actions/workflows/docker-build.yml/badge.svg)](https://github.com/costantinoai/bluesky-tracker/actions/workflows/docker-build.yml)
[![License](https://img.shields.io/github/license/costantinoai/bluesky-tracker)](LICENSE)

---

## Quick Start

```bash
curl -sSL https://raw.githubusercontent.com/costantinoai/bluesky-tracker/main/setup.sh | bash
```

The installer will:
- Check Docker installation
- Download configuration files
- Guide you through setup (handle + app password)
- Start the tracker

**Access dashboard:** http://localhost:8095/report

---

## Screenshots

<details open>
<summary><b>Dashboard Overview</b></summary>

![Dashboard Overview](.github/screenshots/dashboard-overview.png)
*Main dashboard showing follower/following counts, mutual follows, unfollowers, and key metrics*
</details>

<details>
<summary><b>Historical Analytics & Engagement Timeline</b></summary>

![Analytics Timeline](.github/screenshots/analytics-timeline.png)
*Track engagement trends over time with interactive charts for likes, reposts, replies, quotes, and bookmarks*
</details>

<details>
<summary><b>Top Posts by Engagement</b></summary>

![Top Posts](.github/screenshots/top-posts.png)
*View your most popular posts with full text, engagement metrics, and clickable links to Bluesky*
</details>

<details>
<summary><b>Unfollowers & Hidden Accounts</b></summary>

![Unfollowers & Hidden](.github/screenshots/unfollowers-hidden.png)
*Track who unfollowed you and analyze hidden accounts (blocked, deactivated, or suspended users)*
</details>

<details>
<summary><b>Network Lists</b></summary>

![Network Lists](.github/screenshots/network-lists.png)
*Browse mutual follows, non-followers, and followers-only lists*
</details>

---

## What This Tracks

### Network Analytics
- Current follower/following counts
- Mutual follows (people who follow you back)
- Non-mutual follows (you follow, they don't)
- Followers only (they follow, you don't)
- Unfollowers (last 30 days)
- Hidden accounts (blocked, deactivated, or suspended)

### Post Engagement
- Top posts by engagement score
- Likes, reposts, replies, quotes, bookmarks
- Indirect engagement (engagement on posts that quoted yours)
- Full post text (no truncation)
- Clickable post cards linking to Bluesky

### Historical Trends
- Follower/following growth over time
- Engagement timeline charts
- Posting activity patterns
- Engagement distribution breakdown

### Top Interactors
- People who engage most with your content
- Tracked from notification data

---

## Important: Database Persistence

**Measurements are only reliable from when you start collecting data.**

- Historical data **cannot** be retrieved before your first collection
- Unfollower tracking starts from your first run
- Keep your database backed up - it contains all historical data
- Run collections daily for accurate trend tracking

**Recommendation:** Set up daily scheduled collections (see [Scheduling](#scheduling) below).

---

## Requirements

### Bluesky App Password (Required)

You **must** generate an app password:

1. Go to [Bluesky Settings → App Passwords](https://bsky.app/settings/app-passwords)
2. Click "Add App Password"
3. Give it a name (e.g., "Analytics Tracker")
4. Copy the generated password
5. Use it in your `.env` file

**Why?** App passwords are more secure than your main password and can be revoked anytime.

### System Requirements

- Docker and Docker Compose
- 100MB disk space (database grows with data)
- Runs on: Linux (amd64, arm64, armv7), macOS, Windows

---

## Installation

### Docker Compose (Recommended)

```bash
# Download files
curl -O https://raw.githubusercontent.com/costantinoai/bluesky-tracker/main/docker-compose.selfhost.yml
mv docker-compose.selfhost.yml docker-compose.yml
curl -O https://raw.githubusercontent.com/costantinoai/bluesky-tracker/main/.env.example

# Configure
cp .env.example .env
nano .env  # Add your handle and app password

# Start
docker compose up -d
```

### Docker Run

```bash
docker run -d \
  --name bluesky-tracker \
  -p 8095:8095 \
  -v $(pwd)/data:/app/data \
  -e BLUESKY_HANDLE=yourname.bsky.social \
  -e BLUESKY_APP_PASSWORD=your-app-password \
  --restart unless-stopped \
  ghcr.io/costantinoai/bluesky-tracker:latest
```

### From Source

```bash
git clone https://github.com/costantinoai/bluesky-tracker.git
cd bluesky-tracker
cp .env.example .env
nano .env  # Add your handle and app password
docker compose up -d --build
```

---

## Configuration

Edit `.env` file:

```bash
BLUESKY_HANDLE=your-handle.bsky.social  # Required
BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # Required - get from https://bsky.app/settings/app-passwords
PORT=8095  # Web dashboard port
DATABASE_PATH=/app/data/bluesky.db  # Database location
TZ=Europe/Brussels  # Timezone for scheduled collections
```

---

## Scheduling

The tracker includes a built-in scheduler that runs at 6:00 AM (your configured timezone). For additional flexibility, set up platform-specific scheduling:

### Linux/macOS (Cron)

```bash
# Add to crontab (run daily at 2am)
crontab -e
```

Add this line:
```cron
0 2 * * * docker exec bluesky-tracker python /app/collector.py
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 2:00 AM
4. Action: Start a program
5. Program: `docker`
6. Arguments: `exec bluesky-tracker python /app/collector.py`

### Docker Compose with External Cron

```yaml
services:
  tracker:
    # ... your configuration ...

  cron:
    image: alpine:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: >
      sh -c "echo '0 2 * * * docker exec bluesky-tracker python /app/collector.py' | crontab - && crond -f"
```

### Synology NAS

1. Control Panel → Task Scheduler
2. Create → Scheduled Task → User-defined script
3. Schedule: Daily at 2:00 AM
4. Task Settings → Run command:
   ```bash
   docker exec bluesky-tracker python /app/collector.py
   ```

### Portainer

1. Go to Containers → bluesky-tracker
2. Console → Connect
3. Run manually: `python /app/collector.py`
4. Or use Portainer's webhook feature to trigger via HTTP

---

## Usage

### Access Points

- **Dashboard**: http://localhost:8095/report
- **API Stats**: http://localhost:8095/api/stats
- **Health Check**: http://localhost:8095/health
- **Prometheus Metrics**: http://localhost:8095/metrics

### Manual Data Collection

Trigger collection manually:

```bash
# Via Docker exec
docker exec bluesky-tracker python /app/collector.py

# Or via API (requires running container)
curl -X POST http://localhost:8095/api/collect
```

### Backup Your Data

**Important:** Your database contains all historical data.

```bash
# Backup
docker cp bluesky-tracker:/app/data/bluesky.db ./backup-$(date +%Y%m%d).db

# Restore
docker cp ./backup-20250101.db bluesky-tracker:/app/data/bluesky.db
docker restart bluesky-tracker
```

---

## Monitoring & Integrations

The tracker exports Prometheus metrics and can integrate with:

- **Grafana** - Visualization dashboards ([example](examples/grafana-dashboard.json))
- **Homepage** - Status widget ([example](examples/homepage-widget.yaml))
- **Uptime Kuma** - Health monitoring ([example](examples/uptime-kuma.json))
- **Traefik/Caddy** - Reverse proxy setups ([examples](examples/deployments/))

See [examples/](examples/) directory for configurations.

---

## Troubleshooting

### No Data Showing

- Check container logs: `docker logs bluesky-tracker`
- Verify environment variables are set correctly
- Ensure app password is valid
- Run manual collection: `docker exec bluesky-tracker python /app/collector.py`

### Unfollowers Not Detected

- Unfollowers are tracked from your **first** collection forward
- Historical unfollowers before first run **cannot** be detected
- Requires at least 2 collections (24 hours apart) to detect changes

### Database Errors

- Ensure `/app/data` volume is writable
- Check disk space: `df -h`
- Verify database isn't corrupted: `docker exec bluesky-tracker sqlite3 /app/data/bluesky.db "PRAGMA integrity_check;"`

### Rate Limits

- Bluesky API has rate limits
- The tracker includes delays (0.7s between requests)
- If you hit limits, wait and try again later

**Full troubleshooting guide:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Documentation

| Document | Description |
|----------|-------------|
| [INSTALLATION.md](INSTALLATION.md) | Detailed installation instructions for all platforms |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and solutions |
| [SECURITY.md](SECURITY.md) | Security best practices |
| [examples/](examples/) | Integration examples (Grafana, Homepage, etc.) |

---

## Platform Support

| Platform | Architecture | Status |
|----------|-------------|--------|
| Linux x86_64 | amd64 | ✅ Supported |
| Linux ARM64 | arm64 | ✅ Supported (Raspberry Pi 4/5, M1/M2 Macs) |
| Linux ARMv7 | armv7 | ✅ Supported (Raspberry Pi 3) |
| macOS Intel | amd64 | ✅ Supported |
| macOS Apple Silicon | arm64 | ✅ Supported |
| Windows | amd64 | ✅ Supported (via WSL2 or Docker Desktop) |

---

## Privacy & Security

- Your app password is stored **only** in your local `.env` file
- The `.env` file is automatically excluded from git
- No data is sent to external services except Bluesky's official API
- All data is stored locally in SQLite database
- App passwords can be revoked anytime from Bluesky settings

See [SECURITY.md](SECURITY.md) for detailed security information.

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/costantinoai/bluesky-tracker/issues)
- **Discussions**: [GitHub Discussions](https://github.com/costantinoai/bluesky-tracker/discussions)

---

**Note:** This is an unofficial tool and is not affiliated with Bluesky Social PBC.
