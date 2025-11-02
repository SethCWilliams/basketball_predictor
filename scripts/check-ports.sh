#!/bin/bash

# NBA Stats Tracker - Port Checker
# Checks what's running on common ports used by the application

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ports to check
BACKEND_PORT=8000
FRONTEND_PORT=5173
POSTGRES_PORT=5432

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}NBA Stats Tracker - Port Status${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Function to check a port
check_port() {
    local port=$1
    local name=$2

    echo -e "${YELLOW}Checking port ${port} (${name})...${NC}"

    # Check if port is in use (macOS/Linux compatible)
    if command -v lsof &> /dev/null; then
        local pid_info=$(lsof -iTCP:$port -sTCP:LISTEN -n -P 2>/dev/null | grep LISTEN)

        if [ -n "$pid_info" ]; then
            echo -e "${RED}  ✗ Port ${port} is IN USE${NC}"
            echo "$pid_info" | while IFS= read -r line; do
                echo "    $line"
            done
            echo ""
            return 1
        else
            echo -e "${GREEN}  ✓ Port ${port} is AVAILABLE${NC}"
            echo ""
            return 0
        fi
    else
        echo -e "${YELLOW}  ⚠ lsof command not found - cannot check port${NC}"
        echo ""
        return 2
    fi
}

# Check all ports
check_port $BACKEND_PORT "Backend/FastAPI"
backend_status=$?

check_port $FRONTEND_PORT "Frontend/Vite"
frontend_status=$?

check_port $POSTGRES_PORT "PostgreSQL"
postgres_status=$?

# Summary
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}================================${NC}"

if [ $backend_status -eq 0 ] && [ $frontend_status -eq 0 ]; then
    echo -e "${GREEN}✓ All ports available - ready to start Docker containers${NC}"
elif [ $backend_status -eq 1 ] || [ $frontend_status -eq 1 ]; then
    echo -e "${RED}✗ Some ports are in use${NC}"
    echo ""
    echo "To kill processes on these ports:"
    [ $backend_status -eq 1 ] && echo "  lsof -ti:$BACKEND_PORT | xargs kill -9"
    [ $frontend_status -eq 1 ] && echo "  lsof -ti:$FRONTEND_PORT | xargs kill -9"
    [ $postgres_status -eq 1 ] && echo "  lsof -ti:$POSTGRES_PORT | xargs kill -9"
    echo ""
    echo "Or kill all at once:"
    echo "  lsof -ti:$BACKEND_PORT,$FRONTEND_PORT | xargs kill -9"
fi

echo -e "${BLUE}================================${NC}"
