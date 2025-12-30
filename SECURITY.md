# Security

## Reporting Vulnerabilities

If you discover a security vulnerability:

1. **DO NOT** open a public GitHub issue
2. Email details to: [create a security email for your project]
3. Include: description, steps to reproduce, potential impact

Expected response: within 48 hours

---

## App Password Security

### Creating App Passwords

**Required:** You must use a Bluesky app password (not your main password)

1. Generate at: https://bsky.app/settings/app-passwords
2. Name it descriptively (e.g., "Bluesky Tracker")
3. Store in `.env` file (never commit to git)

### Storing Safely

```bash
# .env file (already in .gitignore)
BLUESKY_APP_PASSWORD=your-app-password-here

# Set correct permissions
chmod 600 .env
```

### Best Practices

- Use one app password per application
- Revoke unused passwords
- Rotate every 90 days
- Never share your main Bluesky password

### If Compromised

1. Revoke app password immediately: https://bsky.app/settings/app-passwords
2. Generate new password
3. Update `.env` file
4. Restart container: `docker restart bluesky-tracker`

---

## Docker Security

### Built-in Features

The Docker image includes:
- Non-root user (runs as `appuser`, UID 1000)
- Minimal attack surface (Alpine Linux base)
- No unnecessary packages

### Recommended Settings

Add to your `docker-compose.yml`:

```yaml
services:
  bluesky-tracker:
    # ... other settings ...

    # Security options
    security_opt:
      - no-new-privileges:true

    # Resource limits
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.5'

    # Health monitoring
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8095/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Keep Updated

```bash
# Pull latest image
docker pull ghcr.io/costantinoai/bluesky-tracker:latest

# Restart with new image
docker compose down && docker compose up -d
```

---

## Network Security

### Local Use Only

If only accessing locally, bind to localhost:

```yaml
# docker-compose.yml
ports:
  - "127.0.0.1:8095:8095"  # Only accessible from this machine
```

### Public Access (HTTPS Required)

For external access, use a reverse proxy with automatic HTTPS:

**Recommended:**
- [Caddy](examples/deployments/docker-compose.caddy.yml) - Zero config HTTPS
- [Traefik](examples/deployments/docker-compose.traefik.yml) - Automatic Let's Encrypt

**Never expose port 8095 directly to the internet without HTTPS**

---

## Data Security

### File Permissions

```bash
# Secure data directory
chmod 700 data/
chmod 600 data/bluesky.db
```

### Backups

Regular backups recommended (database contains all historical data):

```bash
# Simple backup
cp data/bluesky.db "backups/bluesky-$(date +%Y%m%d).db"

# Encrypted backup
gpg --symmetric --cipher-algo AES256 data/bluesky.db
```

### Privacy

- All data stored locally in SQLite
- No external services (except Bluesky API)
- No analytics or tracking
- Delete database to remove all data

---

## Security Checklist

Before running in production:

- [ ] Using app password (not main password)
- [ ] `.env` file has correct permissions (`chmod 600 .env`)
- [ ] `.env` not committed to git (check `.gitignore`)
- [ ] Resource limits configured (memory, CPU)
- [ ] Using HTTPS if accessible from internet
- [ ] Regular backups enabled
- [ ] Firewall configured (if applicable)
- [ ] Container set to auto-restart (`restart: unless-stopped`)

---

## Questions?

For non-vulnerability security questions:
- [GitHub Discussions](https://github.com/costantinoai/bluesky-tracker/discussions)
- [GitHub Issues](https://github.com/costantinoai/bluesky-tracker/issues)
