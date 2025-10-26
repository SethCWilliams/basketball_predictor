# NBA Player Stat Prediction App

## Project Vision
A web application that predicts NBA player statistics for upcoming games, helping users make informed decisions about player performance before games happen.

## Core Features

### 1. Today's Games Dashboard
- Display all NBA games scheduled for today
- Show matchup information (Team A vs Team B)
- Display game time and venue
- Quick preview of key predictions (optional: win probability, total points)

### 2. Game Detail Page
- Two tables (one per team) showing predicted stat lines for each player
- Predicted stats should include:
  - Points
  - Rebounds
  - Assists
  - Steals
  - Blocks
  - Field Goal %
  - 3-Point %
  - Minutes played
- Overall game prediction (winner, score prediction, confidence level)
- Historical context (team recent performance, head-to-head stats)

## Tech Stack (FINALIZED)

### Frontend
- **SvelteKit** - Modern, fast, small bundles
- **Tailwind CSS** - Utility-first styling
- **Skeleton UI** - Svelte-native component library

### Backend
- **FastAPI (Python)** - Required for basketball_reference_web_scraper
- **SQLAlchemy** - ORM for database operations
- **basketball_reference_web_scraper** - Data source

### Database
- **PostgreSQL** - Relational database for smart caching
- **Smart Caching Strategy:**
  - First request → Scrape full career → Save to DB
  - Subsequent requests → Query DB (100x faster!)
  - Incremental updates → Only scrape new games

### Deployment
- **Railway** - Single platform for frontend + backend + database

## Development Phases

### Phase 1: MVP (Minimum Viable Product)
- [ ] Set up project structure
- [ ] Integrate NBA schedule API
- [ ] Create basic UI for today's games
- [ ] Implement simple prediction algorithm (e.g., season averages + recent form)
- [ ] Build game detail page with predicted stats tables

### Phase 2: Enhanced Predictions
- [ ] Improve prediction algorithm with more factors
- [ ] Add historical accuracy tracking
- [ ] Include injury reports and player status
- [ ] Add matchup-specific adjustments

### Phase 3: Polish & Features
- [ ] Improve UI/UX
- [ ] Add filtering and sorting
- [ ] Display confidence intervals
- [ ] Add player comparison features
- [ ] Performance optimizations

## Getting Started

### 📚 Documentation Overview

**Start Here:**
- **[QUICK_START.md](QUICK_START.md)** - Summary and first steps
- **[ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md)** - All tech decisions (COMPLETE ✅)

**Implementation:**
- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - Step-by-step build guide with complete code
- **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Complete database design

**Reference:**
- **[TECHNICAL_REQUIREMENTS.md](TECHNICAL_REQUIREMENTS.md)** - Detailed requirements
- **[ROADMAP.md](ROADMAP.md)** - Development phases
- **[DATA_SOURCE_GUIDE.md](DATA_SOURCE_GUIDE.md)** - Basketball Reference scraper info
- **[CLAUDE_CODE_PROMPTS.md](CLAUDE_CODE_PROMPTS.md)** - Prompts for Claude Code

### 🚀 Quick Start

1. **Read** [QUICK_START.md](QUICK_START.md) for overview
2. **Set up** PostgreSQL database (see [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md))
3. **Build** backend following [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
4. **Build** frontend using provided examples
5. **Deploy** to Railway

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- basketball_reference_web_scraper Python library

## Project Structure
```
/
├── frontend/          # UI components and pages
├── backend/           # API and business logic
├── models/            # Prediction algorithms
├── data/              # Data fetching and processing
├── docs/              # Additional documentation
└── tests/             # Test files
```

## Data Flow
1. User opens app → Fetch today's NBA schedule
2. User selects game → Fetch team rosters and recent stats
3. Run prediction algorithm → Generate stat predictions
4. Display results in formatted tables

## Notes & Decisions to Make
- **Prediction complexity:** Start simple or go straight to ML?
- **Real-time vs cached:** How often to refresh data?
- **Mobile-first:** Should we prioritize mobile design?
- **Monetization:** Free tool or premium features?

## Future Enhancements
- User accounts and prediction history
- Compare predictions vs actual results
- Fantasy basketball integration
- Props betting insights
- Player vs player comparisons
- Historical game data visualization

---

**Status:** Planning Phase
**Last Updated:** October 2025
