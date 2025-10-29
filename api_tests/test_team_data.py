"""
Test script for fetching NBA team season statistics
"""
from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import Team
import json

def get_active_teams():
    """Get list of 30 currently active NBA teams"""
    active_teams = [
        'ATLANTA_HAWKS',
        'BOSTON_CELTICS',
        'BROOKLYN_NETS',
        'CHARLOTTE_HORNETS',
        'CHICAGO_BULLS',
        'CLEVELAND_CAVALIERS',
        'DALLAS_MAVERICKS',
        'DENVER_NUGGETS',
        'DETROIT_PISTONS',
        'GOLDEN_STATE_WARRIORS',
        'HOUSTON_ROCKETS',
        'INDIANA_PACERS',
        'LOS_ANGELES_CLIPPERS',
        'LOS_ANGELES_LAKERS',
        'MEMPHIS_GRIZZLIES',
        'MIAMI_HEAT',
        'MILWAUKEE_BUCKS',
        'MINNESOTA_TIMBERWOLVES',
        'NEW_ORLEANS_PELICANS',
        'NEW_YORK_KNICKS',
        'OKLAHOMA_CITY_THUNDER',
        'ORLANDO_MAGIC',
        'PHILADELPHIA_76ERS',
        'PHOENIX_SUNS',
        'PORTLAND_TRAIL_BLAZERS',
        'SACRAMENTO_KINGS',
        'SAN_ANTONIO_SPURS',
        'TORONTO_RAPTORS',
        'UTAH_JAZZ',
        'WASHINGTON_WIZARDS'
    ]

    teams = []
    for team in Team:
        if team.name in active_teams:
            teams.append(team)

    return teams

def test_active_teams():
    """Display all 30 active NBA teams"""
    print("=" * 60)
    print("TEST 1: Active NBA Teams")
    print("=" * 60)

    teams = get_active_teams()

    print(f"\n📋 Active NBA Teams (2025-26 Season): {len(teams)} teams\n")

    # Sort by team name for display
    sorted_teams = sorted(teams, key=lambda t: t.value)

    for i, team in enumerate(sorted_teams, 1):
        print(f"{i:2d}. {team.value:25s} ({team.name})")

    return teams

def test_team_season_stats():
    """Test fetching season statistics for teams"""
    print("\n" + "=" * 60)
    print("TEST 2: Team Season Statistics")
    print("=" * 60)

    try:
        season_year = 2026  # 2025-26 season
        print(f"\n🏀 Fetching team stats for {season_year-1}-{str(season_year)[-2:]} season...")

        # Check what methods are available for team stats
        available_methods = [method for method in dir(client) if 'team' in method.lower()]

        print(f"\n📊 Available team-related methods in client:")
        for method in available_methods:
            if not method.startswith('_'):
                print(f"   - {method}")

        # Try to get team stats
        # Note: The library may not have a direct team stats endpoint
        # We might need to aggregate from player or game data

        print("\n⚠️  Checking for direct team statistics endpoint...")

        # Try common method names
        if hasattr(client, 'team_stats_for_season'):
            print("✅ Found: team_stats_for_season")
            stats = client.team_stats_for_season(season_end_year=season_year)
            print(f"   Retrieved stats for {len(stats)} teams")

        elif hasattr(client, 'season_schedule'):
            print("✅ Found: season_schedule")
            print("   (Team stats can be calculated from schedule/results)")

        else:
            print("⚠️  No direct team stats endpoint found")
            print("   Team statistics will need to be calculated from:")
            print("   - Player aggregated stats")
            print("   - Game-by-game results")
            print("   - Schedule data")

    except Exception as e:
        print(f"❌ Error: {e}")

def test_team_data_structure():
    """Examine what data is available for each team"""
    print("\n" + "=" * 60)
    print("TEST 3: Team Data Structure")
    print("=" * 60)

    teams = get_active_teams()
    sample_team = teams[0]

    print(f"\n🔍 Examining Team enum structure:")
    print(f"   Sample team: {sample_team.value}")
    print(f"   Team attributes:")

    for attr in dir(sample_team):
        if not attr.startswith('_'):
            try:
                value = getattr(sample_team, attr)
                if not callable(value):
                    print(f"      - {attr}: {value}")
            except:
                pass

    print(f"\n📝 Team enum provides:")
    print(f"   - name: Internal enum name (e.g., {sample_team.name})")
    print(f"   - value: Display name (e.g., {sample_team.value})")
    print(f"\n💡 For season statistics, we'll need to:")
    print(f"   1. Query games/schedule using team enum")
    print(f"   2. Aggregate stats from game results")
    print(f"   3. Or aggregate player stats by team")

if __name__ == "__main__":
    print("\n🏀 Basketball Reference Team Season Stats API Tests\n")

    # Run tests
    test_active_teams()
    test_team_season_stats()
    test_team_data_structure()

    print("\n" + "=" * 60)
    print("✅ Team data tests complete!")
    print("=" * 60)
