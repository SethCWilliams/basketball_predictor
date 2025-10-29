from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Float, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Player(Base):
    """NBA Player information and scraping metadata"""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    player_slug = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    position = Column(String(10))  # PG, SG, SF, PF, C
    current_team = Column(String(3))  # Team abbreviation (e.g., 'SAC')
    is_active = Column(Boolean, default=True)
    headshot_url = Column(String(255))

    # Tracking metadata for smart caching
    career_scraped = Column(Boolean, default=False)
    last_scraped_at = Column(DateTime)
    last_game_date = Column(Date)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    game_logs = relationship("GameLog", back_populates="player", cascade="all, delete-orphan")
    season_averages = relationship("SeasonAverage", back_populates="player", cascade="all, delete-orphan")


class Team(Base):
    """NBA Team information"""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    abbreviation = Column(String(3), unique=True, nullable=False, index=True)
    full_name = Column(String(50), nullable=False)
    city = Column(String(50))
    logo_url = Column(String(255))
    conference = Column(String(10))  # East or West
    division = Column(String(20))

    # Defensive ratings (updated periodically)
    defensive_rating = Column(Float)
    pace = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Game(Base):
    """Scheduled and completed NBA games"""
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    game_date = Column(Date, nullable=False, index=True)
    season = Column(Integer, nullable=False)

    home_team = Column(String(3), nullable=False)
    away_team = Column(String(3), nullable=False)

    start_time = Column(String(20))
    venue = Column(String(100))

    # Results (null if game hasn't happened)
    home_score = Column(Integer)
    away_score = Column(Integer)
    game_status = Column(String(20), default='scheduled')  # scheduled, in_progress, final, postponed

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('game_date', 'home_team', 'away_team', name='uq_game'),
    )


class GameLog(Base):
    """Individual game performance for each player - supports all 20 PropsMadness stat categories"""
    __tablename__ = "game_logs"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)

    # Game identification
    game_date = Column(Date, nullable=False, index=True)
    season = Column(Integer, nullable=False)
    opponent = Column(String(3), nullable=False)
    is_home_game = Column(Boolean, nullable=False)
    game_result = Column(String(1))  # 'W' or 'L'
    score_margin = Column(Integer)  # Win/loss margin

    # Basic stats - Core categories
    minutes_played = Column(Float)
    points = Column(Integer)
    rebounds = Column(Integer)
    assists = Column(Integer)
    steals = Column(Integer)
    blocks = Column(Integer)
    turnovers = Column(Integer)
    personal_fouls = Column(Integer)

    # Shooting stats
    field_goals_made = Column(Integer)
    field_goals_attempted = Column(Integer)
    three_pointers_made = Column(Integer)  # For "Threes" category
    three_pointers_attempted = Column(Integer)
    free_throws_made = Column(Integer)
    free_throws_attempted = Column(Integer)  # For "FT Attempted" category

    # Advanced stats
    plus_minus = Column(Integer)
    offensive_rebounds = Column(Integer)
    defensive_rebounds = Column(Integer)

    # Derived/Combo stats (calculated on insert/update for performance)
    pts_plus_ast = Column(Integer)  # Points + Assists
    pts_plus_reb = Column(Integer)  # Points + Rebounds
    reb_plus_ast = Column(Integer)  # Rebounds + Assists
    pts_reb_ast = Column(Integer)  # Points + Rebounds + Assists
    stl_plus_blk = Column(Integer)  # Steals + Blocks
    double_double = Column(Boolean, default=False)  # 10+ in 2 categories
    triple_double = Column(Boolean, default=False)  # 10+ in 3 categories

    # Quarter stats (for 1Q categories)
    first_quarter_points = Column(Integer)
    first_quarter_assists = Column(Integer)
    first_quarter_rebounds = Column(Integer)

    # Game metadata
    was_starter = Column(Boolean, default=False)
    did_not_play = Column(Boolean, default=False)
    dnp_reason = Column(String(50))

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    player = relationship("Player", back_populates="game_logs")

    __table_args__ = (
        UniqueConstraint('player_id', 'game_date', name='uq_player_game'),
    )


class SeasonAverage(Base):
    """Pre-calculated season averages for quick access"""
    __tablename__ = "season_averages"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    season = Column(Integer, nullable=False)

    games_played = Column(Integer, nullable=False)
    games_started = Column(Integer, default=0)

    # Per-game averages for all 20 stat categories
    minutes_per_game = Column(Float)
    points_per_game = Column(Float)
    rebounds_per_game = Column(Float)
    assists_per_game = Column(Float)
    steals_per_game = Column(Float)
    blocks_per_game = Column(Float)
    turnovers_per_game = Column(Float)
    personal_fouls_per_game = Column(Float)

    # Combo stats
    pts_ast_per_game = Column(Float)
    pts_reb_per_game = Column(Float)
    reb_ast_per_game = Column(Float)
    pts_reb_ast_per_game = Column(Float)
    stl_blk_per_game = Column(Float)

    # Shooting percentages
    field_goal_percentage = Column(Float)
    three_point_percentage = Column(Float)
    free_throw_percentage = Column(Float)
    three_pointers_made_per_game = Column(Float)
    free_throws_attempted_per_game = Column(Float)

    # Quarter averages
    first_quarter_points_per_game = Column(Float)
    first_quarter_assists_per_game = Column(Float)
    first_quarter_rebounds_per_game = Column(Float)

    # Double/Triple double rates
    double_double_rate = Column(Float)  # Percentage of games
    triple_double_rate = Column(Float)

    last_calculated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    player = relationship("Player", back_populates="season_averages")

    __table_args__ = (
        UniqueConstraint('player_id', 'season', name='uq_player_season'),
    )


class BettingLine(Base):
    """Betting lines for props - supports all 20 stat categories"""
    __tablename__ = "betting_lines"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    player_id = Column(Integer, ForeignKey("players.id"))

    stat_category = Column(String(20), nullable=False)  # points, assists, rebounds, etc.
    line_value = Column(Float, nullable=False)
    over_odds = Column(Integer)  # e.g., -110
    under_odds = Column(Integer)  # e.g., -110

    sportsbook = Column(String(50))  # Which sportsbook
    is_closing_line = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('game_id', 'player_id', 'stat_category', 'sportsbook', name='uq_betting_line'),
    )


class ScrapingLog(Base):
    """Track scraping activity for debugging and rate limiting"""
    __tablename__ = "scraping_log"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(20), nullable=False)  # 'player', 'schedule', 'team'
    entity_id = Column(String(50))  # player_slug, team abbrev, etc.

    scrape_type = Column(String(20), nullable=False)  # 'full_career', 'incremental', 'schedule'
    games_scraped = Column(Integer, default=0)

    status = Column(String(20), nullable=False)  # 'success', 'partial', 'failed'
    error_message = Column(Text)

    duration_seconds = Column(Float)
    scraped_at = Column(DateTime, default=datetime.utcnow, index=True)
