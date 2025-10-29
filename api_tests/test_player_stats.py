"""
Test script for fetching NBA player statistics
Focus on practical use cases: individual players and team rosters
"""
from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import Team
import json

def test_individual_player_game_logs():
    """Test fetching game logs for a specific player (PRIMARY USE CASE)"""
    print("=" * 60)
    print("TEST 1: Fetching Individual Player Game Logs")
    print("=" * 60)
    print("\n📝 This is how we'll fetch data in production:")
    print("   - User selects a game")
    print("   - We fetch game logs for each player in that game")
    print("   - We use the logs to generate predictions")

    # Test with a few known players
    test_players = [
        ('curryst01', 'Stephen Curry'),
        ('jamesle01', 'LeBron James'),
        ('tatumja01', 'Jayson Tatum'),
    ]

    for player_slug, player_name in test_players:
        print(f"\n{'='*60}")
        print(f"🏀 Fetching game logs for {player_name} ({player_slug})")
        print('='*60)

        try:
            game_logs = client.regular_season_player_box_scores(
                player_identifier=player_slug,
                season_end_year=2026
            )

            print(f"✅ Successfully fetched {len(game_logs)} games")

            if game_logs:
                # Show most recent 5 games
                recent_games = sorted(game_logs, key=lambda x: x['date'], reverse=True)[:5]

                print(f"\n📊 Last 5 games for {player_name}:")
                for i, game in enumerate(recent_games, 1):
                    # Calculate stats
                    fgm = game.get('made_field_goals', 0)
                    fg3m = game.get('made_three_point_field_goals', 0)
                    ftm = game.get('made_free_throws', 0)
                    points = (fgm * 2) + fg3m + ftm

                    oreb = game.get('offensive_rebounds', 0)
                    dreb = game.get('defensive_rebounds', 0)
                    rebounds = oreb + dreb

                    assists = game.get('assists', 0)
                    steals = game.get('steals', 0)
                    blocks = game.get('blocks', 0)
                    minutes = game.get('seconds_played', 0) / 60

                    print(f"\n  Game {i} - {game.get('date', 'Unknown')}")
                    print(f"    vs {game.get('opponent', 'N/A')} ({game.get('location', 'N/A')})")
                    print(f"    {minutes:.1f} MIN, {points} PTS, {rebounds} REB, {assists} AST")
                    print(f"    {steals} STL, {blocks} BLK")
                    print(f"    Outcome: {game.get('outcome', 'N/A')}")

                # Calculate season average from game logs
                if len(game_logs) > 0:
                    total_points = sum((g.get('made_field_goals', 0) * 2 +
                                       g.get('made_three_point_field_goals', 0) +
                                       g.get('made_free_throws', 0)) for g in game_logs)
                    total_rebounds = sum(g.get('offensive_rebounds', 0) + g.get('defensive_rebounds', 0) for g in game_logs)
                    total_assists = sum(g.get('assists', 0) for g in game_logs)

                    print(f"\n📈 Season Averages (from {len(game_logs)} games):")
                    print(f"    PPG: {total_points / len(game_logs):.1f}")
                    print(f"    RPG: {total_rebounds / len(game_logs):.1f}")
                    print(f"    APG: {total_assists / len(game_logs):.1f}")

                # Show all available fields (first game only)
                if player_slug == test_players[0][0]:  # Only show for first player
                    print(f"\n📋 Available fields in game log data:")
                    for key in sorted(game_logs[0].keys()):
                        value = game_logs[0][key]
                        value_str = str(value)[:30]
                        print(f"  - {key}: {value_str}")

            break  # Only test first successful player in detail

        except Exception as e:
            print(f"❌ Error fetching {player_name}: {e}")
            import traceback
            traceback.print_exc()
            continue

def test_team_roster_stats():
    """Test fetching stats for all players on a specific team"""
    print("\n" + "=" * 60)
    print("TEST 2: Fetching Team Roster Stats")
    print("=" * 60)
    print("\n📝 Use case: Get all players for a specific team in a game")

    # Test with a few teams (using Team enum)
    from basketball_reference_web_scraper.data import Team
    test_teams = [
        (Team.BOSTON_CELTICS, 'BOS'),
        (Team.LOS_ANGELES_LAKERS, 'LAL'),
        (Team.GOLDEN_STATE_WARRIORS, 'GSW')
    ]

    try:
        print(f"\n⏳ Fetching season totals (needed to filter by team)...")
        all_stats = client.players_season_totals(season_end_year=2026)
        print(f"✅ Fetched stats for {len(all_stats)} players")

        for team_enum, team_abbr in test_teams:
            print(f"\n{'='*60}")
            print(f"🏀 {team_abbr} Roster")
            print('='*60)

            # Filter for this team (team is stored as Team enum)
            team_players = [p for p in all_stats if p.get('team') == team_enum]

            if team_players:
                print(f"\n📊 Found {len(team_players)} players on {team_abbr}")

                # Sort by games played (most active first)
                team_players.sort(key=lambda x: x.get('games_played', 0), reverse=True)

                # Show top 10 players
                print(f"\nTop 10 players by games played:")
                for i, player in enumerate(team_players[:10], 1):
                    name = player.get('name', 'Unknown')
                    games = player.get('games_played', 0)

                    # Calculate stats
                    if games > 0:
                        fgm = player.get('made_field_goals', 0)
                        fg3m = player.get('made_three_point_field_goals', 0)
                        ftm = player.get('made_free_throws', 0)
                        points = (fgm * 2) + fg3m + ftm

                        rebounds = player.get('offensive_rebounds', 0) + player.get('defensive_rebounds', 0)
                        assists = player.get('assists', 0)

                        ppg = points / games
                        rpg = rebounds / games
                        apg = assists / games

                        print(f"  {i:2d}. {name:25s} - {games} GP, {ppg:.1f} PPG, {rpg:.1f} RPG, {apg:.1f} APG")
                    else:
                        print(f"  {i:2d}. {name:25s} - No games played yet")

            else:
                print(f"⚠️  No players found for team {team_abbr}")

            if team_abbr == test_teams[0]:
                break  # Only show one team in detail

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_player_slug_discovery():
    """Test how to find a player's slug (identifier)"""
    print("\n" + "=" * 60)
    print("TEST 3: Finding Player Slugs")
    print("=" * 60)
    print("\n📝 Problem: We need to map player names to their Basketball Reference slugs")
    print("   Solution: Search through season stats")

    try:
        print(f"\n⏳ Fetching all players to search...")
        all_stats = client.players_season_totals(season_end_year=2026)

        # Search for specific players
        search_names = ["LeBron", "Curry", "Durant", "Tatum"]

        print(f"\n🔍 Searching for players matching: {', '.join(search_names)}\n")

        for search_term in search_names:
            matches = [p for p in all_stats if search_term.lower() in p.get('name', '').lower()]

            if matches:
                print(f"\n'{search_term}' matches:")
                for player in matches[:3]:  # Show max 3 matches
                    name = player.get('name', 'Unknown')
                    team = player.get('team', 'N/A')
                    slug = player.get('slug', 'N/A')
                    print(f"  - {name:30s} ({team}) - slug: {slug}")
            else:
                print(f"\n'{search_term}': No matches found")

        print("\n💡 Key Insight:")
        print("   - We can search by partial name match")
        print("   - Each player has a 'slug' field (if available)")
        print("   - We'll need to build a player lookup table in our database")

    except Exception as e:
        print(f"❌ Error: {e}")

def test_data_structure_details():
    """Deep dive into what fields are available"""
    print("\n" + "=" * 60)
    print("TEST 4: Data Structure Deep Dive")
    print("=" * 60)

    try:
        # Get one player's game logs
        print(f"\n⏳ Fetching game logs for detailed analysis...")
        game_logs = client.regular_season_player_box_scores(
            player_identifier='curryst01',
            season_end_year=2026
        )

        if game_logs and len(game_logs) > 0:
            game = game_logs[0]

            print("\n📋 Complete field listing with sample values:")
            print("="*60)
            for key, value in sorted(game.items()):
                value_str = str(value)
                if len(value_str) > 40:
                    value_str = value_str[:37] + "..."
                print(f"{key:35s} : {type(value).__name__:10s} = {value_str}")

            print("\n💡 Key Fields for Predictions:")
            print("  - date: When the game occurred")
            print("  - opponent: Who they played against")
            print("  - location: HOME or AWAY")
            print("  - seconds_played: Total minutes (convert to minutes)")
            print("  - made_field_goals, made_three_point_field_goals, made_free_throws: For points")
            print("  - offensive_rebounds, defensive_rebounds: For total rebounds")
            print("  - assists, steals, blocks, turnovers: Core stats")
            print("  - outcome: W or L")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n🏀 Basketball Reference Player Stats API Tests")
    print("   Focus: Practical use cases for production\n")

    # Run tests
    test_individual_player_game_logs()
    test_team_roster_stats()
    test_player_slug_discovery()
    test_data_structure_details()

    print("\n" + "=" * 60)
    print("✅ Player stats tests complete!")
    print("=" * 60)
    print("\n📝 Key Takeaways:")
    print("  1. Use regular_season_player_box_scores(player_slug) for individual players")
    print("  2. Use players_season_totals() + filter by team for team rosters")
    print("  3. Player slugs can be found by searching season totals")
    print("  4. Game logs contain all data needed for predictions")
    print("  5. We'll cache this data in PostgreSQL to avoid repeated scraping")
    print("=" * 60)
