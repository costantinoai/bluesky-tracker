#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "  ____  _                 _            _______             _             "
echo " |  _ \| |               | |          |__   __|           | |            "
echo " | |_) | |_   _  ___  ___| | ___   _     | |_ __ __ _  ___| | _____ _ __ "
echo " |  _ <| | | | |/ _ \/ __| |/ / | | |    | | '__/ _\` |/ __| |/ / _ \ '__|"
echo " | |_) | | |_| |  __/\__ \   <| |_| |    | | | | (_| | (__|   <  __/ |   "
echo " |____/|_|\__,_|\___||___/_|\_\\__, |    |_|_|  \__,_|\___|_|\_\___|_|   "
echo "                                __/ |                                     "
echo "                               |___/                                      "
echo -e "${NC}"
echo -e "${GREEN}Self-Host Setup Script${NC}"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
   echo -e "${YELLOW}Warning: Running as root. Consider running as a regular user.${NC}"
   echo ""
fi

# Check Docker installation
echo -e "${BLUE}[1/6]${NC} Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found${NC}"
    echo ""
    echo "Please install Docker first:"
    echo "  Ubuntu/Debian: https://docs.docker.com/engine/install/ubuntu/"
    echo "  Raspberry Pi:  https://docs.docker.com/engine/install/debian/"
    echo "  macOS:         https://docs.docker.com/desktop/mac/install/"
    echo "  Windows:       https://docs.docker.com/desktop/windows/install/"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed${NC}"
docker --version
echo ""

# Check Docker Compose
echo -e "${BLUE}[2/6]${NC} Checking Docker Compose..."
if ! docker compose version &> /dev/null; then
    echo -e "${YELLOW}⚠ Docker Compose (v2) not found, checking for docker-compose...${NC}"
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}✗ Docker Compose not found${NC}"
        echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

echo -e "${GREEN}✓ Docker Compose is installed${NC}"
$COMPOSE_CMD version
echo ""

# Create installation directory
INSTALL_DIR="$HOME/bluesky-tracker"
echo -e "${BLUE}[3/6]${NC} Setting up installation directory..."
echo "Installation path: ${INSTALL_DIR}"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠ Directory already exists${NC}"
    read -p "Overwrite existing installation? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    echo "Backing up existing .env file if present..."
    [ -f "$INSTALL_DIR/.env" ] && cp "$INSTALL_DIR/.env" "$INSTALL_DIR/.env.backup"
fi

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"
echo -e "${GREEN}✓ Directory ready${NC}"
echo ""

# Download configuration files
echo -e "${BLUE}[4/6]${NC} Downloading configuration files..."

# Download docker-compose.yml
echo "  → docker-compose.yml"
curl -fsSL -o docker-compose.yml https://raw.githubusercontent.com/costantinoai/bluesky-tracker/main/docker-compose.selfhost.yml
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to download docker-compose.yml${NC}"
    exit 1
fi

# Download .env.example
echo "  → .env.example"
curl -fsSL -o .env.example https://raw.githubusercontent.com/costantinoai/bluesky-tracker/main/.env.example
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to download .env.example${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Files downloaded${NC}"
echo ""

# Configure environment
echo -e "${BLUE}[5/6]${NC} Configuring environment..."

if [ -f ".env" ]; then
    echo -e "${GREEN}✓ Using existing .env file${NC}"
else
    cp .env.example .env
    echo "Please provide your Bluesky credentials:"
    echo ""

    # Get Bluesky handle
    while true; do
        read -p "Bluesky handle (e.g., yourname.bsky.social): " HANDLE
        if [ -n "$HANDLE" ]; then
            break
        fi
        echo -e "${RED}Handle cannot be empty${NC}"
    done

    echo ""
    echo "To create an app password:"
    echo "  1. Go to https://bsky.app/settings/app-passwords"
    echo "  2. Click 'Add App Password'"
    echo "  3. Name it 'Bluesky Tracker'"
    echo "  4. Copy the generated password"
    echo ""

    # Get app password
    while true; do
        read -sp "Bluesky app password: " PASSWORD
        echo ""
        if [ -n "$PASSWORD" ]; then
            break
        fi
        echo -e "${RED}Password cannot be empty${NC}"
    done

    # Update .env file
    sed -i.bak "s|BLUESKY_HANDLE=.*|BLUESKY_HANDLE=${HANDLE}|g" .env
    sed -i.bak "s|BLUESKY_APP_PASSWORD=.*|BLUESKY_APP_PASSWORD=${PASSWORD}|g" .env
    rm -f .env.bak

    echo -e "${GREEN}✓ Configuration saved${NC}"
fi

# Create data directory
mkdir -p data
echo ""

# Pull and start
echo -e "${BLUE}[6/6]${NC} Starting Bluesky Tracker..."
echo "Pulling latest Docker image..."
$COMPOSE_CMD pull

echo ""
echo "Starting container..."
$COMPOSE_CMD up -d

echo ""
echo "Waiting for service to be healthy..."
sleep 10

# Check if container is running
if $COMPOSE_CMD ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Bluesky Tracker is running!${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}✓ Setup Complete!${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Access your dashboard:"
    echo -e "  ${BLUE}→ Dashboard:${NC} http://localhost:8095/report"
    echo -e "  ${BLUE}→ API Stats:${NC} http://localhost:8095/api/stats"
    echo -e "  ${BLUE}→ Metrics:${NC}   http://localhost:8095/metrics"
    echo ""
    echo "Useful commands:"
    echo "  View logs:    $COMPOSE_CMD logs -f"
    echo "  Stop:         $COMPOSE_CMD stop"
    echo "  Restart:      $COMPOSE_CMD restart"
    echo "  Update:       $COMPOSE_CMD pull && $COMPOSE_CMD up -d"
    echo "  Uninstall:    $COMPOSE_CMD down -v"
    echo ""
    echo "Installation directory: ${INSTALL_DIR}"
    echo ""
    echo "First data collection will run at 06:00 AM (Europe/Brussels)"
    echo "To collect data now: curl -X POST http://localhost:8095/api/collect"
    echo ""
else
    echo -e "${RED}✗ Container failed to start${NC}"
    echo ""
    echo "Check logs with: $COMPOSE_CMD logs"
    echo ""
    exit 1
fi
