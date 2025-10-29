# Basketball Reference API Testing

This directory contains isolated test scripts to explore the `basketball_reference_web_scraper` library capabilities.

## Purpose

These test scripts were used to:
- Understand available API endpoints
- Test data structures and return values
- Document findings for the DATA_SOURCE_GUIDE

**📚 For complete API documentation, see [../docs/DATA_SOURCE_GUIDE.md](../docs/DATA_SOURCE_GUIDE.md)**

---

## Quick Setup

### 1. Activate Virtual Environment
```bash
cd api_tests
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `basketball-reference-web-scraper` - NBA data scraping library
- `requests` - HTTP library (dependency)
- `python-dateutil` - Date utilities (dependency)

---

## Test Scripts

| Script | Purpose |
|--------|---------|
| `test_schedule.py` | Test fetching game schedules |
| `test_player_stats.py` | Test player season stats and game logs |
| `test_team_data.py` | Test team rosters and data |
| `explore_data_structure.py` | Explore API data structures |

---

## Running Tests

### Run Individual Tests
```bash
python test_schedule.py
python test_player_stats.py
python test_team_data.py
```

### Run All Tests
```bash
./run_all_tests.sh  # If available
```

---

## Key Findings

These tests produced the comprehensive documentation in:
**[../docs/DATA_SOURCE_GUIDE.md](../docs/DATA_SOURCE_GUIDE.md)**

Key discoveries:
- ✅ 9 available API endpoints
- ✅ Player slugs included in `players_season_totals()`
- ✅ Stats are season totals (not per-game averages)
- ⚠️ Timezone issue: All times in UTC (convert to ET!)
- ✅ Smart caching strategy for 60x performance improvement

---

## Notes

- **Be respectful:** The library scrapes Basketball Reference - use caching!
- **Request speed:** Some requests take 2-5 seconds to complete
- **Player identifiers:** Use Basketball Reference slugs (e.g., 'jamesle01' for LeBron)
- **Season format:** Year is the ending year (e.g., 2026 for 2025-26 season)

---

## Next Steps

1. ✅ API testing complete
2. ✅ Comprehensive documentation created
3. ⏭️ Implement backend scraper service using findings
4. ⏭️ Build smart caching system in PostgreSQL

---

**For full API reference, usage examples, and best practices:**
👉 **[../docs/DATA_SOURCE_GUIDE.md](../docs/DATA_SOURCE_GUIDE.md)**

---

**Last Updated:** October 29, 2025
