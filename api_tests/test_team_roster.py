"""
Test different methods to get a team's roster
"""
from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import Team

def test_roster_via_season_totals():
    """Method 1: Get roster by filtering season totals"""
    print("=" * 60)
    print("METHOD 1: Roster via Season Totals")
    print("=" * 60)
    print("\n📝 Filter players_season_totals() by team")

    test_teams = [
        Team.BOSTON_CELTICS,
        Team.GOLDEN_STATE_WARRIORS,
        Team.LOS_ANGELES_LAKERS
    ]

    try:
        print("\n⏳ Fetching all player season totals...")
        all_players = client.players_season_totals(season_end_year=2026)
        print(f"✅ Fetched {len(all_players)} total players")

        for team in test_teams:
            print(f"\n{'='*60}")
            print(f"🏀 {team.value} Roster")
            print('='*60)

            # Filter by team
            roster = [p for p in all_players if p.get('team') == team]

            if roster:
                print(f"\n📊 Found {len(roster)} players")

                # Sort by games played
                roster.sort(key=lambda x: x.get('games_played', 0), reverse=True)

                # Show top 10 players
                for i, player in enumerate(roster[:10], 1):
                    name = player.get('name', 'Unknown')
                    games = player.get('games_played', 0)
                    slug = player.get('slug', 'N/A')

                    print(f"  {i:2d}. {name:30s} - {games} GP, slug: {slug}")

                if len(roster) > 10:
                    print(f"  ... and {len(roster) - 10} more players")

                # Show what data we get
                if roster:
                    print(f"\n📋 Available fields per player:")
                    for key in sorted(roster[0].keys())[:15]:
                        print(f"  - {key}")
                    print("  ... (more fields)")

            else:
                print(f"⚠️  No players found for {team.value}")

            # Only show first team in detail
            break

        print("\n✅ Method 1 works!")
        print("   Pros: Simple, gets all data at once")
        print("   Cons: Fetches all 380+ players even if we only need 1 team")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_if_direct_roster_method_exists():
    """Check if there's a direct team_roster() method"""
    print("\n" + "=" * 60)
    print("METHOD 2: Check for Direct Roster Method")
    print("=" * 60)

    # Check all available methods
    roster_methods = [m for m in dir(client) if 'roster' in m.lower() or 'team' in m.lower()]

    print(f"\n🔍 Methods with 'roster' or 'team' in name:")
    if roster_methods:
        for method in roster_methods:
            if not method.startswith('_') and callable(getattr(client, method, None)):
                print(f"  ✅ {method}")
    else:
        print("  ⚠️  No direct roster methods found")

    # Check team-related methods
    print(f"\n📋 All available client methods:")
    all_methods = [m for m in dir(client) if not m.startswith('_') and callable(getattr(client, m, None))]

    team_related = [m for m in all_methods if 'team' in m.lower()]
    print(f"\n🏀 Team-related methods:")
    for m in team_related:
        print(f"  - {m}")

    if not team_related:
        print("  ⚠️  No team-specific roster methods available")

    print("\n💡 Conclusion:")
    print("   No direct team_roster() method exists")
    print("   Must use Method 1: filter season_totals by team")

def test_practical_roster_workflow():
    """Show practical workflow for getting game rosters"""
    print("\n" + "=" * 60)
    print("PRACTICAL WORKFLOW: Game Rosters")
    print("=" * 60)
    print("\n📝 Scenario: User selects a game, we need both rosters")

    try:
        # Step 1: Get today's games
        print("\n1️⃣ Get schedule...")
        schedule = client.season_schedule(season_end_year=2026)

        from datetime import date
        try:
            from zoneinfo import ZoneInfo
        except ImportError:
            from backports.zoneinfo import ZoneInfo

        et_tz = ZoneInfo('America/New_York')

        # Find a game on opening night
        test_date = date(2025, 10, 22)
        games = [g for g in schedule if g['start_time'].astimezone(et_tz).date() == test_date]

        if games:
            game = games[0]
            home_team = game['home_team']
            away_team = game['away_team']

            print(f"   ✅ Found game: {away_team.value} @ {home_team.value}")

            # Step 2: Get all players (we'll cache this)
            print(f"\n2️⃣ Fetch player season totals...")
            all_players = client.players_season_totals(season_end_year=2026)
            print(f"   ✅ Fetched {len(all_players)} players")

            # Step 3: Filter for both teams
            print(f"\n3️⃣ Filter rosters for both teams...")
            home_roster = [p for p in all_players if p.get('team') == home_team]
            away_roster = [p for p in all_players if p.get('team') == away_team]

            print(f"   ✅ Home team ({home_team.value}): {len(home_roster)} players")
            print(f"   ✅ Away team ({away_team.value}): {len(away_roster)} players")

            # Step 4: For each player, we'll need their identifier
            print(f"\n4️⃣ Get player identifiers...")

            # Show example with first 3 players from home team
            print(f"\n   Home team roster (first 3):")
            for i, player in enumerate(home_roster[:3], 1):
                name = player.get('name', 'Unknown')

                # Check if slug is in the data
                if 'slug' in player:
                    slug = player['slug']
                    print(f"      {i}. {name} - slug: {slug} ✅")
                else:
                    # Need to search
                    print(f"      {i}. {name} - no slug, need to search")

                    # Try searching
                    search_results = client.search(term=name)
                    players_found = search_results.get('players', [])

                    if players_found:
                        identifier = players_found[0].get('identifier')
                        print(f"          Search found: {identifier} ✅")
                    else:
                        print(f"          Search failed ❌")

            print(f"\n✅ Complete workflow:")
            print(f"   1. Get game from schedule")
            print(f"   2. Extract home_team and away_team")
            print(f"   3. Fetch all season totals (cache this!)")
            print(f"   4. Filter by team to get rosters")
            print(f"   5. For each player, get identifier (from data or search)")
            print(f"   6. Fetch game logs for each player")
            print(f"   7. Generate predictions")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_caching_strategy():
    """Show optimal caching strategy"""
    print("\n" + "=" * 60)
    print("CACHING STRATEGY")
    print("=" * 60)

    print("\n💡 Optimal approach for our app:")
    print("\n1️⃣ On app startup / daily:")
    print("   - Fetch players_season_totals() ONCE")
    print("   - Store in database with team mapping")
    print("   - This gives us ~380 players")

    print("\n2️⃣ When user selects a game:")
    print("   - Query database for players on home_team")
    print("   - Query database for players on away_team")
    print("   - Get their identifiers from cache")

    print("\n3️⃣ For each player:")
    print("   - Check if we have their game logs in DB")
    print("   - If not, or if stale, fetch and cache")
    print("   - Generate prediction from cached data")

    print("\n✅ Benefits:")
    print("   - Fetch season_totals only once per day")
    print("   - All roster lookups are instant (from DB)")
    print("   - Only scrape individual game logs when needed")
    print("   - Respectful to Basketball Reference")

if __name__ == "__main__":
    print("\n🏀 Team Roster Retrieval Tests\n")

    test_roster_via_season_totals()
    test_if_direct_roster_method_exists()
    test_practical_roster_workflow()
    test_caching_strategy()

    print("\n" + "=" * 60)
    print("✅ Roster tests complete!")
    print("=" * 60)
    print("\n📝 KEY FINDINGS:")
    print("  ❌ No direct team_roster(team) method exists")
    print("  ✅ Must use: players_season_totals() + filter by team")
    print("  ✅ This gives us all players on a team")
    print("  ✅ Each player has name, team, games_played, stats")
    print("  ⚠️  May or may not have 'slug' field")
    print("  ✅ If no slug, use client.search(name) to get identifier")
    print("\n📝 IMPLEMENTATION:")
    print("  1. Cache players_season_totals() daily")
    print("  2. Filter by team when needed")
    print("  3. Build player name → identifier mapping")
    print("  4. Fetch game logs only when needed")
    print("=" * 60)
