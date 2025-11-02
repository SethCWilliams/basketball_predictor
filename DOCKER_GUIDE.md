# NBA Stats Tracker - Docker Guide

## Quick Start

### Prerequisites
- Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop))
- Ports 8000 and 5173 available

### Start Everything
```bash
# From project root
docker-compose up

# Or run in background
docker-compose up -d
```

**Services:**
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173 (when implemented)

## Initial Setup

### 1. Populate Teams
```bash
curl -X POST "http://localhost:8000/api/admin/teams/populate"
```

Response:
```json
{
  "status": "success",
  "teams_added": 30,
  "message": "Successfully populated 30 NBA teams"
}
```

### 2. Check System Status
```bash
curl "http://localhost:8000/api/admin/players/scrape-status"
```

### 3. Search for Players
```bash
curl "http://localhost:8000/api/players/search?q=curry"
```

## Helper Scripts

### Check Ports
```bash
./scripts/check-ports.sh
```

Shows what's running on ports 8000, 5173, and 5432.

### Reset Database
```bash
./scripts/reset-db.sh
```

**Warning:** Deletes all cached player data. You'll need to re-scrape.

## Common Commands

### View Logs
```bash
# All logs
docker-compose logs

# Backend only
docker-compose logs backend

# Follow logs in real-time
docker-compose logs -f backend
```

### Restart Services
```bash
# Restart everything
docker-compose restart

# Restart backend only
docker-compose restart backend
```

### Stop Everything
```bash
docker-compose down

# Also remove volumes (resets database)
docker-compose down -v
```

### Rebuild After Code Changes
```bash
# Rebuild images
docker-compose build

# Rebuild and restart
docker-compose up --build
```

## Development

### Hot Reload
Both backend and frontend support hot reload - code changes are reflected immediately without rebuilding.

**Backend (Python):**
- Mount: `./backend:/app`
- Uvicorn `--reload` flag enabled
- Changes apply instantly

**Frontend (Node):**
- Mount: `./frontend:/app`
- Vite HMR enabled
- Changes apply instantly

### Accessing Containers
```bash
# Backend shell
docker exec -it nba_tracker_backend bash

# Run Python in backend
docker exec nba_tracker_backend python -c "print('Hello')"

# Check Python packages
docker exec nba_tracker_backend pip list
```

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the ports
./scripts/check-ports.sh

# Kill processes on port 8000
lsof -ti:8000 | xargs kill -9

# Or kill all at once
lsof -ti:8000,5173 | xargs kill -9
```

### Container Won't Start
```bash
# Check container status
docker-compose ps

# View error logs
docker-compose logs backend

# Remove everything and start fresh
docker-compose down -v
docker-compose up --build
```

### Database Issues
```bash
# Reset database completely
./scripts/reset-db.sh

# Or manually
docker-compose down
docker volume rm basketball_predictor_nba_db_data
docker-compose up
```

### Code Changes Not Reflected
```bash
# Restart with rebuild
docker-compose up --build

# Or force recreate
docker-compose up --force-recreate
```

## Architecture

### Container Structure
```
┌─────────────────────────────────────────┐
│  Docker Compose Orchestration           │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │   Backend    │  │   Frontend   │   │
│  │   FastAPI    │  │  SvelteKit   │   │
│  │  Python 3.12 │  │   Node 20    │   │
│  │  Port: 8000  │  │  Port: 5173  │   │
│  └──────┬───────┘  └──────────────┘   │
│         │                              │
│         │                              │
│  ┌──────▼───────────┐                 │
│  │  SQLite Database │                 │
│  │  (Docker Volume) │                 │
│  └──────────────────┘                 │
└─────────────────────────────────────────┘
```

### Data Persistence
- Database stored in named Docker volume: `basketball_predictor_nba_db_data`
- Persists across container restarts
- Only deleted with `docker-compose down -v`

### Networks
- Custom bridge network: `nba_network`
- Allows containers to communicate by service name
- Backend: `http://backend:8000`

## Environment Variables

Create `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

Key variables:
```bash
# Database
DATABASE_URL=sqlite:///./nba_predictions.db

# API
VITE_API_URL=http://localhost:8000

# Python
PYTHONUNBUFFERED=1
```

## Production Deployment

### Build Production Images
```bash
# Backend
docker build -t nba-backend:latest ./backend

# Frontend
docker build -t nba-frontend:latest ./frontend
```

### Deploy to Railway/Render
1. Push code to GitHub
2. Connect repository to Railway/Render
3. Set environment variables
4. Deploy automatically

## Health Checks

### Backend Health
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "stats": {
    "players_cached": 0,
    "game_logs_stored": 0
  }
}
```

### Container Health
```bash
docker-compose ps
```

Shows health status for each container.

## Performance

### Docker on macOS
- Uses Orbstack or Docker Desktop
- Volume mounts can be slower than native
- Database performance is good with SQLite

### Optimization Tips
1. Use `.dockerignore` to exclude unnecessary files
2. Layer caching speeds up rebuilds
3. Named volumes are faster than bind mounts
4. Limit memory if needed: `mem_limit: 1g`

## Next Steps

1. Populate teams: `curl -X POST http://localhost:8000/api/admin/teams/populate`
2. Search for players to test API
3. Implement bulk player scraping
4. Build frontend player detail page

---

**Need Help?**
- Check logs: `docker-compose logs -f`
- View status: `docker-compose ps`
- Reset everything: `docker-compose down -v && docker-compose up`
