"""
Test the client.search() method for finding player slugs
"""
from basketball_reference_web_scraper import client

def test_search_function():
    """Test the search function to find player identifiers"""
    print("=" * 60)
    print("TEST: Player Search Function")
    print("=" * 60)
    print("\n📝 This is THE solution for finding player slugs!")

    # Test searching for various players
    search_terms = [
        "LeBron James",
        "Stephen Curry",
        "Jayson Tatum",
        "Kevin Durant",
        "Giannis Antetokounmpo",
    ]

    for term in search_terms:
        print(f"\n{'='*60}")
        print(f"🔍 Searching for: '{term}'")
        print('='*60)

        try:
            results = client.search(term=term)

            # Results structure: {'players': [{'name': ..., 'identifier': ..., 'leagues': set()}]}
            players = results.get('players', [])

            if players:
                print(f"✅ Found {len(players)} player(s):\n")

                for i, player in enumerate(players, 1):
                    name = player.get('name', 'Unknown')
                    identifier = player.get('identifier', 'N/A')
                    leagues = player.get('leagues', set())

                    print(f"  {i}. {name}")
                    print(f"     Identifier: {identifier}")
                    print(f"     Leagues: {leagues if leagues else 'N/A'}")
                    print()

            else:
                print(f"⚠️  No players found for '{term}'")

        except Exception as e:
            print(f"❌ Error searching for '{term}': {e}")
            import traceback
            traceback.print_exc()

        # Only show first 3 searches in detail
        if search_terms.index(term) >= 2:
            print("\n... (showing first 3 searches)")
            break

def test_search_variations():
    """Test different search patterns"""
    print("\n" + "=" * 60)
    print("TEST: Search Pattern Variations")
    print("=" * 60)

    test_cases = [
        ("curry", "Partial last name"),
        ("stephen", "First name only"),
        ("tatum", "Last name only"),
        ("lebron", "First name only (unique)"),
        ("giannis", "First name only (unique spelling)"),
        ("jokic", "Last name"),
    ]

    for search_term, description in test_cases:
        print(f"\n🔍 {description}: '{search_term}'")

        try:
            results = client.search(term=search_term)
            players = results.get('players', [])

            if players:
                print(f"   ✅ Found {len(players)} result(s)")

                # Show first 3 results
                for player in players[:3]:
                    name = player.get('name', 'Unknown')
                    identifier = player.get('identifier', 'N/A')
                    print(f"      - {name} (slug: {identifier})")
            else:
                print(f"   ⚠️  No results")

        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_practical_usage():
    """Show practical usage for our app"""
    print("\n" + "=" * 60)
    print("TEST: Practical Usage Pattern")
    print("=" * 60)
    print("\n📝 How we'll use this in production:\n")

    print("Scenario: User wants stats for 'Jayson Tatum'")

    try:
        # Step 1: Search for the player
        print("\n1️⃣ Search for player...")
        search_results = client.search(term="Jayson Tatum")
        players = search_results.get('players', [])

        if players:
            # Step 2: Get the identifier from search results (first match)
            player = players[0]
            player_name = player.get('name', 'Unknown')
            player_identifier = player.get('identifier')

            print(f"   ✅ Found: {player_name}")
            print(f"   📝 Identifier: {player_identifier}")

            if len(players) > 1:
                print(f"   ℹ️  Note: Found {len(players)} matches, using first one")

            # Step 3: Fetch game logs using the identifier
            print(f"\n2️⃣ Fetch game logs for {player_identifier}...")
            game_logs = client.regular_season_player_box_scores(
                player_identifier=player_identifier,
                season_end_year=2026
            )

            print(f"   ✅ Fetched {len(game_logs)} games")

            if game_logs:
                # Step 4: Show recent stats
                recent = sorted(game_logs, key=lambda x: x['date'], reverse=True)[:3]

                print(f"\n3️⃣ Last 3 games:")
                for game in recent:
                    points = game.get('points_scored', 0)
                    rebounds = (game.get('offensive_rebounds', 0) +
                               game.get('defensive_rebounds', 0))
                    assists = game.get('assists', 0)
                    print(f"      {game['date']}: {points} PTS, {rebounds} REB, {assists} AST")

                print(f"\n✅ Complete workflow successful!")

        else:
            print("   ⚠️  Player not found")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_ambiguous_searches():
    """Test searches that might return multiple results"""
    print("\n" + "=" * 60)
    print("TEST: Handling Ambiguous Searches")
    print("=" * 60)
    print("\n📝 What happens when search returns multiple players?\n")

    ambiguous_terms = [
        "James",      # Should match multiple players
        "Curry",      # Stephen, Seth, Dell
        "Thompson",   # Multiple Thompsons
    ]

    for term in ambiguous_terms:
        print(f"\n🔍 Searching for: '{term}'")

        try:
            results = client.search(term=term)
            players = results.get('players', [])

            if players:
                print(f"   ✅ Found {len(players)} player(s):")

                for i, player in enumerate(players[:5], 1):  # Show max 5
                    print(f"      {i}. {player.get('name')} ({player.get('identifier')})")

                if len(players) > 5:
                    print(f"      ... and {len(players) - 5} more")

                print(f"\n   💡 Insight: Need disambiguation strategy!")
                print(f"      - Show all matches to user")
                print(f"      - Let user pick the right one")
                print(f"      - Or use additional context (team, etc.)")

            else:
                print(f"   ⚠️  No results")

        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("\n🏀 Basketball Reference Search API Tests\n")

    test_search_function()
    test_search_variations()
    test_practical_usage()
    test_ambiguous_searches()

    print("\n" + "=" * 60)
    print("✅ Search tests complete!")
    print("=" * 60)
    print("\n💡 KEY FINDINGS:")
    print("  ✅ client.search(term) returns: {'players': [...]}")
    print("  ✅ Each player has 'name', 'identifier', 'leagues'")
    print("  ✅ 'identifier' is the slug we need for game logs")
    print("  ✅ Can search by full name, partial name, first or last")
    print("  ✅ May return multiple matches - need disambiguation")
    print("  ✅ We should cache player name → identifier mappings")
    print("\n📝 Implementation Strategy:")
    print("  1. User selects a game from schedule")
    print("  2. Get team rosters for that game")
    print("  3. For each player on roster, search for identifier")
    print("  4. Cache player mappings in database")
    print("  5. Fetch game logs for each player")
    print("  6. Generate predictions")
    print("=" * 60)
