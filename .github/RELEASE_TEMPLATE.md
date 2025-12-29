## Docker Images

**Docker Hub (Recommended):**
```bash
docker pull costantinoai/bluesky-tracker:VERSION
docker pull costantinoai/bluesky-tracker:latest
```

**GitHub Container Registry:**
```bash
docker pull ghcr.io/costantinoai/bluesky-tracker:VERSION
```

**Supported Platforms:**
- linux/amd64 (Intel/AMD servers, Intel Macs)
- linux/arm64 (ARM servers, M1/M2 Macs, Raspberry Pi 4/5)
- linux/arm/v7 (Raspberry Pi 3 and older)

---

## What's Changed

<!-- Auto-generated changelog will be inserted here -->

### Features
-

### Bug Fixes
-

### Documentation
-

### Miscellaneous
-

---

## Breaking Changes

<!-- List any breaking changes here -->

None

---

## Quick Start

### One-Command Setup
```bash
curl -sSL https://raw.githubusercontent.com/costantinoai/bluesky-tracker/main/setup.sh | bash
```

### Docker Compose
```bash
curl -O https://raw.githubusercontent.com/costantinoai/bluesky-tracker/main/docker-compose.selfhost.yml
mv docker-compose.selfhost.yml docker-compose.yml
curl -O https://raw.githubusercontent.com/costantinoai/bluesky-tracker/main/.env.example
cp .env.example .env
# Edit .env with your Bluesky credentials
docker compose up -d
```

---

## Upgrading

### From Previous Version

**Docker Compose:**
```bash
docker compose pull
docker compose up -d
```

**Docker Run:**
```bash
docker pull costantinoai/bluesky-tracker:VERSION
docker stop bluesky-tracker
docker rm bluesky-tracker
# Re-run docker run command with new version
```

---

## Documentation

- [Installation Guide](INSTALLATION.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Security](SECURITY.md)
- [README](README.md)

---

## Contributors

Thanks to all contributors who made this release possible!

**Full Changelog**: https://github.com/costantinoai/bluesky-tracker/compare/PREVIOUS_TAG...CURRENT_TAG
