# NBA Player Stats Tracker - PropsMadness Style

A PropsMadness-inspired web application for tracking and analyzing NBA player performance with interactive charts and comprehensive filtering.

## 🎯 Project Vision

Build a professional-grade NBA player stats tracking app that allows users to:
- Browse today's NBA games
- View detailed player performance history with interactive charts
- Analyze stats across 20 different categories (Points, Assists, Rebounds, etc.)
- Apply advanced filters (H2H matchups, Home/Away splits, Back-to-back games)
- Track hit rates against betting lines
- Make informed decisions about player performance

## ⭐ Design Reference

This app is based on the PropsMadness interface with detailed specifications documented in our project plan.

## 🏗️ Tech Stack

### Frontend
- **SvelteKit** - Modern web framework
- **Tailwind CSS** - Utility-first styling
- **Skeleton UI** - Svelte-native components
- **Chart.js / Recharts** - Interactive performance charts

### Backend
- **FastAPI (Python)** - High-performance API
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Relational database
- **basketball_reference_web_scraper** - NBA data source

### Deployment
- **Railway** - Full-stack hosting platform

## 📚 Documentation

**Start here to understand the project:**

### 📖 Essential Reading
1. **[docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md)** ⭐ **THE NORTH STAR**
   - Complete PropsMadness UI/UX specifications
   - All component details (sidebar, header, chart, filters)
   - Data requirements
   - Implementation phases

2. **[docs/ROADMAP.md](docs/ROADMAP.md)**
   - 12-week development timeline
   - Phased milestones and tasks
   - Success criteria for each phase

### 🔧 Implementation Guides
3. **[docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)**
   - Complete database design
   - Table structures and relationships
   - Query patterns

4. **[docs/IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md)**
   - Step-by-step build guide
   - Code examples
   - Smart caching strategy

### 📘 Reference Documentation
5. **[docs/ARCHITECTURE_DECISIONS.md](docs/ARCHITECTURE_DECISIONS.md)**
   - All tech stack decisions
   - Rationale and trade-offs

6. **[docs/DATA_SOURCE_GUIDE.md](docs/DATA_SOURCE_GUIDE.md)**
   - Basketball Reference API details
   - Available data and limitations

7. **[docs/INDEX.md](docs/INDEX.md)**
   - Complete documentation index
   - Quick navigation guide

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+

### Development Setup

**1. Clone the repository**
```bash
git clone <repository-url>
cd basketball_predictor
```

**2. Explore the API (Current Phase)**
```bash
cd api_tests
source venv/bin/activate
pip install -r requirements.txt
python test_schedule.py
python test_player_stats.py
```

**3. Set up PostgreSQL**
```bash
# macOS with Homebrew
brew install postgresql@15
brew services start postgresql@15
createdb nba_predictions
```

**4. Next Steps**
See [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) Phase 0 for detailed setup instructions.

## 🎨 Key Features

### Core Interface (Phase 1 - Weeks 1-4)
- ✅ **Left Sidebar Navigation**
  - All games view
  - Search by player/team
  - Single game roster view

- ✅ **Top Navigation**
  - 20 stat categories
  - Real-time category switching

- ✅ **Player Header**
  - Season average
  - Graph average (filtered)
  - Hit rate calculation

- ✅ **Interactive Performance Chart**
  - Bar chart with game-by-game performance
  - Draggable betting line
  - Real-time hit rate updates
  - Game hover tooltips

- ✅ **Filter Controls**
  - Season selector (23/24, 24/25, 25/26, All)
  - Games counter (L15, Max)

### Advanced Features (Phase 2 - Weeks 5-7)
- 🔄 **Splits Filters**
  - H2H (Head-to-head)
  - Home/Away
  - Regular season/Playoffs
  - Back-to-back games

- 🔄 **Betting Lines Integration**
  - Real betting lines display
  - Historical closing lines

### Secondary Components (Phase 3 - Weeks 8-10)
- 📊 **Shooting Zones** (for Points category)
- 👥 **Similar Players** analysis
- 🎯 **Play Type Breakdown** (Transition, PnR, etc.)
- 📈 **Advanced Filters** with chart overlays

## 📊 Data Requirements

### Core Data (MVP)
- **Players**: 600+ active NBA players
- **Games**: Schedule and results
- **Game Logs**: Player performance per game
- **Teams**: 30 NBA teams
- **Betting Lines**: Historical and current lines

### Smart Caching Strategy
1. **First Request**: Scrape full player history → Store in PostgreSQL
2. **Subsequent Requests**: Query database (100x faster)
3. **Incremental Updates**: Only scrape new games when needed

## 🗓️ Development Timeline

- **Week 1**: API exploration, database setup, project scaffolding
- **Weeks 2-4**: Core MVP (sidebar, chart, basic filters)
- **Weeks 5-7**: Advanced filters and betting lines
- **Weeks 8-10**: Secondary components
- **Weeks 11-12**: Polish, optimization, deployment

**Target Launch**: Week 12

## 📈 Current Status

**Current Phase**: Phase 0 - Foundation & API Exploration
**Next Milestone**: Complete API testing and database setup
**Progress**: 📊 Planning Complete | 🚧 Development Starting

## 🤝 Contributing

This is currently a personal project. Documentation is structured to be comprehensive for solo development and future collaboration.

## 📝 License

TBD

---

**Last Updated**: October 29, 2025
**Version**: 2.0 (PropsMadness Edition)
