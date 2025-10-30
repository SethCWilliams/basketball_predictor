from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, Dict
from database import get_db, engine, Base
import models
from services.player_service import PlayerService
from services.scraper_service import ScraperService
from utils import get_current_season_year, season_display_name

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NBA Stats Tracker API",
    description="PropsMadness-style NBA player stats tracking with smart caching",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """API health check"""
    current_season = get_current_season_year()
    return {
        "message": "NBA Stats Tracker API",
        "status": "running",
        "version": "1.0.0",
        "current_season": season_display_name(current_season),
        "season_end_year": current_season
    }


@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    """Check database connection"""
    try:
        # Simple query to check DB
        player_count = db.query(models.Player).count()
        game_log_count = db.query(models.GameLog).count()

        return {
            "status": "healthy",
            "database": "connected",
            "stats": {
                "players_cached": player_count,
                "game_logs_stored": game_log_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/games/today")
def get_today_games(
    timezone: Optional[str] = Query(default=None, description="IANA timezone (e.g., 'America/New_York'). Defaults to EST."),
    db: Session = Depends(get_db)
):
    """
    Get today's NBA games.
    Times are converted from UTC to the specified timezone (defaults to EST).
    """
    try:
        scraper = ScraperService(db, timezone=timezone)
        games = scraper.scrape_today_schedule()

        return {
            "date": "today",
            "count": len(games),
            "timezone": timezone or "America/New_York (default)",
            "games": [
                {
                    "id": g.id,
                    "date": g.game_date.isoformat(),
                    "home_team": g.home_team,
                    "away_team": g.away_team,
                    "start_time": g.start_time,
                    "status": g.game_status
                }
                for g in games
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schedule: {str(e)}")


@app.get("/api/players/{player_slug}")
def get_player(player_slug: str, db: Session = Depends(get_db)):
    """Get player info (triggers smart caching if needed)"""
    try:
        service = PlayerService(db)
        player = service.get_player_by_slug(player_slug)

        return {
            "slug": player.player_slug,
            "name": player.full_name,
            "position": player.position,
            "team": player.current_team,
            "is_active": player.is_active,
            "career_scraped": player.career_scraped,
            "last_updated": player.last_scraped_at.isoformat() if player.last_scraped_at else None,
            "last_game_date": player.last_game_date.isoformat() if player.last_game_date else None
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching player: {str(e)}")


@app.get("/api/players/search")
def search_players(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    """Search for players by name"""
    try:
        service = PlayerService(db)
        results = service.search_players(q)

        return {
            "query": q,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching players: {str(e)}")


@app.get("/api/players/{player_slug}/stats")
def get_player_stats(
    player_slug: str,
    stat_category: str = Query(default="points", description="Stat category to analyze"),
    games: int = Query(default=15, ge=1, le=82, description="Number of recent games"),
    season: Optional[int] = Query(default=None, description="Filter by season"),
    opponent: Optional[str] = Query(default=None, description="Filter by opponent"),
    is_home: Optional[bool] = Query(default=None, description="Filter by home/away"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive player stats for the chart view.
    Includes: season avg, graph avg, recent games, and chart data.
    """
    try:
        service = PlayerService(db)
        player = service.get_player_by_slug(player_slug)

        # Build filters
        filters = {}
        if season:
            filters['season'] = season
        if opponent:
            filters['opponent'] = opponent.upper()
        if is_home is not None:
            filters['is_home'] = is_home

        # Get season average
        current_season = season or 2025
        season_avg = service.get_season_average(player_slug, current_season, stat_category)

        # Get graph average (for displayed games only)
        graph_avg = service.get_graph_average(player_slug, stat_category, games, filters)

        # Get chart data
        chart_data = service.get_player_chart_data(player_slug, stat_category, games, filters)

        return {
            "player": {
                "slug": player.player_slug,
                "name": player.full_name,
                "position": player.position,
                "team": player.current_team
            },
            "stat_category": stat_category,
            "season_average": season_avg['average'],
            "graph_average": graph_avg['average'],
            "chart": chart_data
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@app.get("/api/players/{player_slug}/hit-rate")
def get_hit_rate(
    player_slug: str,
    stat_category: str = Query(default="points", description="Stat category"),
    line: float = Query(..., description="Betting line value"),
    games: int = Query(default=15, ge=1, le=82, description="Number of recent games"),
    season: Optional[int] = Query(default=None, description="Filter by season"),
    opponent: Optional[str] = Query(default=None, description="Filter by opponent"),
    is_home: Optional[bool] = Query(default=None, description="Filter by home/away"),
    db: Session = Depends(get_db)
):
    """
    Calculate hit rate for a given line value.
    Returns percentage and count of games where player went OVER the line.
    """
    try:
        service = PlayerService(db)

        # Build filters
        filters = {}
        if season:
            filters['season'] = season
        if opponent:
            filters['opponent'] = opponent.upper()
        if is_home is not None:
            filters['is_home'] = is_home

        hit_rate = service.calculate_hit_rate(player_slug, stat_category, line, games, filters)

        return hit_rate
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating hit rate: {str(e)}")


@app.get("/api/players/{player_slug}/recent")
def get_player_recent_games(
    player_slug: str,
    games: int = Query(default=10, ge=1, le=82),
    db: Session = Depends(get_db)
):
    """Get recent games for a player"""
    try:
        service = PlayerService(db)
        recent = service.get_recent_games(player_slug, games)

        return {
            "player_slug": player_slug,
            "count": len(recent),
            "games": [
                {
                    "date": g.game_date.isoformat(),
                    "opponent": g.opponent,
                    "is_home": g.is_home_game,
                    "points": g.points,
                    "rebounds": g.rebounds,
                    "assists": g.assists,
                    "minutes": float(g.minutes_played) if g.minutes_played else 0.0,
                    "game_result": g.game_result
                }
                for g in recent
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent games: {str(e)}")


@app.get("/api/stats/categories")
def get_stat_categories():
    """Get all available stat categories (for the top navigation)"""
    return {
        "categories": [
            {"id": "points", "name": "Points", "short": "PTS"},
            {"id": "assists", "name": "Assists", "short": "AST"},
            {"id": "rebounds", "name": "Rebounds", "short": "REB"},
            {"id": "threes", "name": "Threes", "short": "3PM"},
            {"id": "pts_ast", "name": "Pts+Ast", "short": "P+A"},
            {"id": "pts_reb", "name": "Pts+Reb", "short": "P+R"},
            {"id": "reb_ast", "name": "Reb+Ast", "short": "R+A"},
            {"id": "pts_reb_ast", "name": "Pts+Reb+Ast", "short": "P+R+A"},
            {"id": "double_double", "name": "Double Double", "short": "DD"},
            {"id": "triple_double", "name": "Triple Double", "short": "TD"},
            {"id": "1q_points", "name": "1Q Points", "short": "1Q PTS"},
            {"id": "1q_assists", "name": "1Q Assists", "short": "1Q AST"},
            {"id": "1q_rebounds", "name": "1Q Rebounds", "short": "1Q REB"},
            {"id": "steals", "name": "Steals", "short": "STL"},
            {"id": "blocks", "name": "Blocks", "short": "BLK"},
            {"id": "stl_blk", "name": "Stl+Blk", "short": "S+B"},
            {"id": "turnovers", "name": "Turnovers", "short": "TO"},
            {"id": "fouls", "name": "Fouls", "short": "PF"},
            {"id": "ft_attempted", "name": "FT Attempted", "short": "FTA"},
        ]
    }


@app.get("/api/debug/scraping-log")
def get_scraping_log(limit: int = Query(default=20, le=100), db: Session = Depends(get_db)):
    """Get recent scraping activity (for debugging)"""
    try:
        logs = db.query(models.ScrapingLog).order_by(
            models.ScrapingLog.scraped_at.desc()
        ).limit(limit).all()

        return {
            "count": len(logs),
            "logs": [
                {
                    "entity_type": log.entity_type,
                    "entity_id": log.entity_id,
                    "scrape_type": log.scrape_type,
                    "games_scraped": log.games_scraped,
                    "status": log.status,
                    "duration": log.duration_seconds,
                    "error": log.error_message,
                    "timestamp": log.scraped_at.isoformat()
                }
                for log in logs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching logs: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
