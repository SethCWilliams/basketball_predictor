from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict
import models
from services.scraper_service import ScraperService


class PlayerService:
    """Business logic for player data operations"""

    # Mapping of stat categories to database columns
    STAT_MAPPINGS = {
        'points': 'points',
        'assists': 'assists',
        'rebounds': 'rebounds',
        'threes': 'three_pointers_made',
        'pts_ast': 'pts_plus_ast',
        'pts_reb': 'pts_plus_reb',
        'reb_ast': 'reb_plus_ast',
        'pts_reb_ast': 'pts_reb_ast',
        'double_double': 'double_double',
        'triple_double': 'triple_double',
        '1q_points': 'first_quarter_points',
        '1q_assists': 'first_quarter_assists',
        '1q_rebounds': 'first_quarter_rebounds',
        'steals': 'steals',
        'blocks': 'blocks',
        'stl_blk': 'stl_plus_blk',
        'turnovers': 'turnovers',
        'fouls': 'personal_fouls',
        'ft_attempted': 'free_throws_attempted',
    }

    def __init__(self, db: Session):
        self.db = db
        self.scraper = ScraperService(db)

    def get_player_by_slug(self, player_slug: str) -> models.Player:
        """Get player, scraping if necessary"""
        return self.scraper.get_or_scrape_player_data(player_slug)

    def get_recent_games(self, player_slug: str, n: int = 10,
                        filters: Dict = None) -> List[models.GameLog]:
        """
        Get last N games for a player with optional filters.

        Filters can include:
        - opponent: Filter by specific opponent
        - is_home: Filter by home/away
        - season: Filter by season
        """
        player = self.get_player_by_slug(player_slug)

        query = self.db.query(models.GameLog).filter(
            models.GameLog.player_id == player.id,
            models.GameLog.did_not_play == False
        )

        # Apply filters
        if filters:
            if 'opponent' in filters:
                query = query.filter(models.GameLog.opponent == filters['opponent'])
            if 'is_home' in filters:
                query = query.filter(models.GameLog.is_home_game == filters['is_home'])
            if 'season' in filters:
                query = query.filter(models.GameLog.season == filters['season'])

        return query.order_by(desc(models.GameLog.game_date)).limit(n).all()

    def get_season_average(self, player_slug: str, season: int,
                          stat_category: str = 'points') -> Dict:
        """Calculate season averages for a player"""
        player = self.get_player_by_slug(player_slug)

        # Get the stat column name
        stat_col = self.STAT_MAPPINGS.get(stat_category, 'points')

        # Query for season averages
        games = self.db.query(models.GameLog).filter(
            models.GameLog.player_id == player.id,
            models.GameLog.season == season,
            models.GameLog.did_not_play == False
        ).all()

        if not games:
            return {
                'player_slug': player_slug,
                'season': season,
                'games_played': 0,
                'average': 0.0
            }

        # Calculate average for the requested stat
        stat_values = []
        for game in games:
            val = getattr(game, stat_col, 0)
            if val is not None:
                stat_values.append(float(val) if not isinstance(val, bool) else (1.0 if val else 0.0))

        average = sum(stat_values) / len(stat_values) if stat_values else 0.0

        return {
            'player_slug': player_slug,
            'player_name': player.full_name,
            'season': season,
            'games_played': len(games),
            'stat_category': stat_category,
            'average': round(average, 1)
        }

    def get_graph_average(self, player_slug: str, stat_category: str = 'points',
                         n_games: int = 15, filters: Dict = None) -> Dict:
        """
        Calculate average for games that will be displayed in the graph.
        This respects all active filters.
        """
        games = self.get_recent_games(player_slug, n=n_games, filters=filters)

        if not games:
            return {
                'player_slug': player_slug,
                'stat_category': stat_category,
                'games_count': 0,
                'average': 0.0
            }

        # Get the stat column name
        stat_col = self.STAT_MAPPINGS.get(stat_category, 'points')

        # Calculate average
        stat_values = []
        for game in games:
            val = getattr(game, stat_col, 0)
            if val is not None:
                stat_values.append(float(val) if not isinstance(val, bool) else (1.0 if val else 0.0))

        average = sum(stat_values) / len(stat_values) if stat_values else 0.0

        return {
            'player_slug': player_slug,
            'stat_category': stat_category,
            'games_count': len(games),
            'average': round(average, 1)
        }

    def calculate_hit_rate(self, player_slug: str, stat_category: str,
                          line_value: float, n_games: int = 15,
                          filters: Dict = None) -> Dict:
        """
        Calculate hit rate: percentage of games where player went OVER the line.
        Formula: games where stat_value >= line_value / total_games_shown
        """
        games = self.get_recent_games(player_slug, n=n_games, filters=filters)

        if not games:
            return {
                'player_slug': player_slug,
                'stat_category': stat_category,
                'line_value': line_value,
                'games_count': 0,
                'hits': 0,
                'hit_rate_percentage': 0.0,
                'hit_rate_display': '0% (0/0)'
            }

        # Get the stat column name
        stat_col = self.STAT_MAPPINGS.get(stat_category, 'points')

        # Count hits
        hits = 0
        for game in games:
            val = getattr(game, stat_col, 0)
            if val is not None:
                stat_val = float(val) if not isinstance(val, bool) else (1.0 if val else 0.0)
                if stat_val >= line_value:
                    hits += 1

        total_games = len(games)
        hit_rate = (hits / total_games * 100) if total_games > 0 else 0.0

        return {
            'player_slug': player_slug,
            'stat_category': stat_category,
            'line_value': line_value,
            'games_count': total_games,
            'hits': hits,
            'hit_rate_percentage': round(hit_rate, 1),
            'hit_rate_display': f'{int(hit_rate)}% ({hits}/{total_games})'
        }

    def get_player_chart_data(self, player_slug: str, stat_category: str = 'points',
                             n_games: int = 15, filters: Dict = None) -> Dict:
        """
        Get all data needed for the main performance chart.
        Returns game-by-game data with opponent, date, and stat value.
        """
        player = self.get_player_by_slug(player_slug)
        games = self.get_recent_games(player_slug, n=n_games, filters=filters)

        # Get the stat column name
        stat_col = self.STAT_MAPPINGS.get(stat_category, 'points')

        chart_data = []
        for game in reversed(games):  # Reverse to show chronological order (oldest to newest)
            val = getattr(game, stat_col, 0)
            stat_val = float(val) if val is not None and not isinstance(val, bool) else (1.0 if val else 0.0)

            chart_data.append({
                'date': game.game_date.isoformat(),
                'opponent': game.opponent,
                'is_home': game.is_home_game,
                'stat_value': stat_val,
                'minutes': float(game.minutes_played) if game.minutes_played else 0.0,
                'game_result': game.game_result,
                'score_margin': game.score_margin
            })

        return {
            'player_slug': player_slug,
            'player_name': player.full_name,
            'position': player.position,
            'team': player.current_team,
            'stat_category': stat_category,
            'games_count': len(chart_data),
            'games': chart_data
        }

    def search_players(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for players by name"""
        players = self.db.query(models.Player).filter(
            models.Player.full_name.ilike(f'%{query}%')
        ).limit(limit).all()

        return [
            {
                'slug': p.player_slug,
                'name': p.full_name,
                'position': p.position,
                'team': p.current_team
            }
            for p in players
        ]
