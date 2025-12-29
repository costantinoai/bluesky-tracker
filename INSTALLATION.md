# Installation Guide

Complete guide for installing and running Bluesky Tracker.

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
  - [Method 1: One-Command Setup (Recommended)](#method-1-one-command-setup-recommended)
  - [Method 2: Docker Compose](#method-2-docker-compose)
  - [Method 3: Docker Run](#method-3-docker-run)
  - [Method 4: Portainer Stack](#method-4-portainer-stack)
- [Getting Your App Password](#getting-your-app-password)
- [Configuration](#configuration)
- [Verification](#verification)
- [Platform-Specific Guides](#platform-specific-guides)
- [Updating](#updating)
- [Uninstalling](#uninstalling)

---

## Quick Start

The fastest way to get started:

```bash
curl -sSL https://raw.githubusercontent.com/costantinoai/bluesky-tracker/main/setup.sh | bash
```

This script will:
- Check Docker installation
- Download configuration files
- Guide you through setup
- Start the tracker automatically

---

## Prerequisites

### Required

- **Docker** (20.10 or later)
  - Ubuntu/Debian: [Installation Guide](https://docs.docker.com/engine/install/ubuntu/)
  - macOS: [Docker Desktop](https://docs.docker.com/desktop/mac/install/)
  - Windows: [Docker Desktop](https://docs.docker.com/desktop/windows/install/)
  - Raspberry Pi: [Installation Guide](https://docs.docker.com/engine/install/debian/)

- **Docker Compose** (v2.0 or later)
  - Usually included with Docker Desktop
  - Linux: `sudo apt-get install docker-compose-plugin`

- **Bluesky Account** with app password
  - See [Getting Your App Password](#getting-your-app-password)

### Optional

- **Reverse Proxy** (for HTTPS access)
  - Traefik, Caddy, Nginx Proxy Manager, or SWAG
  - See [examples/deployments/](examples/deployments/) for configurations

---

## Installation Methods

### Method 1: One-Command Setup (Recommended)

The easiest installation method:

```bash
curl -sSL https://raw.githubusercontent.com/costantinoai/bluesky-tracker/main/setup.sh | bash
```

**What it does:**
1. Checks for Docker and Docker Compose
2. Creates installation directory (`~/bluesky-tracker`)
3. Downloads configuration files
4. Prompts for your Bluesky credentials
5. Pulls the latest Docker image
6. Starts the service

**Manual review option:**
```bash
# Download and review the script first
curl -sSL -o setup.sh https://raw.githubusercontent.com/costantinoai/bluesky-tracker/main/setup.sh
cat setup.sh  # Review the script
chmod +x setup.sh
./setup.sh
```

---

### Method 2: Docker Compose

For more control over the installation:

#### Step 1: Create Directory

```bash
mkdir -p ~/bluesky-tracker
cd ~/bluesky-tracker
```

#### Step 2: Download Files

**Option A: Download from GitHub**
```bash
curl -O https://raw.githubusercontent.com/costantinoai/bluesky-tracker/main/docker-compose.selfhost.yml
mv docker-compose.selfhost.yml docker-compose.yml

curl -O https://raw.githubusercontent.com/costantinoai/bluesky-tracker/main/.env.example
```

**Option B: Create Manually**

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  bluesky-tracker:
    image: costantinoai/bluesky-tracker:latest
    container_name: bluesky-tracker
    ports:
      - "8095:8095"
    volumes:
      - ./data:/app/data
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8095/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

Create `.env.example`:
```bash
BLUESKY_HANDLE=your-handle.bsky.social
BLUESKY_APP_PASSWORD=your-app-password
PORT=8095
TZ=Europe/Brussels
```

#### Step 3: Configure

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Edit the following required variables:
- `BLUESKY_HANDLE`: Your Bluesky handle (e.g., `yourname.bsky.social`)
- `BLUESKY_APP_PASSWORD`: Your app password (see [Getting Your App Password](#getting-your-app-password))

Optional variables:
- `PORT`: Web interface port (default: `8095`)
- `TZ`: Timezone for collection schedule (default: `Europe/Brussels`)

#### Step 4: Start

```bash
docker compose up -d
```

#### Step 5: Check Status

```bash
docker compose ps
docker compose logs -f
```

---

### Method 3: Docker Run

For a single-command deployment without Docker Compose:

```bash
docker run -d \
  --name bluesky-tracker \
  -p 8095:8095 \
  -v $(pwd)/data:/app/data \
  -e BLUESKY_HANDLE=yourname.bsky.social \
  -e BLUESKY_APP_PASSWORD=your-app-password \
  -e TZ=Europe/Brussels \
  --restart unless-stopped \
  costantinoai/bluesky-tracker:latest
```

**To view logs:**
```bash
docker logs -f bluesky-tracker
```

**To stop:**
```bash
docker stop bluesky-tracker
docker rm bluesky-tracker
```

---

### Method 4: Portainer Stack

If you're using Portainer:

#### Step 1: Open Portainer

Navigate to **Stacks** → **Add stack**

#### Step 2: Paste Configuration

Name: `bluesky-tracker`

Web editor:
```yaml
version: '3.8'

services:
  bluesky-tracker:
    image: costantinoai/bluesky-tracker:latest
    container_name: bluesky-tracker
    ports:
      - "8095:8095"
    volumes:
      - bluesky-data:/app/data
    environment:
      - BLUESKY_HANDLE=${BLUESKY_HANDLE}
      - BLUESKY_APP_PASSWORD=${BLUESKY_APP_PASSWORD}
      - TZ=${TZ:-Europe/Brussels}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8095/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  bluesky-data:
```

#### Step 3: Add Environment Variables

Click **Add an environment variable** for each:
- `BLUESKY_HANDLE` = `yourname.bsky.social`
- `BLUESKY_APP_PASSWORD` = `your-app-password`
- `TZ` = `Europe/Brussels` (optional)

#### Step 4: Deploy

Click **Deploy the stack**

---

## Getting Your App Password

Bluesky app passwords are more secure than using your main password and can be revoked anytime.

### Steps:

1. **Log in to Bluesky**
   - Go to [https://bsky.app](https://bsky.app)

2. **Open Settings**
   - Click your profile picture → Settings

3. **Navigate to App Passwords**
   - Go to [https://bsky.app/settings/app-passwords](https://bsky.app/settings/app-passwords)
   - Or: Settings → Privacy and Security → App Passwords

4. **Create New Password**
   - Click **"Add App Password"**
   - Name it: `Bluesky Tracker` (or any name you prefer)
   - Click **"Create"**

5. **Copy the Password**
   - Copy the generated password immediately
   - You won't be able to see it again!
   - Store it in your `.env` file as `BLUESKY_APP_PASSWORD`

### Security Notes:

- App passwords are scoped to specific permissions
- They can be revoked anytime without changing your main password
- Each app should have its own password
- Never share your app password publicly
- Don't commit `.env` files to git

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BLUESKY_HANDLE` | Yes | - | Your Bluesky handle (e.g., `name.bsky.social`) |
| `BLUESKY_APP_PASSWORD` | Yes | - | App password from Bluesky settings |
| `PORT` | No | `8095` | Port for web interface |
| `DATABASE_PATH` | No | `/app/data/bluesky.db` | SQLite database location |
| `TZ` | No | `Europe/Brussels` | Timezone for scheduled collection |

### Collection Schedule

By default, data is collected daily at **06:00 AM** in the configured timezone.

To change the timezone:
```bash
# In .env file
TZ=America/New_York  # Eastern Time
TZ=America/Los_Angeles  # Pacific Time
TZ=Europe/London  # GMT
TZ=Asia/Tokyo  # JST
```

[List of valid timezones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

### Manual Collection

Trigger collection anytime via API:
```bash
curl -X POST http://localhost:8095/api/collect
```

---

## Verification

After installation, verify everything is working:

### 1. Check Health

```bash
curl http://localhost:8095/health
```

Expected response:
```json
{"status": "ok", "timestamp": "2024-01-15T10:30:00.000000"}
```

### 2. Access Dashboard

Open in browser:
```
http://localhost:8095/report
```

You should see the analytics dashboard.

### 3. Check Metrics

```bash
curl http://localhost:8095/metrics
```

Should return Prometheus metrics.

### 4. View API Stats

```bash
curl http://localhost:8095/api/stats
```

Expected response:
```json
{
  "follower_count": 100,
  "following_count": 50,
  "unfollowers_30d": 5,
  "non_mutual_following": 10,
  "followers_only": 20
}
```

### 5. Check Logs

```bash
docker compose logs bluesky-tracker
# or
docker logs bluesky-tracker
```

Look for:
- `✓ Authenticated successfully`
- `Bluesky Tracker starting on port 8095`
- No error messages

---

## Platform-Specific Guides

### Raspberry Pi

Bluesky Tracker supports ARM architectures (arm64, armv7).

#### Raspberry Pi 4/5 (64-bit)
```bash
# Same installation as above
curl -sSL https://raw.githubusercontent.com/costantinoai/bluesky-tracker/main/setup.sh | bash
```

#### Raspberry Pi 3 (32-bit)
```bash
# Specify armv7 platform
docker run -d \
  --platform linux/arm/v7 \
  --name bluesky-tracker \
  -p 8095:8095 \
  -v $(pwd)/data:/app/data \
  -e BLUESKY_HANDLE=yourname.bsky.social \
  -e BLUESKY_APP_PASSWORD=your-app-password \
  --restart unless-stopped \
  costantinoai/bluesky-tracker:latest
```

#### Performance Tips
- Use SSD or USB3 storage for database
- Allocate at least 256MB RAM
- Consider running on Raspberry Pi 4+ for better performance

### Synology NAS

1. Open **Docker** package
2. Go to **Registry** → Search `costantinoai/bluesky-tracker`
3. Download the image
4. Go to **Image** → Select the image → **Launch**
5. Configure:
   - Container name: `bluesky-tracker`
   - Port: `8095` → `8095`
   - Volume: Create folder `/docker/bluesky-tracker/data` → Mount to `/app/data`
   - Environment: Add `BLUESKY_HANDLE` and `BLUESKY_APP_PASSWORD`
6. Start container

### Unraid

1. Go to **Docker** tab
2. Click **Add Container**
3. Fill in:
   - Name: `bluesky-tracker`
   - Repository: `costantinoai/bluesky-tracker:latest`
   - Port: `8095` → `8095`
   - Path: `/mnt/user/appdata/bluesky-tracker` → `/app/data`
   - Variable: `BLUESKY_HANDLE` = `yourname.bsky.social`
   - Variable: `BLUESKY_APP_PASSWORD` = `your-app-password`
4. Click **Apply**

### macOS (Apple Silicon M1/M2)

The image supports arm64 natively:

```bash
docker run -d \
  --platform linux/arm64 \
  --name bluesky-tracker \
  -p 8095:8095 \
  -v $(pwd)/data:/app/data \
  -e BLUESKY_HANDLE=yourname.bsky.social \
  -e BLUESKY_APP_PASSWORD=your-app-password \
  --restart unless-stopped \
  costantinoai/bluesky-tracker:latest
```

---

## Updating

### Docker Compose

```bash
cd ~/bluesky-tracker
docker compose pull
docker compose up -d
```

### Docker Run

```bash
docker pull costantinoai/bluesky-tracker:latest
docker stop bluesky-tracker
docker rm bluesky-tracker
# Re-run the docker run command from installation
```

### Portainer

1. Go to **Stacks** → Select `bluesky-tracker`
2. Click **Pull and redeploy**

---

## Uninstalling

### Docker Compose

```bash
cd ~/bluesky-tracker
docker compose down -v  # -v removes volumes (deletes data)
cd ..
rm -rf bluesky-tracker
```

**To keep data:**
```bash
docker compose down  # Without -v
cd ..
rm -rf bluesky-tracker/docker-compose.yml  # Keep data folder
```

### Docker Run

```bash
docker stop bluesky-tracker
docker rm bluesky-tracker
docker rmi costantinoai/bluesky-tracker
rm -rf ~/bluesky-tracker  # If you want to delete data
```

---

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

**Quick checks:**

1. **Container won't start**
   ```bash
   docker logs bluesky-tracker
   ```

2. **Port already in use**
   ```bash
   # Change port in .env or docker command
   PORT=9095
   ```

3. **Authentication failed**
   - Verify handle doesn't include `@` symbol
   - Generate a new app password
   - Check for typos in `.env`

4. **No data appearing**
   - Wait until 6 AM (collection time)
   - Or trigger manually: `curl -X POST http://localhost:8095/api/collect`

---

## Next Steps

- **Monitoring**: See [examples/grafana-dashboard.json](examples/grafana-dashboard.json)
- **Reverse Proxy**: See [examples/deployments/](examples/deployments/)
- **Homepage Integration**: See [examples/homepage-widget.yaml](examples/homepage-widget.yaml)
- **Uptime Monitoring**: See [examples/uptime-kuma.json](examples/uptime-kuma.json)

---

## Support

- **Issues**: [GitHub Issues](https://github.com/costantinoai/bluesky-tracker/issues)
- **Discussions**: [GitHub Discussions](https://github.com/costantinoai/bluesky-tracker/discussions)
- **Documentation**: [README.md](README.md)
