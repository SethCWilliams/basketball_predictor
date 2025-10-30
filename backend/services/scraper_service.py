from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import OutputType, Team
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import List, Optional
import time
import models
import sys
sys.path.insert(0, '..')
from utils import get_current_season_year, get_today_local, utc_to_local, format_game_time


class ScraperService:
    """Smart scraping service that uses database as cache"""

    def __init__(self, db: Session, timezone: Optional[str] = None):
        self.db = db
        self.timezone = timezone
        # Automatically detect current season (2025-26 = 2026, 2026-27 = 2027, etc.)
        self.current_season = get_current_season_year()

    def get_or_scrape_player_data(self, player_slug: str) -> models.Player:
        """
        Main entry point: Get player data from DB or scrape if needed.
        This is the 'smart caching' logic!
        """
        # Check if player exists in database
        player = self.db.query(models.Player).filter(
            models.Player.player_slug == player_slug
        ).first()

        if not player:
            # Player doesn't exist - scrape full career
            print(f"🔍 Player {player_slug} not found in DB. Scraping full career...")
            player = self._scrape_full_player_career(player_slug)
        elif not player.career_scraped:
            # Player exists but career not fully scraped
            print(f"🔍 Player {player_slug} needs full career scrape...")
            player = self._scrape_full_player_career(player_slug)
        elif self._needs_update(player):
            # Player exists, but data might be stale
            print(f"🔄 Player {player_slug} data is stale. Scraping new games...")
            player = self._scrape_incremental_update(player)
        else:
            print(f"✅ Player {player_slug} data is current. Using cache!")

        return player

    def _needs_update(self, player: models.Player) -> bool:
        """Check if player data needs updating"""
        if not player.last_game_date:
            return True

        # If last game was more than 1 day ago, check for new games
        days_since_update = (date.today() - player.last_game_date).days
        return days_since_update > 1

    def _scrape_full_player_career(self, player_slug: str) -> models.Player:
        """Scrape entire career for a player (first-time scrape)"""
        start_time = time.time()

        try:
            # Scrape all career games
            print(f"  Fetching game logs for {player_slug}...")
            game_logs = client.regular_season_player_box_scores(
                player_identifier=player_slug,
                season_end_year=self.current_season
            )

            if not game_logs:
                raise ValueError(f"No data found for player {player_slug}")

            # Create or update player record
            player = self.db.query(models.Player).filter(
                models.Player.player_slug == player_slug
            ).first()

            if not player:
                # Extract player info from first game log
                first_game = game_logs[0]
                player = models.Player(
                    player_slug=player_slug,
                    full_name=first_game.get('name', player_slug),
                    career_scraped=True,
                    last_scraped_at=datetime.utcnow()
                )
                self.db.add(player)
                self.db.flush()  # Get the player ID

            # Insert all game logs
            games_added = 0
            for game_data in game_logs:
                game_log = self._create_game_log_from_scrape(player.id, game_data)
                if game_log:
                    self.db.merge(game_log)  # Use merge to handle duplicates
                    games_added += 1

            # Update player metadata
            player.career_scraped = True
            player.last_scraped_at = datetime.utcnow()
            if game_logs:
                # Find the most recent game date
                dates = [g.game_date for g in game_logs if hasattr(g, 'game_date')]
                if dates:
                    player.last_game_date = max(dates)

            self.db.commit()

            duration = time.time() - start_time
            print(f"✅ Scraped {games_added} games for {player_slug} in {duration:.1f}s")

            # Log the scraping activity
            self._log_scrape('player', player_slug, 'full_career', games_added, 'success', duration)

            return player

        except Exception as e:
            self.db.rollback()
            duration = time.time() - start_time
            print(f"❌ Error scraping {player_slug}: {e}")
            self._log_scrape('player', player_slug, 'full_career', 0, 'failed', duration, str(e))
            raise

    def _scrape_incremental_update(self, player: models.Player) -> models.Player:
        """Scrape only new games since last update"""
        start_time = time.time()

        try:
            # Get all games for current season
            all_games = client.regular_season_player_box_scores(
                player_identifier=player.player_slug,
                season_end_year=self.current_season
            )

            # Filter for games after last_game_date
            new_games = [
                g for g in all_games
                if hasattr(g, 'game_date') and g.game_date > player.last_game_date
            ]

            if new_games:
                games_added = 0
                for game_data in new_games:
                    game_log = self._create_game_log_from_scrape(player.id, game_data)
                    if game_log:
                        self.db.merge(game_log)
                        games_added += 1

                # Update player metadata
                player.last_scraped_at = datetime.utcnow()
                dates = [g.game_date for g in new_games if hasattr(g, 'game_date')]
                if dates:
                    player.last_game_date = max(dates)

                self.db.commit()

                duration = time.time() - start_time
                print(f"✅ Updated {player.player_slug} with {games_added} new games in {duration:.1f}s")
                self._log_scrape('player', player.player_slug, 'incremental', games_added, 'success', duration)
            else:
                duration = time.time() - start_time
                print(f"✅ {player.player_slug} already up to date")
                self._log_scrape('player', player.player_slug, 'incremental', 0, 'success', duration)

            return player

        except Exception as e:
            self.db.rollback()
            duration = time.time() - start_time
            print(f"❌ Error updating {player.player_slug}: {e}")
            self._log_scrape('player', player.player_slug, 'incremental', 0, 'failed', duration, str(e))
            raise

    def _create_game_log_from_scrape(self, player_id: int, game_data) -> Optional[models.GameLog]:
        """Convert scraped game data to GameLog model"""
        try:
            # Handle both dict and object access patterns
            def get_val(key, default=None):
                if isinstance(game_data, dict):
                    return game_data.get(key, default)
                return getattr(game_data, key, default)

            # Calculate derived stats
            points = get_val('points', 0) or 0
            rebounds = (get_val('offensive_rebounds', 0) or 0) + (get_val('defensive_rebounds', 0) or 0)
            assists = get_val('assists', 0) or 0
            steals = get_val('steals', 0) or 0
            blocks = get_val('blocks', 0) or 0

            # Check for double/triple double
            stats_10_plus = sum([
                points >= 10,
                rebounds >= 10,
                assists >= 10,
                steals >= 10,
                blocks >= 10
            ])

            double_double = stats_10_plus >= 2
            triple_double = stats_10_plus >= 3

            # Get opponent (handle enum or string)
            opponent = get_val('opponent', 'UNK')
            if hasattr(opponent, 'value'):
                opponent = opponent.value

            # Get team
            team = get_val('team', '')
            if hasattr(team, 'value'):
                team = team.value

            return models.GameLog(
                player_id=player_id,
                game_date=get_val('game_date') or get_val('date'),
                season=get_val('season', self.current_season),
                opponent=str(opponent)[:3] if opponent else 'UNK',
                is_home_game=get_val('location', 'HOME') != 'AWAY',
                minutes_played=float(get_val('seconds_played', 0) or 0) / 60.0,
                points=points,
                rebounds=rebounds,
                assists=assists,
                steals=steals,
                blocks=blocks,
                turnovers=get_val('turnovers', 0) or 0,
                personal_fouls=get_val('personal_fouls', 0) or 0,
                field_goals_made=get_val('made_field_goals', 0) or 0,
                field_goals_attempted=get_val('attempted_field_goals', 0) or 0,
                three_pointers_made=get_val('made_three_point_field_goals', 0) or 0,
                three_pointers_attempted=get_val('attempted_three_point_field_goals', 0) or 0,
                free_throws_made=get_val('made_free_throws', 0) or 0,
                free_throws_attempted=get_val('attempted_free_throws', 0) or 0,
                offensive_rebounds=get_val('offensive_rebounds', 0) or 0,
                defensive_rebounds=get_val('defensive_rebounds', 0) or 0,
                # Derived stats
                pts_plus_ast=points + assists,
                pts_plus_reb=points + rebounds,
                reb_plus_ast=rebounds + assists,
                pts_reb_ast=points + rebounds + assists,
                stl_plus_blk=steals + blocks,
                double_double=double_double,
                triple_double=triple_double,
                did_not_play=(get_val('seconds_played', 0) or 0) == 0
            )
        except Exception as e:
            print(f"  Error creating game log: {e}")
            return None

    def scrape_schedule_by_date(self, target_date: date) -> List[models.Game]:
        """
        Scrape NBA schedule for a specific date.
        Note: Times from API are in UTC and need to be converted to user's timezone.

        Args:
            target_date: The date to get games for (as date object or YYYY-MM-DD string)
        """
        start_time_scrape = time.time()

        try:
            # If target_date is a string, convert to date
            if isinstance(target_date, str):
                target_date = datetime.strptime(target_date, '%Y-%m-%d').date()

            schedule = client.season_schedule(season_end_year=self.current_season)

            matching_games = []
            for game_data in schedule:
                # Handle both dict and object patterns
                def get_val(key, default=None):
                    if isinstance(game_data, dict):
                        return game_data.get(key, default)
                    return getattr(game_data, key, default)

                game_datetime = get_val('start_time')
                if game_datetime:
                    # Convert UTC time to user's local timezone
                    if isinstance(game_datetime, datetime):
                        local_datetime = utc_to_local(game_datetime, self.timezone)
                        game_date = local_datetime.date()
                    else:
                        game_date = game_datetime

                    if game_date == target_date:
                        matching_games.append(game_data)

            games = self._process_and_store_games(matching_games, target_date)

            duration = time.time() - start_time_scrape
            self._log_scrape('schedule', target_date.isoformat(), 'date_scrape', len(games), 'success', duration)

            return games

        except Exception as e:
            self.db.rollback()
            duration = time.time() - start_time_scrape
            print(f"❌ Error scraping schedule for {target_date}: {e}")
            self._log_scrape('schedule', target_date.isoformat(), 'date_scrape', 0, 'error', duration, str(e))
            raise

    def scrape_today_schedule(self) -> List[models.Game]:
        """
        Scrape today's NBA schedule.
        Note: Times from API are in UTC and need to be converted to user's timezone.
        """
        start_time_scrape = time.time()

        try:
            schedule = client.season_schedule(season_end_year=self.current_season)
            # Get today's date in user's timezone (not UTC)
            today = get_today_local(self.timezone)

            today_games = []
            for game_data in schedule:
                # Handle both dict and object patterns
                def get_val(key, default=None):
                    if isinstance(game_data, dict):
                        return game_data.get(key, default)
                    return getattr(game_data, key, default)

                game_datetime = get_val('start_time')
                if game_datetime:
                    # Convert UTC time to user's local timezone
                    if isinstance(game_datetime, datetime):
                        local_datetime = utc_to_local(game_datetime, self.timezone)
                        game_date = local_datetime.date()
                    else:
                        game_date = game_datetime

                    if game_date == today:
                        today_games.append(game_data)

            games = self._process_and_store_games(today_games, today)

            duration = time.time() - start_time_scrape
            print(f"✅ Scraped {len(games)} games for today in {duration:.1f}s")
            self._log_scrape('schedule', 'today', 'schedule', len(games), 'success', duration)

            return games

        except Exception as e:
            self.db.rollback()
            duration = time.time() - start_time_scrape
            print(f"❌ Error scraping schedule: {e}")
            self._log_scrape('schedule', 'today', 'schedule', 0, 'failed', duration, str(e))
            raise

    def _process_and_store_games(self, games_data: List, target_date: date) -> List[models.Game]:
        """
        Helper method to process and store game data.
        Used by both scrape_today_schedule and scrape_schedule_by_date.
        """
        games = []
        for game_data in games_data:
            def get_val(key, default=None):
                if isinstance(game_data, dict):
                    return game_data.get(key, default)
                return getattr(game_data, key, default)

            home_team = get_val('home_team', '')
            away_team = get_val('away_team', '')

            if hasattr(home_team, 'value'):
                home_team = home_team.value
            if hasattr(away_team, 'value'):
                away_team = away_team.value

            # Format time in user's timezone
            start_time_val = get_val('start_time')
            if isinstance(start_time_val, datetime):
                start_time_str = format_game_time(start_time_val, self.timezone)
                # Determine game status based on current time vs start time
                game_status = self._determine_game_status(start_time_val)
            else:
                start_time_str = str(start_time_val)
                game_status = 'scheduled'  # Default if we don't have datetime

            # Get scores (only available for completed games)
            home_score = get_val('home_team_score')
            away_score = get_val('away_team_score')

            # Check if game already exists (avoid duplicates)
            existing_game = self.db.query(models.Game).filter(
                models.Game.game_date == target_date,
                models.Game.home_team == str(home_team)[:3],
                models.Game.away_team == str(away_team)[:3]
            ).first()

            if not existing_game:
                game = models.Game(
                    game_date=target_date,
                    season=self.current_season,
                    home_team=str(home_team)[:3],
                    away_team=str(away_team)[:3],
                    start_time=start_time_str,
                    game_status=game_status,
                    home_score=home_score,
                    away_score=away_score
                )
                self.db.add(game)
                games.append(game)
            else:
                # Update start time, status, and scores if they changed
                existing_game.start_time = start_time_str
                existing_game.game_status = game_status
                existing_game.home_score = home_score
                existing_game.away_score = away_score
                games.append(existing_game)

        self.db.commit()
        return games

    def _determine_game_status(self, start_time_utc: datetime) -> str:
        """
        Determine game status based on start time.

        Logic:
        - If start time is in the future: 'scheduled'
        - If start time was 0-3 hours ago: 'in_progress' (NBA games are ~2.5 hours)
        - If start time was 3+ hours ago: 'final'
        """
        # Make sure both datetimes are timezone-naive for comparison
        if start_time_utc.tzinfo is not None:
            start_time_utc = start_time_utc.replace(tzinfo=None)

        now_utc = datetime.utcnow()
        time_since_start = now_utc - start_time_utc

        if time_since_start.total_seconds() < 0:
            # Game hasn't started yet
            return 'scheduled'
        elif time_since_start.total_seconds() < 3 * 3600:  # 3 hours
            # Game started less than 3 hours ago - likely in progress or just finished
            return 'in_progress'
        else:
            # Game started more than 3 hours ago - definitely finished
            return 'final'

    def _log_scrape(self, entity_type: str, entity_id: str, scrape_type: str,
                   games_scraped: int, status: str, duration: float, error: str = None):
        """Log scraping activity"""
        try:
            log = models.ScrapingLog(
                entity_type=entity_type,
                entity_id=entity_id,
                scrape_type=scrape_type,
                games_scraped=games_scraped,
                status=status,
                error_message=error,
                duration_seconds=duration
            )
            self.db.add(log)
            self.db.commit()
        except Exception as e:
            print(f"  Warning: Could not log scrape activity: {e}")
            self.db.rollback()
