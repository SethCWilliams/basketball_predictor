"""
Test to see complete raw schedule data for a specific day
"""
from basketball_reference_web_scraper import client
from datetime import date
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo
import json

def test_raw_schedule_data():
    """Get and display complete raw schedule data"""
    print("=" * 60)
    print("TEST: Raw Schedule Data for a Specific Day")
    print("=" * 60)

    try:
        # Fetch full season schedule
        print("\n⏳ Fetching 2025-26 season schedule...")
        schedule = client.season_schedule(season_end_year=2026)
        print(f"✅ Fetched {len(schedule)} total games")

        # Convert to ET timezone
        et_tz = ZoneInfo('America/New_York')

        # Pick a specific date with games (opening night or recent)
        test_date = date(2025, 10, 22)  # Opening night
        print(f"\n📅 Filtering for games on: {test_date} (ET)")

        # Filter for that date
        games_on_date = []
        for game in schedule:
            et_time = game['start_time'].astimezone(et_tz)
            if et_time.date() == test_date:
                games_on_date.append(game)

        print(f"✅ Found {len(games_on_date)} games on {test_date}")

        # Show complete data for each game
        for i, game in enumerate(games_on_date, 1):
            print(f"\n{'='*60}")
            print(f"GAME {i}")
            print('='*60)

            # Show as formatted dict
            print("\n📋 Complete game data structure:")
            print("-" * 60)

            for key, value in sorted(game.items()):
                # Format the value for display
                if key == 'start_time':
                    et_time = value.astimezone(et_tz)
                    print(f"{key:20s} : {value} (UTC)")
                    print(f"{'':20s}   {et_time} (ET)")
                elif hasattr(value, 'value'):
                    # It's an enum
                    print(f"{key:20s} : {value} (enum value: {value.value})")
                elif hasattr(value, 'name'):
                    # It's an enum
                    print(f"{key:20s} : {value} (enum name: {value.name})")
                else:
                    print(f"{key:20s} : {value} (type: {type(value).__name__})")

            # Show matchup summary
            print(f"\n📊 Matchup Summary:")
            home_team = game['home_team']
            away_team = game['away_team']
            et_time = game['start_time'].astimezone(et_tz)

            home_team_name = home_team.value if hasattr(home_team, 'value') else str(home_team)
            away_team_name = away_team.value if hasattr(away_team, 'value') else str(away_team)

            print(f"  {away_team_name} @ {home_team_name}")
            print(f"  Time: {et_time.strftime('%I:%M %p ET')}")

            # Check if game has been played (has scores)
            if 'home_team_score' in game and game['home_team_score'] is not None:
                print(f"  Score: {away_team_name} {game['away_team_score']} - {home_team_name} {game['home_team_score']}")
            else:
                print(f"  Status: Scheduled (no scores yet)")

            print()

        # Now let's look at today's games
        print(f"\n{'='*60}")
        print("TODAY'S GAMES (if any)")
        print('='*60)

        today_et = date.today()
        print(f"\n📅 Today's date (ET): {today_et}")

        today_games = []
        for game in schedule:
            et_time = game['start_time'].astimezone(et_tz)
            if et_time.date() == today_et:
                today_games.append(game)

        if today_games:
            print(f"✅ Found {len(today_games)} games today\n")

            for i, game in enumerate(today_games, 1):
                home_team_name = game['home_team'].value if hasattr(game['home_team'], 'value') else str(game['home_team'])
                away_team_name = game['away_team'].value if hasattr(game['away_team'], 'value') else str(game['away_team'])
                et_time = game['start_time'].astimezone(et_tz)

                print(f"Game {i}: {away_team_name} @ {home_team_name}")
                print(f"  Time: {et_time.strftime('%I:%M %p ET')}")
                print(f"  All fields: {list(game.keys())}")
                print()
        else:
            print("⚠️  No games scheduled for today")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_what_we_need_for_predictions():
    """Identify what data we need from schedule for predictions"""
    print("\n" + "=" * 60)
    print("TEST: What We Need From Schedule")
    print("=" * 60)

    print("\n📝 For each game, we need to extract:")
    print("  1. Home team identifier")
    print("  2. Away team identifier")
    print("  3. Game date/time")
    print("  4. Game ID (if available)")

    try:
        schedule = client.season_schedule(season_end_year=2026)
        et_tz = ZoneInfo('America/New_York')

        # Get first game
        if schedule:
            game = schedule[0]
            et_time = game['start_time'].astimezone(et_tz)

            print(f"\n📊 Example extraction from first game:")
            print(f"  Game Date (ET): {et_time.date()}")
            print(f"  Game Time (ET): {et_time.strftime('%I:%M %p')}")
            print(f"  Home Team: {game['home_team']}")
            print(f"  Home Team (enum value): {game['home_team'].value if hasattr(game['home_team'], 'value') else 'N/A'}")
            print(f"  Home Team (enum name): {game['home_team'].name if hasattr(game['home_team'], 'name') else 'N/A'}")
            print(f"  Away Team: {game['away_team']}")
            print(f"  Away Team (enum value): {game['away_team'].value if hasattr(game['away_team'], 'value') else 'N/A'}")

            print(f"\n💡 Key Insights:")
            print(f"  - Teams are Team enum objects")
            print(f"  - Use .value to get full team name")
            print(f"  - Use .name to get enum constant name")
            print(f"  - No explicit game ID in schedule")
            print(f"  - Can create unique ID from: date + home_team + away_team")

            # Show how to create a unique game identifier
            game_id = f"{et_time.date()}_{game['home_team'].name}_{game['away_team'].name}"
            print(f"\n  Proposed Game ID format: {game_id}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("\n🏀 Raw Schedule Data Test\n")

    test_raw_schedule_data()
    test_what_we_need_for_predictions()

    print("\n" + "=" * 60)
    print("✅ Raw schedule test complete!")
    print("=" * 60)
    print("\n📝 Summary:")
    print("  - Schedule returns list of game dicts")
    print("  - Each game has home_team, away_team (Team enums)")
    print("  - Start times in UTC, convert to ET for display")
    print("  - Completed games have scores")
    print("  - No explicit game ID - create from date+teams")
    print("=" * 60)
