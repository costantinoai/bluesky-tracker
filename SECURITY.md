# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 3.x     | :white_check_mark: |
| < 3.0   | :x:                |

## Reporting a Vulnerability

We take the security of Bluesky Tracker seriously. If you discover a security vulnerability, please follow these steps:

### DO NOT

- ❌ Open a public GitHub issue
- ❌ Disclose the vulnerability publicly before it's been addressed
- ❌ Test the vulnerability on production systems you don't own

### DO

1. **Email the details to:** [Your security email - create one for your project]
2. **Include:**
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

3. **Expected response time:**
   - Initial response: Within 48 hours
   - Status update: Within 7 days
   - Resolution timeline: Depends on severity

## Security Best Practices

### App Password Management

#### Creating App Passwords

1. **Use dedicated app passwords**
   - Generate at: https://bsky.app/settings/app-passwords
   - Create one password per application
   - Name them descriptively (e.g., "Bluesky Tracker - Home Server")

2. **Never use your main password**
   - App passwords are scoped and can be revoked
   - They don't give full account access
   - Safer than sharing your main password

3. **Rotate regularly**
   - Change app passwords every 90 days
   - Revoke passwords you're not using
   - Create new passwords after suspected compromise

#### Storing App Passwords

1. **Environment variables (.env file)**
   ```bash
   # Store in .env file (never commit to git)
   BLUESKY_APP_PASSWORD=your-app-password-here
   ```

2. **File permissions**
   ```bash
   chmod 600 .env  # Only owner can read/write
   ```

3. **Docker secrets (advanced)**
   ```yaml
   # docker-compose.yml with secrets
   secrets:
     bluesky_password:
       file: ./secrets/bluesky_password.txt
   services:
     bluesky-tracker:
       secrets:
         - bluesky_password
   ```

### Docker Security

#### Container Security Features

The official image includes:

1. **Non-root user**
   - Runs as `appuser` (UID 1000)
   - Never runs as root inside container
   - Reduces impact of container escapes

2. **Read-only root filesystem (optional)**
   ```yaml
   services:
     bluesky-tracker:
       read_only: true
       tmpfs:
         - /tmp
   ```

3. **No new privileges**
   ```yaml
   services:
     bluesky-tracker:
       security_opt:
         - no-new-privileges:true
   ```

4. **Resource limits**
   ```yaml
   deploy:
     resources:
       limits:
         memory: 256M
         cpus: '0.5'
   ```

#### Docker Best Practices

1. **Keep Docker updated**
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt upgrade docker-ce
   ```

2. **Use specific image tags**
   ```yaml
   # Good
   image: costantinoai/bluesky-tracker:3.1.0

   # Avoid (less predictable)
   image: costantinoai/bluesky-tracker:latest
   ```

3. **Scan images for vulnerabilities**
   ```bash
   docker scan costantinoai/bluesky-tracker:latest
   ```

### Network Security

#### Reverse Proxy with TLS

For public-facing deployments, use a reverse proxy with HTTPS:

**Recommended proxies:**
- [Traefik](examples/deployments/docker-compose.traefik.yml)
- [Caddy](examples/deployments/docker-compose.caddy.yml)
- Nginx Proxy Manager
- SWAG (Secure Web Application Gateway)

**Benefits:**
- Encrypted traffic (TLS/SSL)
- Automatic certificate management (Let's Encrypt)
- Rate limiting
- DDoS protection
- IP whitelisting

#### Firewall Configuration

**Only expose necessary ports:**

```bash
# Allow only reverse proxy access (if using one)
sudo ufw allow from 172.18.0.0/16 to any port 8095

# Or allow from specific IP
sudo ufw allow from 192.168.1.100 to any port 8095
```

**Don't expose directly to internet:**
```yaml
# Bind to localhost only
ports:
  - "127.0.0.1:8095:8095"
```

#### Rate Limiting

Implement at reverse proxy level:

**Traefik example:**
```yaml
labels:
  - "traefik.http.middlewares.ratelimit.ratelimit.average=10"
  - "traefik.http.middlewares.ratelimit.ratelimit.burst=20"
```

### Database Security

#### Backup Strategy

1. **Regular backups**
   ```bash
   # Backup script
   cp data/bluesky.db "backups/bluesky-$(date +%Y%m%d).db"
   ```

2. **Encrypted backups**
   ```bash
   # Encrypt with GPG
   gpg --symmetric --cipher-algo AES256 data/bluesky.db
   ```

3. **Off-site storage**
   - Store backups on different physical location
   - Use cloud storage with encryption
   - Test restore procedures regularly

#### File Permissions

```bash
# Secure the data directory
chmod 700 data/
chmod 600 data/bluesky.db
```

### Monitoring & Alerting

#### Security Monitoring

1. **Container health**
   ```bash
   # Check for unexpected restarts
   docker ps -a --filter "status=exited"
   ```

2. **Log monitoring**
   ```bash
   # Watch for authentication failures
   docker logs bluesky-tracker | grep -i "authentication failed"
   ```

3. **Resource usage**
   ```bash
   # Detect anomalies
   docker stats bluesky-tracker
   ```

#### Automated Security Updates

**Dependabot** (already configured):
- Automatically checks for dependency updates
- Creates PRs for security patches
- Configured for pip, Docker, and GitHub Actions

**Watchtower** (auto-update containers):
```yaml
services:
  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 86400  # Check daily
```

### Incident Response

#### If Compromised

1. **Immediate actions:**
   ```bash
   # Stop the container
   docker stop bluesky-tracker

   # Revoke app password immediately
   # Go to: https://bsky.app/settings/app-passwords
   ```

2. **Investigation:**
   ```bash
   # Check logs
   docker logs bluesky-tracker > incident-logs.txt

   # Check for unauthorized access
   grep "POST /api/collect" incident-logs.txt
   ```

3. **Recovery:**
   - Generate new app password
   - Update .env file
   - Review all account activity
   - Check for unexpected follows/unfollows
   - Restart with new credentials

### Supply Chain Security

#### Image Verification

1. **Verify image signatures** (when available)
   ```bash
   docker trust inspect costantinoai/bluesky-tracker:latest
   ```

2. **Check image source**
   - Official images: `costantinoai/bluesky-tracker`
   - Source code: https://github.com/costantinoai/bluesky-tracker
   - Build process: GitHub Actions (public audit trail)

3. **Multi-architecture support**
   - All platforms built from same source
   - Automated builds (no manual intervention)
   - Reproducible builds

#### Dependency Management

- **Automated security scanning** (Bandit)
- **Vulnerability detection** (Dependabot)
- **Minimal dependencies** (reduce attack surface)
- **Pinned versions** (reproducible builds)

### Compliance & Privacy

#### Data Handling

1. **Local-only storage**
   - All data stored in your SQLite database
   - No external data transmission (except to Bluesky API)
   - No analytics or tracking

2. **GDPR compliance**
   - You control all data
   - Easy to delete (just remove database)
   - No third-party processors

3. **Data retention**
   - Historical data kept locally
   - You can purge old data anytime
   - No automatic external backups

### Security Checklist

- [ ] Using app passwords (not main password)
- [ ] .env file not committed to git
- [ ] File permissions set correctly (600 for .env)
- [ ] Running as non-root user in container
- [ ] Resource limits configured
- [ ] Using reverse proxy with TLS for public access
- [ ] Firewall rules configured
- [ ] Regular backups enabled
- [ ] Monitoring and alerting set up
- [ ] Using specific image tags (not latest)
- [ ] Regular security updates applied

---

## Additional Resources

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)

---

## Questions?

For security-related questions that aren't vulnerabilities:
- [GitHub Discussions](https://github.com/costantinoai/bluesky-tracker/discussions)
- [Issues](https://github.com/costantinoai/bluesky-tracker/issues)
