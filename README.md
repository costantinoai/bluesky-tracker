# 🦋 Bluesky Analytics Tracker

Comprehensive analytics dashboard for Bluesky social network activity tracking.

[![Docker Pulls](https://img.shields.io/docker/pulls/costantinoai/bluesky-tracker)](https://hub.docker.com/r/costantinoai/bluesky-tracker)
[![GitHub Release](https://img.shields.io/github/v/release/costantinoai/bluesky-tracker)](https://github.com/costantinoai/bluesky-tracker/releases)
[![Tests](https://github.com/costantinoai/bluesky-tracker/actions/workflows/test.yml/badge.svg)](https://github.com/costantinoai/bluesky-tracker/actions/workflows/test.yml)
[![Docker Build](https://github.com/costantinoai/bluesky-tracker/actions/workflows/docker-build.yml/badge.svg)](https://github.com/costantinoai/bluesky-tracker/actions/workflows/docker-build.yml)
[![License](https://img.shields.io/github/license/costantinoai/bluesky-tracker)](LICENSE)
[![Docker Image Size](https://img.shields.io/docker/image-size/costantinoai/bluesky-tracker/latest)](https://hub.docker.com/r/costantinoai/bluesky-tracker)
[![Platform Support](https://img.shields.io/badge/platform-amd64%20%7C%20arm64%20%7C%20armv7-blue)](https://hub.docker.com/r/costantinoai/bluesky-tracker)

---

## 🚀 Quick Start

### One-Command Installation

```bash
curl -sSL https://raw.githubusercontent.com/costantinoai/bluesky-tracker/main/setup.sh | bash
```

**That's it!** The script will:
- ✅ Check Docker installation
- ✅ Download configuration files
- ✅ Guide you through setup
- ✅ Start the tracker automatically

**Access your dashboard:** http://localhost:8095/report

### Alternative Installation Methods

<details>
<summary><b>Docker Compose</b></summary>

```bash
# Download files
curl -O https://raw.githubusercontent.com/costantinoai/bluesky-tracker/main/docker-compose.selfhost.yml
mv docker-compose.selfhost.yml docker-compose.yml
curl -O https://raw.githubusercontent.com/costantinoai/bluesky-tracker/main/.env.example

# Configure
cp .env.example .env
nano .env  # Add your Bluesky handle and app password

# Start
docker compose up -d
```
</details>

<details>
<summary><b>Docker Run</b></summary>

```bash
docker run -d \
  --name bluesky-tracker \
  -p 8095:8095 \
  -v $(pwd)/data:/app/data \
  -e BLUESKY_HANDLE=yourname.bsky.social \
  -e BLUESKY_APP_PASSWORD=your-app-password \
  --restart unless-stopped \
  costantinoai/bluesky-tracker:latest
```
</details>

<details>
<summary><b>Portainer</b></summary>

See [portainer-stack.yml](portainer-stack.yml) for a ready-to-use template.
</details>

**📖 Full installation guide:** [INSTALLATION.md](INSTALLATION.md)

---

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| **[Installation Guide](INSTALLATION.md)** | Complete installation instructions for all platforms |
| **[Troubleshooting](TROUBLESHOOTING.md)** | Common issues and solutions |
| **[Security Guide](SECURITY.md)** | Security best practices and recommendations |
| **[Examples](examples/)** | Integration examples (Grafana, Homepage, Traefik, etc.) |

---

## 🔐 Authentication Notice

**IMPORTANT: App password is OPTIONAL and NOT REQUIRED for most features!**

This tracker works WITHOUT authentication for:
- Public profile analytics
- Follower/following counts
- Public post engagement metrics
- Most dashboard features

Authentication is ONLY needed for:
- Private/protected accounts
- Detailed notification tracking
- Some advanced engagement metrics

**Privacy & Security:**
- Your password is NEVER shared with any external provider
- It is stored ONLY in your local `.env` file (never tracked in git)
- It is used ONLY by this tool to authenticate with Bluesky's official API
- You can run this tool completely password-free for public accounts

See `.env.example` for configuration details.

---

## 🌐 Access Points (when running)
- **Dashboard**: http://localhost:8095/report
- **API Stats**: http://localhost:8095/api/stats
- **Metrics**: http://localhost:8095/metrics (Prometheus)
- **Health**: http://localhost:8095/health

---

## ✨ Features

### 1. **Network Analytics**
- Real-time follower/following counts
- Mutual follows tracking
- Unfollower detection (30-day rolling window)
- Hidden account analysis (blocked/suspended accounts)
- "Not Following Back" identification
- "They Follow, You Don't" tracking

### 2. **Post Engagement Tracking**
- Top posts by engagement score
- Full post text display (no truncation)
- Clickable post cards (link to Bluesky)
- Engagement metrics:
  - ❤️ Likes
  - 🔄 Reposts
  - 💬 Replies
  - 💬 Quotes
  - 🔖 Bookmarks

### 3. **Indirect Engagement** 🆕
Tracks engagement on posts that **quoted** your posts:
- Indirect likes, reposts, replies, bookmarks
- Quote post detection
- Viral reach estimation
- Weighted in engagement score (0.5×)

### 4. **Top Interactors**
- 48 users tracked from notifications
- Interaction breakdown by type:
  - 💖 Likes
  - 💬 Replies
  - 🔄 Reposts
  - 💭 Quotes
  - 👤 Follows
- Weighted scoring system (replies = 5pts, quotes = 4pts, follows = 3pts, reposts = 2pts, likes = 1pt)
- Clickable profile cards

### 5. **Historical Analytics** 📊 🆕

#### **Interactive Time-Series Graphs**
Located in dedicated "Historical Analytics" section on dashboard.

**5 Chart Types:**

1. **Network Growth** (Line Chart)
   - Followers over time
   - Following over time
   - Dual-line visualization
   - Auto-scales with data

2. **Daily Net Change** (Bar Chart)
   - Net follower changes per day
   - Green bars = gains
   - Red bars = losses
   - Requires 2+ days of data

3. **Engagement Timeline** (Stacked Area Chart)
   - 5 engagement types visualized:
     - Likes (pink)
     - Reposts (green)
     - Replies (blue)
     - Quotes (purple)
     - Bookmarks (orange)
   - Stacked visualization shows total engagement growth

4. **Posting Activity** (Bar Chart)
   - Posts per day
   - Identify posting patterns
   - Find optimal posting frequency

5. **Engagement Distribution** (Doughnut Chart)
   - Pie chart breakdown of engagement types
   - Shows which metrics dominate
   - Updates with time range selection

#### **Dynamic Time Range Selection**
All graphs support 6 time ranges:
- **1D** - Last 24 hours
- **7D** - Last week
- **30D** - Last month (default)
- **90D** - Last quarter
- **1Y** - Last year
- **All** - Since beginning (all collected data)

#### **Summary Statistics**
4 key metric cards above graphs:
- Days Tracked
- Follower Change (±)
- Total Posts
- Avg Engagement per Post

All statistics update dynamically when changing time ranges.

---

## 🛠️ Technical Stack

### Backend
- **Language**: Python 3.11
- **Framework**: Flask + Gunicorn
- **Database**: SQLite
- **Scheduler**: APScheduler (6 AM daily collection)
- **Metrics**: Prometheus Client

### Frontend
- **Charts**: Chart.js 4.4.1
- **Icons**: Material Design Icons + Colored Emojis
- **Design**: Material Design 3 principles
- **Colors**: Blue theme (#1976D2, #0288D1, #0097A7)

### Data Collection
- **API**: Bluesky AT Protocol
- **Auth**: App Password (stored in .env)
- **Endpoints Used**:
  - `app.bsky.graph.getFollowers`
  - `app.bsky.graph.getFollows`
  - `app.bsky.feed.getAuthorFeed`
  - `app.bsky.feed.getQuotes` (for indirect engagement)
  - `app.bsky.notification.listNotifications`
  - `app.bsky.graph.getMutes`
  - `app.bsky.graph.getBlocks`

---

## 📊 Database Schema

### Key Tables:

#### **followers_snapshot**
Daily snapshots of followers
```sql
- collection_date (DATE)
- did (TEXT) - Stable identifier
- handle (TEXT) - Display handle
```

#### **following_snapshot**
Daily snapshots of following
```sql
- collection_date (DATE)
- did (TEXT)
- handle (TEXT)
```

#### **post_engagement**
Post metrics with indirect engagement
```sql
- collection_date (DATE)
- post_uri (TEXT)
- post_text (TEXT)
- created_at (TEXT)
- like_count, repost_count, reply_count, quote_count, bookmark_count
- indirect_likes, indirect_reposts, indirect_replies, indirect_bookmarks
```

#### **daily_metrics**
Daily follower/following aggregates
```sql
- metric_date (DATE)
- follower_count, following_count
- unfollower_count, new_follower_count
```

#### **follower_velocity**
Daily growth rates
```sql
- metric_date (DATE)
- new_followers, lost_followers
- new_following, lost_following
- net_follower_change, net_following_change
```

#### **daily_engagement_metrics** 🆕
Daily engagement aggregates for graphs
```sql
- metric_date (DATE)
- total_posts
- total_likes, total_reposts, total_replies, total_quotes, total_bookmarks
- total_indirect_likes, total_indirect_reposts, total_indirect_replies, total_indirect_bookmarks
- avg_engagement_per_post
```

#### **interactions**
Top interactor tracking
```sql
- collection_date (DATE)
- user_did, user_handle, user_display_name
- likes_received, replies_received, reposts_received, quotes_received, follows_received
- interaction_score
```

---

## 🔧 API Endpoints

### Dashboard Endpoints
- `GET /report` - Main HTML dashboard
- `GET /api/stats` - Summary statistics (for Homepage widget)
- `GET /api/collect` (POST) - Manual data collection trigger
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

### Graph Data Endpoints 🆕
All support `?days=N` parameter:

- `GET /api/graphs/follower-growth?days=30`
  - Returns: `{dates: [], followers: [], following: []}`

- `GET /api/graphs/net-growth?days=30`
  - Returns: `{dates: [], netFollowers: [], netFollowing: []}`

- `GET /api/graphs/engagement-timeline?days=30`
  - Returns: `{dates: [], likes: [], reposts: [], replies: [], quotes: [], bookmarks: []}`

- `GET /api/graphs/posting-frequency?days=30`
  - Returns: `{dates: [], posts: []}`

- `GET /api/graphs/engagement-breakdown?days=30`
  - Returns: `{labels: [], values: []}`

- `GET /api/graphs/stats-summary?days=30`
  - Returns: `{daysTracked, followerChange, avgFollowers, totalEngagement, avgEngagementPerPost, totalPosts}`

---

## ⚙️ Configuration

### Environment Variables (.env)

**Quick Start:**
1. Copy `.env.example` to `.env`
2. Set your `BLUESKY_HANDLE`
3. (Optional) Set `BLUESKY_APP_PASSWORD` only if needed
4. Adjust `PORT` and `TZ` if desired

**Example .env file:**
```bash
BLUESKY_HANDLE=your-handle.bsky.social
BLUESKY_APP_PASSWORD=        # OPTIONAL - leave empty for public accounts
PORT=8095
DATABASE_PATH=/app/data/bluesky.db
TZ=Europe/Brussels
```

**Note:** The app password is optional and only needed for private accounts or advanced features. See the Authentication Notice section above for details.

### Scheduled Collection
- **Time**: 6:00 AM Europe/Brussels
- **Frequency**: Daily
- **Duration**: ~25-30 seconds
- **Actions**:
  1. Authenticate with Bluesky
  2. Fetch followers list (pagination)
  3. Fetch following list (pagination)
  4. Fetch muted/blocked accounts
  5. Fetch post engagement data (50 posts)
  6. Fetch indirect engagement (quotes)
  7. Fetch interactions (notifications)
  8. Calculate changes vs previous day
  9. Update all metrics
  10. Aggregate daily statistics for graphs

---

## 📈 Engagement Score Calculation

### Formula
```
Direct Score = likes + (reposts × 2) + (replies × 3) + (bookmarks × 2)
Indirect Score = (indirect_likes + (indirect_reposts × 2) + (indirect_replies × 3) + (indirect_bookmarks × 2)) × 0.5
Total Score = Direct + Indirect
```

### Weights Rationale
- **Likes**: 1× (passive engagement)
- **Reposts/Bookmarks**: 2× (active amplification/saving)
- **Replies**: 3× (high-value conversation)
- **Indirect**: 0.5× (secondary reach, still valuable)

---

## 🎨 UI Design

### Color Palette
- **Primary Blue**: #1976D2
- **Secondary Blue**: #0288D1
- **Tertiary Cyan**: #0097A7
- **Success Green**: #00897B
- **Error Red**: #D32F2F
- **Background**: #E3F2FD (light blue)

### Icons
- **Sections**: Colored emojis (📊, 💔, 🚫, 👥, 🤝, 👻, 🌟)
- **Stats Cards**: Colored emojis (👥, ➕, 🤝, 🚫, 💔, 👤)
- **Post Metrics**: Material Design Icons (monochrome blue)
- **Consistency**: All large icons use emojis, inline metrics use MD icons

### Post Cards
- Avatar + Name + Handle + Timestamp (Bluesky-style)
- Full post text (white-space: pre-wrap)
- Horizontal metrics bar (likes, reposts, replies, quotes, bookmarks)
- Engagement score (right-aligned)
- Indirect engagement badge (when > 0)
- Clickable (opens on bsky.app)

---

## 🔍 Monitoring

### Prometheus Metrics
```
bluesky_follower_count
bluesky_following_count
bluesky_unfollowers_30d
bluesky_non_mutual_following
bluesky_followers_only
bluesky_api_requests_total{endpoint, status}
bluesky_collection_duration_seconds
```

### Grafana Integration
Scrape target configured in `monitoring/prometheus/prometheus.yml`:
```yaml
- job_name: "bluesky"
  static_configs:
    - targets: ["bluesky-tracker:8095"]
```

---

## 🚀 Deployment

### Initial Setup
```bash
# Clone or navigate to the repository
cd bluesky-tracker

# Create your configuration file
cp .env.example .env

# Edit .env with your Bluesky handle (and optionally app password)
nano .env  # or use your preferred editor
```

### Build & Run
```bash
docker compose up -d --build
```

### View Logs
```bash
docker logs bluesky-tracker -f
```

### Manual Collection
```bash
curl -X POST http://localhost:8095/api/collect
```

### Database Backup
```bash
cp data/bluesky.db data/bluesky_backup_$(date +%Y%m%d).db
```

---

## 📚 File Structure
```
bluesky-tracker/
├── app.py                  # Flask application + API endpoints
├── collector.py            # Bluesky data collection logic
├── database.py             # SQLite operations
├── config.py               # Configuration management
├── templates.py            # HTML template generation (includes Chart.js)
├── Dockerfile              # Container definition
├── docker-compose.yml      # Service deployment
├── .env.example            # Example configuration (copy to .env)
├── .env                    # Your credentials (gitignored, create from .env.example)
├── .gitignore              # Git exclusions
├── .dockerignore          # Build optimization
├── data/                   # Persistent volume (gitignored)
│   └── bluesky.db         # SQLite database
└── README.md              # This file
```

---

## 🐛 Troubleshooting

### Charts Not Displaying
1. Check browser console for JavaScript errors
2. Verify Chart.js CDN is loaded: View page source and search for "chart.umd.min.js"
3. Verify graph APIs return data: `curl http://localhost:8095/api/graphs/follower-growth?days=1`
4. Check if data exists: `sqlite3 data/bluesky.db "SELECT * FROM daily_metrics"`

### Empty Graphs (But Data Exists)
- **Single data point**: Charts will show single points with larger radius (pointRadius: 6)
- **No data yet**: Charts display "No data available yet" message
- **Need 2+ days**: Net growth chart requires at least 2 days to show changes

### Collection Failures
1. Check logs: `docker logs bluesky-tracker --tail 50`
2. Verify authentication: Look for "✓ Authenticated successfully"
3. Check API rate limits (Bluesky may throttle)
4. Verify app password is valid in .env

### Database Locked Errors
```bash
# Stop container
docker compose down

# Check for stale lock
ls -la data/.bluesky.db*

# Remove lock if exists
rm data/.bluesky.db-shm data/.bluesky.db-wal

# Restart
docker compose up -d
```

---

## 📖 Version History

### v3.0.0 (2025-12-29) - Historical Analytics 🆕
- ✅ Added Chart.js 4.4.1 integration
- ✅ Implemented 5 interactive time-series graphs
- ✅ Dynamic time range selection (1D/7D/30D/90D/1Y/All)
- ✅ Daily engagement metrics aggregation
- ✅ Summary statistics cards
- ✅ Graph API endpoints with time-range support
- ✅ Single data point rendering (visible with larger points)
- ✅ Empty data handling with user feedback
- ✅ Responsive graph layout

### v2.5.0 (2025-12-29) - Bookmarks & Indirect Engagement
- ✅ Added bookmark/save tracking
- ✅ Indirect engagement calculation (quote posts)
- ✅ Updated engagement score formula
- ✅ Bookmark icon in metrics
- ✅ Indirect engagement badge

### v2.0.0 (2025-12-29) - Enhanced UI & Features
- ✅ Improved post card design (avatar, name, handle, timestamp)
- ✅ Consistent emoji/icon styling
- ✅ Top Interactors section
- ✅ Full post text display
- ✅ Clickable post cards
- ✅ Material Design icons
- ✅ Blue color theme

### v1.0.0 (2025-12-28) - Initial Release
- ✅ Basic follower/following tracking
- ✅ Unfollower detection
- ✅ Hidden account analysis
- ✅ Post engagement tracking
- ✅ Prometheus metrics
- ✅ Daily automated collection

---

## 🎯 Future Enhancements

See `/tmp/BLUESKY_ANALYTICS_ROADMAP.md` for comprehensive roadmap including:
- Optimal posting times heatmap
- Content type performance analysis
- Topic/keyword tracking
- Predictive analytics
- Network graph visualization
- Community detection
- Follower retention analysis

---

## 📧 Support

For issues or questions:
1. Check logs: `docker logs bluesky-tracker -f`
2. Verify health: `curl http://localhost:8095/health`
3. Test APIs manually with curl
4. Review database: `sqlite3 data/bluesky.db`

---

**Last Updated**: December 29, 2025
**License**: MIT (see repository for details)
