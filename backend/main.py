from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, Dict
from database import get_db, engine, Base
import models
from services.player_service import PlayerService
from services.scraper_service import ScraperService
from utils import get_current_season_year, season_display_name, validate_season, get_allowed_seasons
from routers import admin

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NBA Stats Tracker API",
    description="PropsMadness-style NBA player stats tracking with smart caching",
    version="1.0.0"
)

# Include routers
app.include_router(admin.router)

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
                    "status": g.game_status,
                    "home_score": g.home_score,
                    "away_score": g.away_score
                }
                for g in games
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schedule: {str(e)}")


@app.get("/api/games/date/{date}")
def get_games_by_date(
    date: str,
    timezone: Optional[str] = Query(default=None, description="IANA timezone (e.g., 'America/New_York'). Defaults to EST."),
    db: Session = Depends(get_db)
):
    """
    Get NBA games for a specific date.
    Date format: YYYY-MM-DD (e.g., '2025-10-29')
    Times are converted from UTC to the specified timezone (defaults to EST).
    """
    try:
        scraper = ScraperService(db, timezone=timezone)
        games = scraper.scrape_schedule_by_date(date)

        return {
            "date": date,
            "count": len(games),
            "timezone": timezone or "America/New_York (default)",
            "games": [
                {
                    "id": g.id,
                    "date": g.game_date.isoformat(),
                    "home_team": g.home_team,
                    "away_team": g.away_team,
                    "start_time": g.start_time,
                    "status": g.game_status,
                    "home_score": g.home_score,
                    "away_score": g.away_score
                }
                for g in games
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schedule: {str(e)}")


@app.post("/api/games/season/populate")
def populate_season_schedule(
    season: Optional[int] = Query(default=None, description="Season end year (e.g., 2026 for 2025-26). Defaults to current season."),
    timezone: Optional[str] = Query(default=None, description="IANA timezone. Defaults to EST."),
    db: Session = Depends(get_db)
):
    """
    Bulk populate the games table with an entire season's schedule.
    Only allows current season + 2 previous seasons.

    This will scrape all ~1200 games for the season and store them in the database.
    Games already in the database will be updated with fresh data.

    Example: POST /api/games/season/populate?season=2026
    """
    try:
        # Validate season (will raise ValueError if outside allowed range)
        season_year = validate_season(season)

        scraper = ScraperService(db, timezone=timezone)

        # Use the specified season instead of scraper's default current season
        original_season = scraper.current_season
        scraper.current_season = season_year

        summary = scraper.scrape_full_season_schedule(season_year)

        # Restore original season
        scraper.current_season = original_season

        return {
            "season": season_display_name(season_year),
            "season_end_year": season_year,
            "summary": summary,
            "allowed_seasons": [season_display_name(s) for s in get_allowed_seasons()]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error populating season schedule: {str(e)}")


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


@app.get("/api/players/{player_slug}/stats")
def get_player_stats(
    player_slug: str,
    stat_category: str = Query(default="points", description="Stat category to analyze"),
    games: int = Query(default=15, ge=1, le=82, description="Number of recent games"),
    season: Optional[int] = Query(default=None, description="Season end year (e.g., 2026). Only current + 2 previous seasons allowed."),
    opponent: Optional[str] = Query(default=None, description="Filter by opponent"),
    is_home: Optional[bool] = Query(default=None, description="Filter by home/away"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive player stats for the chart view.
    Includes: season avg, graph avg, recent games, and chart data.
    Only supports current season + 2 previous seasons.
    """
    try:
        # Validate season
        season_year = validate_season(season)

        service = PlayerService(db)
        player = service.get_player_by_slug(player_slug)

        # Build filters
        filters = {}
        filters['season'] = season_year
        if opponent:
            filters['opponent'] = opponent.upper()
        if is_home is not None:
            filters['is_home'] = is_home

        # Get season average
        season_avg = service.get_season_average(player_slug, season_year, stat_category)

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


# ===== ADMIN / BULK ENDPOINTS =====

@app.get("/api/admin/db/stats")
def get_database_stats(db: Session = Depends(get_db)):
    """
    Get database statistics - see what's currently stored.
    Useful for checking if bulk operations worked.
    """
    try:
        stats = {
            "players": {
                "total": db.query(models.Player).count(),
                "scraped": db.query(models.Player).filter(models.Player.career_scraped == True).count(),
                "active": db.query(models.Player).filter(models.Player.is_active == True).count(),
            },
            "game_logs": {
                "total": db.query(models.GameLog).count(),
            },
            "games": {
                "total": db.query(models.Game).count(),
                "by_status": {}
            },
            "season_averages": {
                "total": db.query(models.SeasonAverage).count(),
            },
            "scraping_logs": {
                "total": db.query(models.ScrapingLog).count(),
                "successful": db.query(models.ScrapingLog).filter(models.ScrapingLog.status == "success").count(),
                "failed": db.query(models.ScrapingLog).filter(models.ScrapingLog.status == "error").count(),
            }
        }

        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching database stats: {str(e)}")


@app.get("/api/admin/db/players")
def list_all_players(
    limit: int = Query(default=50, le=500),
    offset: int = Query(default=0, ge=0),
    scraped_only: bool = Query(default=False, description="Only show players with scraped data"),
    db: Session = Depends(get_db)
):
    """
    List all players in the database.
    Useful for seeing what players are available.
    """
    try:
        query = db.query(models.Player)

        if scraped_only:
            query = query.filter(models.Player.career_scraped == True)

        total = query.count()
        players = query.offset(offset).limit(limit).all()

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "count": len(players),
            "players": [
                {
                    "slug": p.player_slug,
                    "name": p.full_name,
                    "team": p.current_team,
                    "position": p.position,
                    "is_active": p.is_active,
                    "career_scraped": p.career_scraped,
                    "last_game_date": p.last_game_date.isoformat() if p.last_game_date else None,
                    "last_scraped": p.last_scraped_at.isoformat() if p.last_scraped_at else None
                }
                for p in players
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing players: {str(e)}")


@app.get("/api/admin/db/games")
def list_all_games(
    limit: int = Query(default=50, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List all games in the database.
    Useful for seeing what games are scheduled.
    """
    try:
        total = db.query(models.Game).count()
        games = db.query(models.Game).order_by(
            models.Game.game_date.desc()
        ).offset(offset).limit(limit).all()

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "count": len(games),
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
        raise HTTPException(status_code=500, detail=f"Error listing games: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
