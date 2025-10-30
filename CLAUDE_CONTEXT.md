# Persistent Context for Claude Code

This document explains how to add persistent context to every conversation with Claude Code, so you don't have to repeat important project details.

## 📋 Project Context to Remember

### NBA Season Detection (Automatic!)
- **Detection Logic**: Use `get_current_season_year()` - don't hardcode!
  - Oct-Dec: season ends next year (Oct 2025 = 2025-26 = season_end_year 2026)
  - Jan-Sep: season ends current year
- **Season Format**: "2025-26" for display, 2026 for API calls

### Timezone Information
- **All basketball-reference data**: UTC timezone
- **Must convert to**: User's local timezone (default: America/New_York / EST/EDT)
- **Game times**: Always display with timezone (e.g., "7:00 PM EDT")
- **Use**: `format_game_time()` for all time displays

### Database Strategy
- **Development**: SQLite (`backend/nba_predictions.db`)
- **Production**: PostgreSQL (to be deployed on Railway)
- **Migration**: SQLAlchemy models work with both databases
- **Important**: Must `unset DATABASE_URL` before running backend (global env var conflicts)

### Tech Stack
- **Backend**: Python 3.12, FastAPI, SQLAlchemy, SQLite
- **Frontend**: SvelteKit, TypeScript, Tailwind CSS v3
- **Data Source**: basketball-reference-web-scraper library

## 🔧 How to Set Up Persistent Context

### ✅ Recommended Approach: Use the Project Context File

**The file already exists**: `backend/.claude/project-context.md`

Claude Code automatically looks for this file and will reference it in conversations. The file contains:
- Season detection logic (automatic, no hardcoded dates!)
- Timezone conversion requirements (UTC → EST/EDT)
- Database strategy (SQLite for dev, PostgreSQL for prod)
- Python version requirements (3.12 only)
- Common issues and solutions

**No action needed!** Just know it's there and Claude will use it.

### Alternative: Quick Reference at Session Start

If you ever need to remind Claude mid-conversation:

```
Context reminder:
- Season detection is automatic (get_current_season_year())
- All times are UTC → convert to EST/EDT
- SQLite for dev, PostgreSQL for prod
- Python 3.12 only
```

## ✅ What This Fixes

With the project context file, Claude will automatically:

1. ✅ Use automatic season detection (no hardcoded years!)
2. ✅ Convert UTC times to EST/EDT
3. ✅ Know SQLite is for dev, PostgreSQL is for production
4. ✅ Remember to unset DATABASE_URL before running backend
5. ✅ Use Python 3.12 (not 3.13)
6. ✅ Use proper timezone formatting for game times

## 📚 Additional Resources

- **Project Context File**: `backend/.claude/project-context.md` (auto-loaded by Claude)
- **Progress Tracking**: `PROGRESS.md`
- **Database Schema**: `docs/DATABASE_SCHEMA.md`
- **API Docs**: `http://localhost:8000/docs`
- **Full Project Plan**: `docs/PROJECT_PLAN.md`

---

**Context File Location**: `backend/.claude/project-context.md`
**Key Point**: No hardcoded dates! Season and timezone are handled automatically.
