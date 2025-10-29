#!/bin/bash

# Quick start script for running all API tests

echo "🏀 Basketball Reference API Test Suite"
echo "========================================"

# Check if venv is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo ""
    echo "⚠️  Virtual environment not activated!"
    echo "Please run:"
    echo "  source venv/bin/activate"
    echo ""
    exit 1
fi

# Check if dependencies are installed
if ! python -c "import basketball_reference_web_scraper" 2>/dev/null; then
    echo ""
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "Running test suite..."
echo ""

# Run each test
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Schedule Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python test_schedule.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Player Stats Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python test_player_stats.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Team Data Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python test_team_data.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Data Structure Explorer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python explore_data_structure.py

echo ""
echo "========================================"
echo "✅ All tests complete!"
echo "========================================"
