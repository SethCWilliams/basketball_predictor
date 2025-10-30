# Persistent Context for Claude Code

This document explains how to add persistent context to every conversation with Claude Code, so you don't have to repeat important project details.

## 📋 Project Context to Remember

### Current NBA Season
- **Season**: 2025-26
- **Season End Year**: 2026 (used in basketball-reference API)
- **Current Date**: October 30, 2025

### Timezone Information
- **All basketball-reference data**: UTC timezone
- **Must convert to**: User's local timezone (default: America/New_York / EST/EDT)
- **Game times**: Always display in user's local time with timezone abbreviation (e.g., "7:00 PM EDT")

### Database
- **Type**: SQLite (for development)
- **Location**: `backend/nba_predictions.db`
- **Environment Variable**: `DATABASE_URL=sqlite:///./nba_predictions.db`
- **Important**: Must `unset DATABASE_URL` before running backend (global env var conflicts)

### Tech Stack
- **Backend**: Python 3.12, FastAPI, SQLAlchemy, SQLite
- **Frontend**: SvelteKit, TypeScript, Tailwind CSS v3
- **Data Source**: basketball-reference-web-scraper library

## 🔧 How to Add Persistent Context to Claude Code

There are two ways to provide persistent context:

### Method 1: Project-Level Instructions (Recommended)

Create a file in your project that Claude can reference:

1. **Create `.claude/project-context.md`** in your project root:

```bash
mkdir -p .claude
cat > .claude/project-context.md << 'EOF'
# NBA Stats Tracker - Project Context

**Important Information for Every Conversation:**

## Current Season & Time
- Today's date: October 30, 2025
- Current NBA season: 2025-26 (season_end_year = 2026)
- All timestamps from basketball-reference API are in UTC
- Convert all times to America/New_York (EST/EDT) by default
- Display times as "7:00 PM EDT" format

## Environment
- Python version: 3.12 (NOT 3.13 - pydantic compatibility issues)
- Database: SQLite at `backend/nba_predictions.db`
- Must run: `unset DATABASE_URL` before starting backend
- Backend runs on port 8000, frontend on port 5173

## Key Architectural Decisions
- All data scraped from basketball-reference is in UTC
- Season year = end year (2025-26 season = 2026)
- Smart caching: scrape once, store in DB, update incrementally
- Timezone conversion happens at API layer
EOF
```

2. **Reference it in conversations**: Claude can read this file when needed

###Method 2: Claude Code Settings (Slash Commands)

You can create a custom slash command that includes context:

1. Create `.claude/commands/context.md`:

```bash
cat > .claude/commands/context.md << 'EOF'
Remember these critical details for this project:

1. **Current NBA Season**: 2025-26 (season_end_year = 2026)
2. **Today's Date**: October 30, 2025
3. **Timezone**: All API data is UTC, convert to America/New_York (EST/EDT) for display
4. **Python**: Version 3.12 only (3.13 has pydantic issues)
5. **Database**: SQLite, must `unset DATABASE_URL` before starting backend
6. **Ports**: Backend=8000, Frontend=5173

When working with dates/times:
- basketball-reference returns UTC
- Convert to user timezone (default EST/EDT)
- Display as "7:00 PM EDT"

When working with seasons:
- NBA season 2025-26 uses season_end_year=2026
- Automatically detect current season based on month (Oct-Dec = next year, Jan-Sep = current year)
EOF
```

2. **Use it**: Type `/context` at the start of conversations

### Method 3: Custom System Prompt (Advanced)

If you have access to Claude Code settings:

1. Open Claude Code settings
2. Find "Custom System Prompt" or "Project Instructions"
3. Add this text:

```
When working on the NBA Stats Tracker project located at ~/Code/personal_work/basketball_predictor:

CRITICAL CONTEXT:
- Current date: October 30, 2025
- Current NBA season: 2025-26 (season_end_year = 2026)
- All timestamps from basketball-reference API are in UTC
- Always convert times to America/New_York (EST/EDT) timezone
- Display format: "7:00 PM EDT"
- Python version: 3.12 (NOT 3.13)
- Database: SQLite, location: backend/nba_predictions.db
- Must unset DATABASE_URL environment variable before running backend

SEASON LOGIC:
- Oct-Dec: season ends next year (Oct 2025 = 2025-26 season = 2026)
- Jan-Sep: season ends current year (Jan 2026 = 2025-26 season = 2026)

TIMEZONE LOGIC:
- basketball-reference data: UTC
- Convert to: user timezone (default America/New_York)
- Format: "7:00 PM EDT" or "7:00 PM EST"
```

## 📝 Quick Reference for Each Session

If you don't set up persistent context, start each session with:

```
Quick context for this project:
- Current NBA season: 2025-26 (season_end_year=2026)
- All API times are UTC, convert to EST/EDT
- Python 3.12, SQLite database
- Run `unset DATABASE_URL` before starting backend
```

## ✅ What This Fixes

With persistent context, Claude will automatically:

1. ✅ Use correct season year (2026 for 2025-26 season)
2. ✅ Convert UTC times to your local timezone
3. ✅ Display times with timezone abbreviations
4. ✅ Remember to unset DATABASE_URL
5. ✅ Use Python 3.12 (not 3.13)
6. ✅ Know current date without asking

## 🧪 Testing the Context

After setting up, test by asking:

"What's the current NBA season?"
Expected: "2025-26 season (season_end_year = 2026)"

"Show me today's games"
Expected: Times displayed in EST/EDT, not UTC

"What Python version should I use?"
Expected: "Python 3.12 (3.13 has pydantic compatibility issues)"

## 📚 Additional Resources

- Project documentation: `docs/`
- Progress tracking: `PROGRESS.md`
- Database schema: `docs/DATABASE_SCHEMA.md`
- API endpoints: `http://localhost:8000/docs`

---

**Last Updated**: October 30, 2025
**Location**: `.claude/project-context.md` or `.claude/commands/context.md`
