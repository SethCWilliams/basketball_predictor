"""
Script to explore and document the data structures returned by the API
"""
from basketball_reference_web_scraper import client
import json
from pprint import pprint

def explore_schedule_structure():
    """Deep dive into schedule data structure"""
    print("=" * 60)
    print("EXPLORING: Schedule Data Structure")
    print("=" * 60)

    try:
        schedule = client.season_schedule(season_end_year=2026)

        if schedule:
            game = schedule[0]

            print("\n📋 First game (full structure):")
            print("\nType:", type(game))

            # If it's an object with attributes
            if hasattr(game, '__dict__'):
                print("\nAttributes:")
                pprint(game.__dict__, indent=2)

            # If it's a dictionary
            if isinstance(game, dict):
                print("\nDictionary keys and values:")
                for key, value in game.items():
                    print(f"\n{key}:")
                    print(f"  Type: {type(value)}")
                    print(f"  Value: {value}")

            # Try common attributes
            print("\n🔍 Accessing common attributes:")
            attrs = ['home_team', 'away_team', 'start_time', 'date']
            for attr in attrs:
                try:
                    value = getattr(game, attr) if hasattr(game, attr) else game.get(attr, 'N/A')
                    print(f"  {attr}: {value} (type: {type(value).__name__})")
                except Exception as e:
                    print(f"  {attr}: Error - {e}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def explore_player_stats_structure():
    """Deep dive into player stats data structure"""
    print("\n" + "=" * 60)
    print("EXPLORING: Player Stats Data Structure")
    print("=" * 60)

    try:
        stats = client.players_season_totals(season_end_year=2026)

        if stats:
            player = stats[0]

            print("\n📋 First player (full structure):")
            print("\nType:", type(player))

            if isinstance(player, dict):
                print("\n📊 All available fields:")
                print("-" * 60)

                for key, value in sorted(player.items()):
                    value_str = str(value)
                    if len(value_str) > 50:
                        value_str = value_str[:47] + "..."

                    print(f"{key:35s} : {type(value).__name__:15s} = {value_str}")

            # Find a player with good stats to show meaningful data
            print("\n🔍 Looking for active player with substantial minutes...")

            active_players = [p for p in stats if p.get('games_played', 0) > 10]

            if active_players:
                active = active_players[0]
                print(f"\n📊 Sample active player: {active.get('name', 'Unknown')}")
                print(f"   Team: {active.get('team', 'N/A')}")
                print(f"   Games: {active.get('games_played', 0)}")
                print(f"   Made FG: {active.get('made_field_goals', 0)}")
                print(f"   Made 3P: {active.get('made_three_point_field_goals', 0)}")
                print(f"   Total Rebounds: {active.get('offensive_rebounds', 0) + active.get('defensive_rebounds', 0)}")
                print(f"   Assists: {active.get('assists', 0)}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def explore_game_log_structure():
    """Deep dive into game log data structure"""
    print("\n" + "=" * 60)
    print("EXPLORING: Game Log Data Structure")
    print("=" * 60)

    # Try multiple players
    test_players = ['curryst01', 'jamesle01', 'monkma01']

    for player_slug in test_players:
        try:
            print(f"\n🏀 Trying player: {player_slug}")

            game_logs = client.regular_season_player_box_scores(
                player_identifier=player_slug,
                season_end_year=2026
            )

            if game_logs:
                game = game_logs[0]

                print(f"✅ Found {len(game_logs)} games")
                print("\n📋 First game log (full structure):")
                print("\nType:", type(game))

                if isinstance(game, dict):
                    print("\n📊 All available fields:")
                    print("-" * 60)

                    for key, value in sorted(game.items()):
                        value_str = str(value)
                        if len(value_str) > 50:
                            value_str = value_str[:47] + "..."

                        print(f"{key:35s} : {type(value).__name__:15s} = {value_str}")

                break  # Success, exit loop

        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
            continue

def compare_data_formats():
    """Compare how to calculate common stats from the raw data"""
    print("\n" + "=" * 60)
    print("CALCULATING: Common Stats from Raw Data")
    print("=" * 60)

    try:
        stats = client.players_season_totals(season_end_year=2026)

        # Find a player with good data
        active = [p for p in stats if p.get('games_played', 0) > 10][0]

        print(f"\n🏀 Player: {active.get('name', 'Unknown')}")
        print(f"   Games Played: {active.get('games_played', 0)}")

        print("\n📊 CALCULATIONS:")

        # Points
        fgm = active.get('made_field_goals', 0)
        fg3m = active.get('made_three_point_field_goals', 0)
        ftm = active.get('made_free_throws', 0)
        total_points = (fgm * 2) + fg3m + ftm  # 2pts for FG, 3pts counted separately, 1pt for FT

        print(f"\nPoints:")
        print(f"  Formula: (FGM * 2) + 3PM + FTM")
        print(f"  Calculation: ({fgm} * 2) + {fg3m} + {ftm} = {total_points}")

        # Rebounds
        oreb = active.get('offensive_rebounds', 0)
        dreb = active.get('defensive_rebounds', 0)
        total_reb = oreb + dreb

        print(f"\nRebounds:")
        print(f"  Formula: OREB + DREB")
        print(f"  Calculation: {oreb} + {dreb} = {total_reb}")

        # FG%
        fga = active.get('attempted_field_goals', 0)
        fg_pct = (fgm / fga * 100) if fga > 0 else 0

        print(f"\nField Goal %:")
        print(f"  Formula: (FGM / FGA) * 100")
        print(f"  Calculation: ({fgm} / {fga}) * 100 = {fg_pct:.1f}%")

        # Per game averages
        games = active.get('games_played', 1) or 1

        print(f"\nPer Game Averages:")
        print(f"  PPG: {total_points / games:.1f}")
        print(f"  RPG: {total_reb / games:.1f}")
        print(f"  APG: {active.get('assists', 0) / games:.1f}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n🔍 Basketball Reference API Data Structure Explorer\n")

    explore_schedule_structure()
    explore_player_stats_structure()
    explore_game_log_structure()
    compare_data_formats()

    print("\n" + "=" * 60)
    print("✅ Exploration complete!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("  1. Schedule returns list of game objects with home/away teams and dates")
    print("  2. Player stats returns dictionaries with season totals")
    print("  3. Game logs provide per-game statistics")
    print("  4. Points = (FGM * 2) + 3PM + FTM")
    print("  5. Player identifiers use Basketball Reference slugs")
    print("=" * 60)
