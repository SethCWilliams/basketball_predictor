#!/bin/bash

# NBA Stats Tracker - Database Reset Script
# Safely stops containers and resets the database

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}NBA Stats Tracker - DB Reset${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Confirmation prompt
echo -e "${YELLOW}⚠️  WARNING: This will delete all cached player data and game logs!${NC}"
echo -e "${YELLOW}You will need to re-scrape data for players.${NC}"
echo ""
read -p "Are you sure you want to reset the database? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${GREEN}Reset cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Step 1: Stopping Docker containers...${NC}"
docker-compose down

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Containers stopped${NC}"
else
    echo -e "${RED}✗ Failed to stop containers${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Step 2: Removing database volume...${NC}"
docker volume rm basketball_predictor_nba_db_data 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database volume removed${NC}"
else
    echo -e "${YELLOW}⚠ Volume may not exist or already removed${NC}"
fi

echo ""
echo -e "${BLUE}Step 3: Removing local database file (if exists)...${NC}"
if [ -f "backend/nba_predictions.db" ]; then
    rm backend/nba_predictions.db
    rm backend/nba_predictions.db-shm 2>/dev/null
    rm backend/nba_predictions.db-wal 2>/dev/null
    echo -e "${GREEN}✓ Local database files removed${NC}"
else
    echo -e "${YELLOW}⚠ No local database file found${NC}"
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✓ Database reset complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "To start fresh:"
echo "  docker-compose up"
echo ""
echo "The database will be recreated automatically."
echo -e "${BLUE}================================${NC}"
