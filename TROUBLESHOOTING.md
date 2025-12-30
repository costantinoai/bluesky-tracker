# Troubleshooting

Common issues and solutions for Bluesky Tracker.

---

## Container Issues

### Container Won't Start

**Check logs:**
```bash
docker logs bluesky-tracker
```

**Common causes:**

**1. Missing credentials in `.env` file**
```
Error: BLUESKY_HANDLE is required
```

Solution:
```bash
# Create .env from example
cp .env.example .env
nano .env  # Add your handle and app password
docker compose restart
```

**2. Invalid handle format**
```bash
# Correct:
BLUESKY_HANDLE=yourname.bsky.social

# Wrong:
BLUESKY_HANDLE=@yourname.bsky.social  # No @ symbol
BLUESKY_HANDLE=yourname                # Need full handle
```

**3. Permission issues**
```
Error: Permission denied: '/app/data/bluesky.db'
```

Solution:
```bash
sudo chown -R $USER:$USER ./data
chmod 755 ./data
docker compose restart
```

### Container Keeps Restarting

**Check what's happening:**
```bash
# Watch logs in real-time
docker logs -f bluesky-tracker

# Check health status
docker inspect bluesky-tracker | grep -A 5 Health
```

**Common fixes:**

1. **Wait for startup** - Container needs 30-40 seconds to initialize
2. **Port conflict** - See [Port Already in Use](#port-already-in-use)
3. **Increase memory** - Edit docker-compose.yml:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 512M  # Increase from 256M
   ```

---

## Authentication

### Authentication Failed

**Error:**
```
❌ Authentication failed: Invalid identifier or password
```

**Solutions:**

**1. Verify credentials**
```bash
# Check handle (no @ symbol)
grep BLUESKY_HANDLE .env

# Check for extra spaces
cat .env | grep BLUESKY
```

**2. Generate new app password**
1. Go to https://bsky.app/settings/app-passwords
2. Delete old password (if exists)
3. Create new one named "Bluesky Tracker"
4. Copy to `.env` file immediately
5. Restart: `docker compose restart`

**3. Common mistakes**
- Extra spaces before/after values
- Using main password instead of app password
- Copy-paste errors (use Ctrl+V, not manual typing)

---

## Network & Ports

### Port Already in Use

**Error:**
```
Error: bind: address already in use
```

**Find what's using the port:**
```bash
sudo lsof -i :8095
# or
sudo netstat -tulpn | grep 8095
```

**Solution 1: Change port**
```bash
# In .env file
PORT=9095

# Restart
docker compose restart
```

**Solution 2: Stop conflicting service**
```bash
# Find process ID
sudo lsof -i :8095

# Stop it
sudo kill <PID>
```

### Can't Access Dashboard

**Diagnosis:**
```bash
# 1. Check container is running
docker ps | grep bluesky-tracker

# 2. Check health
curl http://localhost:8095/health

# 3. Check port mapping
docker port bluesky-tracker
```

**Solutions:**

1. **Container not running**: `docker compose up -d`
2. **Wrong port**: Check `docker ps` for actual port
3. **Firewall blocking**: `sudo ufw allow 8095/tcp`

### Access from Other Devices

**Works on localhost but not from other machines:**

Check port binding in docker-compose.yml:
```yaml
ports:
  - "0.0.0.0:8095:8095"  # Allow external access
```

**Warning:** Only do this on trusted networks. Use reverse proxy with HTTPS for public access.

---

## Data Collection

### No Data Appearing

**Symptoms:** Dashboard shows zeros, empty tables

**Diagnosis:**
```bash
# Check if collection ran
docker logs bluesky-tracker | grep "Collection complete"

# Check database exists
ls -lh data/bluesky.db

# Check for errors
docker logs bluesky-tracker | grep -i error
```

**Solutions:**

**1. Trigger manual collection**
```bash
curl -X POST http://localhost:8095/api/collect
```

**2. Wait for scheduled collection**
- Default: 6:00 AM (timezone from `.env` TZ setting)
- Check current time: `TZ=Europe/Brussels date`

**3. Check authentication**
See [Authentication Failed](#authentication-failed)

### Collection Failing

**Rate limiting (Error 429)**
```bash
# Bluesky API rate limit hit
# Wait 15 minutes and retry
sleep 900
curl -X POST http://localhost:8095/api/collect
```

**Network timeout**
```bash
# Check Bluesky API is reachable
curl https://bsky.social/xrpc/_health

# If fails, check internet connection
ping bsky.social
```

---

## Database

### Database Locked

**Error:**
```
database is locked
```

**Solution:**
Wait a few seconds and retry - SQLite uses file locking during writes.

**If persists:**
```bash
# Stop container
docker compose stop

# Remove lock files
rm -f data/*.db-shm data/*.db-wal

# Restart
docker compose up -d
```

### Corrupted Database

**Error:**
```
database disk image is malformed
```

**Solution 1: Restore from backup**
```bash
docker compose stop
cp backups/bluesky-YYYYMMDD.db data/bluesky.db
docker compose up -d
```

**Solution 2: Start fresh** (loses all data)
```bash
docker compose down
rm data/bluesky.db
docker compose up -d
curl -X POST http://localhost:8095/api/collect  # First collection
```

---

## Performance

### Slow Dashboard

**Optimize database:**
```bash
# Vacuum database (reclaim space)
docker exec bluesky-tracker sqlite3 /app/data/bluesky.db "VACUUM;"

# Check resource usage
docker stats bluesky-tracker
```

**If large database:**
- 100-150MB memory usage is normal
- Consider increasing resources in docker-compose.yml
- Use SSD instead of SD card (Raspberry Pi)

---

## Platform-Specific

### Raspberry Pi

**Out of memory:**
```bash
# Increase swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

**Correct architecture:**
```bash
# Raspberry Pi 4/5
docker pull --platform linux/arm64 ghcr.io/costantinoai/bluesky-tracker

# Raspberry Pi 3
docker pull --platform linux/arm/v7 ghcr.io/costantinoai/bluesky-tracker
```

### Synology NAS

**Port conflicts** - Use port above 10000 (Synology reserves many ports):
```bash
# In .env
PORT=10095
```

---

## Diagnostic Commands

Quick checks to diagnose issues:

```bash
# Container status
docker ps -a | grep bluesky-tracker

# Recent logs
docker logs --tail 50 bluesky-tracker

# Health check
curl -f http://localhost:8095/health

# API stats
curl http://localhost:8095/api/stats

# Resource usage
docker stats --no-stream bluesky-tracker

# Database size
ls -lh data/bluesky.db
```

---

## Getting Help

If issues persist:

### Create GitHub Issue

Include:
- Problem description
- Error messages from logs
- Output from diagnostic commands above
- Docker version: `docker --version`
- OS/platform: `uname -a`

**Important:** Remove passwords from logs before sharing!

Links:
- [GitHub Issues](https://github.com/costantinoai/bluesky-tracker/issues)
- [GitHub Discussions](https://github.com/costantinoai/bluesky-tracker/discussions)
