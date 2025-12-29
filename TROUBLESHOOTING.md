# Troubleshooting Guide

Common issues and solutions for Bluesky Tracker.

## Table of Contents

- [Container Issues](#container-issues)
- [Authentication Problems](#authentication-problems)
- [Network & Port Issues](#network--port-issues)
- [Data Collection Issues](#data-collection-issues)
- [Performance Issues](#performance-issues)
- [Database Problems](#database-problems)
- [Platform-Specific Issues](#platform-specific-issues)

---

## Container Issues

### Container Won't Start

**Symptoms:**
- Container exits immediately
- `docker ps` doesn't show the container

**Diagnosis:**
```bash
# Check container logs
docker logs bluesky-tracker

# Check exit code
docker ps -a --filter "name=bluesky-tracker"
```

**Common Causes:**

#### 1. Missing Environment Variables

**Error:**
```
CONFIGURATION ERROR
✗ BLUESKY_HANDLE is required
✗ BLUESKY_APP_PASSWORD is required
```

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Verify contents
cat .env | grep -v PASSWORD  # Don't show password

# Fix: Create or update .env
cp .env.example .env
nano .env  # Add your credentials
```

#### 2. Invalid Handle Format

**Error:**
```
BLUESKY_HANDLE is required
```

**Solution:**
```bash
# Correct formats:
BLUESKY_HANDLE=yourname.bsky.social  # ✓
BLUESKY_HANDLE=user.custom-domain.com  # ✓

# Wrong formats:
BLUESKY_HANDLE=@yourname.bsky.social  # ✗ (no @ symbol)
BLUESKY_HANDLE=yourname  # ✗ (needs full handle)
```

#### 3. Permission Issues

**Error:**
```
Permission denied: '/app/data/bluesky.db'
```

**Solution:**
```bash
# Fix data directory permissions
sudo chown -R $USER:$USER ./data
chmod 755 ./data

# Or recreate with correct permissions
rm -rf ./data
mkdir -p ./data
```

### Container Keeps Restarting

**Diagnosis:**
```bash
# Check restart count
docker ps -a

# Watch logs in real-time
docker logs -f bluesky-tracker
```

**Solutions:**

1. **Health check failing:**
   ```bash
   # Check health status
   docker inspect bluesky-tracker | grep -A 10 Health

   # Wait longer (container needs time to start)
   docker-compose up -d
   sleep 40  # Wait for start_period
   curl http://localhost:8095/health
   ```

2. **Resource exhaustion:**
   ```bash
   # Check resource usage
   docker stats bluesky-tracker

   # Increase limits in docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 512M  # Increase from 256M
   ```

3. **Port conflicts:**
   See [Network & Port Issues](#network--port-issues)

---

## Authentication Problems

### Authentication Failed

**Error:**
```
❌ Authentication failed: Invalid identifier or password
```

**Solutions:**

#### 1. Verify Credentials

```bash
# Check handle is correct (no @ symbol)
grep BLUESKY_HANDLE .env

# Regenerate app password
# 1. Go to https://bsky.app/settings/app-passwords
# 2. Delete old password
# 3. Create new one named "Bluesky Tracker"
# 4. Update .env immediately
```

#### 2. Check for Typos

```bash
# Common issues:
# - Extra spaces
# - Wrong quotes
# - Hidden characters

# Verify no extra spaces
cat -A .env | grep BLUESKY

# Should show:
# BLUESKY_HANDLE=name.bsky.social$
# BLUESKY_APP_PASSWORD=xxxx$

# Fix extra spaces:
sed -i 's/ *$//' .env  # Remove trailing spaces
```

#### 3. Password Characters

```bash
# App passwords are case-sensitive
# - Must be exact match
# - Copy-paste to avoid typos
# - No spaces at beginning or end
```

### Password Not Working After Update

**Solution:**
```bash
# Bluesky may have revoked the password
# Create a new one:

# 1. Revoke old password on Bluesky
# 2. Generate new app password
# 3. Update .env
nano .env

# 4. Restart container
docker-compose restart
```

---

## Network & Port Issues

### Port Already in Use

**Error:**
```
Error: bind: address already in use
```

**Diagnosis:**
```bash
# Find what's using port 8095
sudo lsof -i :8095
# or
sudo netstat -tulpn | grep 8095
```

**Solutions:**

#### 1. Change Port

```bash
# In .env file
PORT=9095  # Use different port

# Or in docker-compose.yml
ports:
  - "9095:8095"  # HOST:CONTAINER

# Restart
docker-compose up -d
```

#### 2. Stop Conflicting Service

```bash
# Identify the process
sudo lsof -i :8095

# Stop it
sudo kill <PID>

# Or stop the service
sudo systemctl stop <service-name>
```

### Can't Access Dashboard

**Symptoms:**
- Browser shows "Connection refused"
- `curl localhost:8095` fails

**Diagnosis:**
```bash
# 1. Check container is running
docker ps | grep bluesky-tracker

# 2. Check port mapping
docker port bluesky-tracker

# 3. Check health
curl http://localhost:8095/health
```

**Solutions:**

#### 1. Container Not Running
```bash
docker-compose up -d
docker logs bluesky-tracker
```

#### 2. Wrong Port
```bash
# Check actual port
docker ps

# Access on correct port
curl http://localhost:ACTUAL_PORT/health
```

#### 3. Firewall Blocking
```bash
# Allow port through firewall
sudo ufw allow 8095/tcp

# Or disable firewall temporarily (testing only!)
sudo ufw disable
```

#### 4. Docker Network Issues
```bash
# Restart Docker
sudo systemctl restart docker

# Recreate container
docker-compose down
docker-compose up -d
```

### Can't Access from Other Devices

**Symptoms:**
- Works on localhost
- Doesn't work from other machines

**Solution:**
```bash
# Check port binding
docker ps

# If shows 127.0.0.1:8095
# Change to 0.0.0.0:8095 in docker-compose.yml
ports:
  - "0.0.0.0:8095:8095"  # Allow external access

# WARNING: Only do this behind a firewall!
# Use reverse proxy with TLS for public access
```

---

## Data Collection Issues

### No Data Appearing

**Symptoms:**
- Dashboard shows zero followers
- Empty tables
- No historical data

**Diagnosis:**
```bash
# Check logs for collection
docker logs bluesky-tracker | grep -i "collection"

# Check database size
ls -lh data/bluesky.db

# Check last collection time
docker logs bluesky-tracker | grep "Collection complete"
```

**Solutions:**

#### 1. Wait for Scheduled Collection
```bash
# Default schedule: 06:00 AM Europe/Brussels
# Check current time in that timezone
TZ=Europe/Brussels date

# Or trigger manual collection
curl -X POST http://localhost:8095/api/collect
```

#### 2. Check Collection Logs
```bash
# View full collection log
docker logs bluesky-tracker 2>&1 | grep -A 20 "Starting collection"

# Look for errors
docker logs bluesky-tracker 2>&1 | grep -i error
```

#### 3. Verify API Access
```bash
# Test Bluesky API is reachable
curl https://bsky.social/xrpc/_health

# If timeout, check network/firewall
```

### Collection Failing

**Error:**
```
Collection failed: <error message>
```

**Common Causes:**

#### 1. Authentication Issues
See [Authentication Problems](#authentication-problems)

#### 2. Rate Limiting
```
Error 429: Too Many Requests
```

**Solution:**
```bash
# Wait 15 minutes and retry
sleep 900
curl -X POST http://localhost:8095/api/collect

# Increase delay in code (advanced)
# REQUEST_DELAY already set to 0.7s
```

#### 3. Network Timeout
```
Connection timeout
```

**Solution:**
```bash
# Check internet connection
ping bsky.social

# Increase Docker timeout (if needed)
# Restart Docker daemon
sudo systemctl restart docker
```

---

## Performance Issues

### Slow Response Times

**Diagnosis:**
```bash
# Check resource usage
docker stats bluesky-tracker

# Check database size
du -sh data/bluesky.db

# Check query performance
docker exec bluesky-tracker sqlite3 /app/data/bluesky.db "ANALYZE;"
```

**Solutions:**

#### 1. Database Optimization
```bash
# Vacuum database
docker exec bluesky-tracker sqlite3 /app/data/bluesky.db "VACUUM;"

# Rebuild indexes
docker exec bluesky-tracker sqlite3 /app/data/bluesky.db "REINDEX;"
```

#### 2. Increase Resources
```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      memory: 512M  # Increase from 256M
      cpus: '1.0'   # Increase from 0.5
```

#### 3. Storage Performance
```bash
# Use SSD instead of SD card (Raspberry Pi)
# Move data to faster storage
docker-compose down
mv data /mnt/ssd/bluesky-tracker-data
ln -s /mnt/ssd/bluesky-tracker-data data
docker-compose up -d
```

### High Memory Usage

**Diagnosis:**
```bash
docker stats bluesky-tracker
```

**Solutions:**

#### 1. Normal Operation
- 100-150MB is normal
- Spikes during collection are expected

#### 2. Memory Leak
```bash
# Restart container
docker-compose restart

# If persists, check logs
docker logs bluesky-tracker | grep -i "memory\|oom"
```

#### 3. Too Many Workers
```bash
# Gunicorn uses 2 workers by default
# Reduce if needed (modify Dockerfile)
# CMD ["gunicorn", "--workers=1", ...]
```

---

## Database Problems

### Database Locked

**Error:**
```
database is locked
```

**Solutions:**

#### 1. Wait and Retry
```bash
# SQLite uses file locking
# Wait a few seconds and retry
sleep 5
curl http://localhost:8095/api/stats
```

#### 2. Close Other Connections
```bash
# Don't access database while collection is running
# Wait for collection to finish
docker logs -f bluesky-tracker | grep "Collection complete"
```

#### 3. Fix Stale Lock
```bash
# Stop container
docker-compose stop

# Check for lock files
ls -la data/

# Remove stale locks (if any)
rm -f data/*.db-shm data/*.db-wal

# Restart
docker-compose up -d
```

### Corrupted Database

**Symptoms:**
- "database disk image is malformed"
- SQL errors in logs
- Missing data

**Solutions:**

#### 1. Try Repair
```bash
# Backup first!
cp data/bluesky.db data/bluesky.db.backup

# Attempt repair
docker exec bluesky-tracker sqlite3 /app/data/bluesky.db ".recover" | \
  docker exec -i bluesky-tracker sqlite3 /app/data/bluesky_recovered.db

# Test recovered database
docker exec bluesky-tracker sqlite3 /app/data/bluesky_recovered.db "SELECT COUNT(*) FROM daily_metrics;"

# If successful, replace
docker-compose stop
mv data/bluesky.db data/bluesky.db.corrupted
mv data/bluesky_recovered.db data/bluesky.db
docker-compose start
```

#### 2. Restore from Backup
```bash
# If you have backups
docker-compose stop
cp backups/bluesky-YYYYMMDD.db data/bluesky.db
docker-compose start
```

#### 3. Start Fresh
```bash
# Last resort - lose all data
docker-compose down
rm data/bluesky.db
docker-compose up -d
# Trigger first collection
curl -X POST http://localhost:8095/api/collect
```

---

## Platform-Specific Issues

### Raspberry Pi

#### Out of Memory
```bash
# Increase swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

#### SD Card Performance
```bash
# Use USB 3.0 SSD for database
# Much faster than SD card
mkdir /mnt/ssd/bluesky-data
# Move data folder to SSD
```

#### ARM Architecture Issues
```bash
# Ensure correct platform
docker pull --platform linux/arm64 costantinoai/bluesky-tracker  # Pi 4/5
docker pull --platform linux/arm/v7 costantinoai/bluesky-tracker  # Pi 3
```

### Synology NAS

#### Permission Denied
```bash
# Fix in Synology DSM:
# 1. Open Docker package
# 2. Container → Settings → Environment
# 3. Add: PUID=1000, PGID=1000
```

#### Port Conflicts
```bash
# Synology reserves many ports
# Use port above 10000
# Change to 10095 instead of 8095
```

### Unraid

#### Array Not Started
```bash
# Make sure Unraid array is started
# before starting container
```

#### AppData Location
```bash
# Use /mnt/user/appdata/bluesky-tracker
# Not /mnt/disk1 or /mnt/cache
```

---

## Getting Help

If none of these solutions work:

### 1. Gather Information

```bash
# Collect diagnostics
docker --version
docker-compose --version
docker logs bluesky-tracker > logs.txt 2>&1
docker inspect bluesky-tracker > inspect.txt
cat .env | grep -v PASSWORD > env-safe.txt

# System info
uname -a > system.txt
```

### 2. Create GitHub Issue

Include:
- Problem description
- Steps to reproduce
- Expected vs actual behavior
- Logs (without passwords!)
- System info
- Docker version

Link: https://github.com/costantinoai/bluesky-tracker/issues

### 3. Check Existing Issues

Search for similar problems:
https://github.com/costantinoai/bluesky-tracker/issues?q=

### 4. Community Help

- [GitHub Discussions](https://github.com/costantinoai/bluesky-tracker/discussions)
- Include the same diagnostic info

---

## Quick Diagnostic Script

```bash
#!/bin/bash
echo "=== Bluesky Tracker Diagnostics ==="
echo
echo "Docker Version:"
docker --version
echo
echo "Container Status:"
docker ps -a | grep bluesky-tracker
echo
echo "Container Logs (last 50 lines):"
docker logs --tail 50 bluesky-tracker
echo
echo "Health Check:"
curl -f http://localhost:8095/health 2>&1
echo
echo "Port Mapping:"
docker port bluesky-tracker 2>&1
echo
echo "Resource Usage:"
docker stats --no-stream bluesky-tracker
echo
echo "Database Info:"
ls -lh data/bluesky.db 2>&1
```

Save as `diagnose.sh`, run with `bash diagnose.sh`
