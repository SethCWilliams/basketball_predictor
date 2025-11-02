"""
Admin endpoints for bulk data population and management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models
import json
import os
from pathlib import Path

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/teams/populate")
def populate_teams(db: Session = Depends(get_db)):
    """
    Populate teams table with all 30 NBA teams from seed data.
    Idempotent - can be run multiple times safely.
    """
    try:
        # Load teams seed data
        data_dir = Path(__file__).parent.parent / "data"
        teams_file = data_dir / "nba_teams.json"

        if not teams_file.exists():
            raise HTTPException(status_code=500, detail="Teams seed data file not found")

        with open(teams_file, 'r') as f:
            teams_data = json.load(f)

        teams_added = 0
        teams_updated = 0

        for team_data in teams_data:
            # Check if team already exists
            existing_team = db.query(models.Team).filter(
                models.Team.abbreviation == team_data['abbreviation']
            ).first()

            if existing_team:
                # Update existing team
                existing_team.full_name = team_data['full_name']
                existing_team.city = team_data['city']
                existing_team.conference = team_data['conference']
                existing_team.division = team_data['division']
                teams_updated += 1
            else:
                # Create new team
                new_team = models.Team(
                    abbreviation=team_data['abbreviation'],
                    full_name=team_data['full_name'],
                    city=team_data['city'],
                    conference=team_data['conference'],
                    division=team_data['division']
                )
                db.add(new_team)
                teams_added += 1

        db.commit()

        return {
            "status": "success",
            "teams_added": teams_added,
            "teams_updated": teams_updated,
            "total_teams": teams_added + teams_updated,
            "message": f"Successfully populated {teams_added + teams_updated} NBA teams"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error populating teams: {str(e)}")


@router.get("/teams/list")
def list_teams(db: Session = Depends(get_db)):
    """Get all teams from database"""
    teams = db.query(models.Team).order_by(models.Team.full_name).all()

    return {
        "count": len(teams),
        "teams": [
            {
                "abbreviation": t.abbreviation,
                "full_name": t.full_name,
                "city": t.city,
                "conference": t.conference,
                "division": t.division
            }
            for t in teams
        ]
    }


@router.get("/players/scrape-status")
def get_scrape_status(db: Session = Depends(get_db)):
    """
    Get overview of player scraping status.
    Shows how many players are cached and their data completeness.
    """
    try:
        total_players = db.query(models.Player).count()
        scraped_players = db.query(models.Player).filter(
            models.Player.career_scraped == True
        ).count()

        # Get game log statistics
        total_games = db.query(models.GameLog).count()

        # Get recent scraping activity
        recent_scrapes = db.query(models.ScrapingLog).filter(
            models.ScrapingLog.entity_type == 'player'
        ).order_by(models.ScrapingLog.scraped_at.desc()).limit(10).all()

        return {
            "players": {
                "total": total_players,
                "fully_scraped": scraped_players,
                "partially_scraped": total_players - scraped_players
            },
            "game_logs": {
                "total": total_games,
                "average_per_player": round(total_games / total_players, 1) if total_players > 0 else 0
            },
            "recent_activity": [
                {
                    "player_slug": log.entity_id,
                    "scrape_type": log.scrape_type,
                    "games_scraped": log.games_scraped,
                    "status": log.status,
                    "duration": round(log.duration_seconds, 1) if log.duration_seconds else None,
                    "scraped_at": log.scraped_at.isoformat() if log.scraped_at else None
                }
                for log in recent_scrapes
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching scrape status: {str(e)}")
