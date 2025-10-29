"""
Test script for fetching NBA game schedules
"""
from basketball_reference_web_scraper import client
from datetime import datetime, date, timezone
import json
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

def test_season_schedule():
    """Test fetching the full season schedule"""
    print("=" * 60)
    print("TEST 1: Fetching Season Schedule")
    print("=" * 60)

    try:
        # Fetch current season schedule (2025-26 season)
        season_year = 2026
        print(f"\nFetching schedule for {season_year-1}-{season_year} season...")

        schedule = client.season_schedule(season_end_year=season_year)

        print(f"✅ Successfully fetched {len(schedule)} games")

        # Show first game
        if schedule:
            first_game = schedule[0]
            print("\n📋 Sample game data structure:")
            print(json.dumps(str(first_game), indent=2))

            # Show available fields
            print("\n📊 Available fields in game data:")
            for key in first_game.keys() if hasattr(first_game, 'keys') else dir(first_game):
                if not key.startswith('_'):
                    value = getattr(first_game, key) if hasattr(first_game, key) else first_game.get(key)
                    print(f"  - {key}: {type(value).__name__}")

        return schedule

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_today_games(schedule):
    """Filter schedule for today's games"""
    print("\n" + "=" * 60)
    print("TEST 2: Finding Today's Games")
    print("=" * 60)

    if not schedule:
        print("⚠️  No schedule data available")
        return

    # Get today's date in Eastern Time
    et_tz = ZoneInfo('America/New_York')
    now_et = datetime.now(et_tz)
    today_et = now_et.date()

    print(f"\nToday's date (ET): {today_et}")
    print(f"Current time (ET): {now_et.strftime('%Y-%m-%d %I:%M %p %Z')}")

    # Show season date range (in UTC for reference)
    if schedule:
        season_start = min(g['start_time'].date() for g in schedule)
        season_end = max(g['start_time'].date() for g in schedule)
        print(f"Season date range (UTC): {season_start} to {season_end}")

    # Filter for today's games (convert UTC to ET)
    today_games = []
    for game in schedule:
        # Convert UTC time to Eastern Time
        utc_time = game['start_time']
        et_time = utc_time.astimezone(et_tz)
        game_date_et = et_time.date()

        if game_date_et == today_et:
            # Store the ET time with the game for display
            game['start_time_et'] = et_time
            today_games.append(game)

    print(f"\n📅 Found {len(today_games)} games scheduled for today")

    if today_games:
        for i, game in enumerate(today_games, 1):
            print(f"\nGame {i}:")
            away_team = game['away_team'].value if hasattr(game['away_team'], 'value') else str(game['away_team'])
            home_team = game['home_team'].value if hasattr(game['home_team'], 'value') else str(game['home_team'])
            print(f"  {away_team} @ {home_team}")
            print(f"  Time (ET): {game['start_time_et'].strftime('%I:%M %p')}")
            print(f"  Time (UTC): {game['start_time']}")
    else:
        # Show next upcoming games instead
        print("\n📅 No games today. Showing next 5 upcoming games:")
        upcoming_games = []
        for g in schedule:
            et_time = g['start_time'].astimezone(et_tz)
            if et_time.date() > today_et:
                g['start_time_et'] = et_time
                upcoming_games.append(g)

        for i, game in enumerate(sorted(upcoming_games, key=lambda x: x['start_time_et'])[:5], 1):
            print(f"\nGame {i}:")
            away_team = game['away_team'].value if hasattr(game['away_team'], 'value') else str(game['away_team'])
            home_team = game['home_team'].value if hasattr(game['home_team'], 'value') else str(game['home_team'])
            print(f"  {away_team} @ {home_team}")
            print(f"  Date: {game['start_time_et'].strftime('%A, %B %d, %Y')}")
            print(f"  Time (ET): {game['start_time_et'].strftime('%I:%M %p')}")

def test_specific_date_games(schedule):
    """Test filtering games for a specific date"""
    print("\n" + "=" * 60)
    print("TEST 3: Games for Specific Date")
    print("=" * 60)

    if not schedule:
        print("⚠️  No schedule data available")
        return

    # Convert to Eastern Time
    et_tz = ZoneInfo('America/New_York')

    # Use opening night as test date (Oct 22, 2025)
    test_date = date(2025, 10, 22)
    print(f"\nTest date (ET): {test_date}")

    # Filter games by ET date
    games_on_date = []
    for game in schedule:
        et_time = game['start_time'].astimezone(et_tz)
        if et_time.date() == test_date:
            game['start_time_et'] = et_time
            games_on_date.append(game)

    print(f"📅 Found {len(games_on_date)} games on {test_date}")

    for i, game in enumerate(games_on_date, 1):  # Show all games on this date
        print(f"\nGame {i}:")
        away_team = game['away_team'].value if hasattr(game['away_team'], 'value') else str(game['away_team'])
        home_team = game['home_team'].value if hasattr(game['home_team'], 'value') else str(game['home_team'])
        print(f"  {away_team} @ {home_team}")
        print(f"  Time (ET): {game['start_time_et'].strftime('%I:%M %p')}")

if __name__ == "__main__":
    print("\n🏀 Basketball Reference Schedule API Tests\n")

    # Run tests
    schedule = test_season_schedule()
    test_today_games(schedule)
    test_specific_date_games(schedule)

    print("\n" + "=" * 60)
    print("✅ Schedule tests complete!")
    print("=" * 60)
