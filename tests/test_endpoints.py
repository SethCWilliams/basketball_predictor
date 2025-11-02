#!/usr/bin/env python3
"""
Comprehensive endpoint testing for NBA Stats Tracker API
Tests all endpoints to ensure they're working correctly
"""

import requests
import sys
import time
from typing import Dict, Any, List, Tuple

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# API Configuration
API_BASE = "http://localhost:8000"
TIMEOUT = 30  # seconds


class EndpointTester:
    def __init__(self, base_url: str = API_BASE):
        self.base_url = base_url
        self.passed = 0
        self.failed = 0
        self.results: List[Tuple[str, bool, str]] = []

    def test(self, name: str, method: str, endpoint: str,
             expected_status: int = 200,
             params: Dict[str, Any] = None,
             validate_json: bool = True) -> bool:
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"

        print(f"\n{BLUE}Testing:{RESET} {name}")
        print(f"  URL: {url}")
        if params:
            print(f"  Params: {params}")

        try:
            start = time.time()

            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=TIMEOUT)
            elif method.upper() == "POST":
                response = requests.post(url, json=params, timeout=TIMEOUT)
            else:
                raise ValueError(f"Unsupported method: {method}")

            elapsed = (time.time() - start) * 1000  # ms

            # Check status code
            if response.status_code != expected_status:
                self._log_failure(name, f"Expected status {expected_status}, got {response.status_code}")
                return False

            # Check JSON response
            if validate_json:
                try:
                    data = response.json()
                except Exception as e:
                    self._log_failure(name, f"Invalid JSON response: {e}")
                    return False
            else:
                data = None

            self._log_success(name, f"{response.status_code} | {elapsed:.0f}ms")
            return True

        except requests.exceptions.Timeout:
            self._log_failure(name, f"Timeout after {TIMEOUT}s")
            return False
        except requests.exceptions.ConnectionError:
            self._log_failure(name, "Connection refused - is the server running?")
            return False
        except Exception as e:
            self._log_failure(name, f"Error: {str(e)}")
            return False

    def _log_success(self, name: str, details: str):
        """Log successful test"""
        self.passed += 1
        self.results.append((name, True, details))
        print(f"  {GREEN}✓ PASS{RESET} - {details}")

    def _log_failure(self, name: str, details: str):
        """Log failed test"""
        self.failed += 1
        self.results.append((name, False, details))
        print(f"  {RED}✗ FAIL{RESET} - {details}")

    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        print("\n" + "=" * 70)
        print(f"{BLUE}TEST SUMMARY{RESET}")
        print("=" * 70)

        for name, passed, details in self.results:
            status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
            print(f"{status} {name}: {details}")

        print("\n" + "=" * 70)
        print(f"Total: {total} | Passed: {GREEN}{self.passed}{RESET} | Failed: {RED}{self.failed}{RESET}")

        if self.failed == 0:
            print(f"\n{GREEN}🎉 All tests passed!{RESET}")
        else:
            print(f"\n{RED}⚠️  Some tests failed{RESET}")

        print("=" * 70)

        return self.failed == 0


def main():
    """Run all endpoint tests"""
    print(f"{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}NBA Stats Tracker API - Endpoint Tests{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}")
    print(f"Testing API at: {API_BASE}")
    print(f"Timeout: {TIMEOUT}s")

    tester = EndpointTester()

    # Test 1: Root endpoint
    tester.test(
        "Root Health Check",
        "GET",
        "/"
    )

    # Test 2: Health check
    tester.test(
        "API Health Check",
        "GET",
        "/api/health"
    )

    # Test 3: Stat categories
    tester.test(
        "Get Stat Categories",
        "GET",
        "/api/stats/categories"
    )

    # Test 4: Today's games
    tester.test(
        "Get Today's Games",
        "GET",
        "/api/games/today"
    )

    # Test 5: Player search
    tester.test(
        "Search Players (LeBron)",
        "GET",
        "/api/players/search",
        params={"q": "lebron"}
    )

    # Test 6: Player search (multiple results)
    tester.test(
        "Search Players (Curry)",
        "GET",
        "/api/players/search",
        params={"q": "curry"}
    )

    # Test 7: Get specific player
    # Note: This will trigger scraping if not cached (may take 30s)
    print(f"\n{YELLOW}Note: The following tests may take 30+ seconds on first run (scraping data){RESET}")

    tester.test(
        "Get Player (LeBron James)",
        "GET",
        "/api/players/jamesle01"
    )

    # Test 8: Get player stats
    tester.test(
        "Get Player Stats (Points, Last 15)",
        "GET",
        "/api/players/jamesle01/stats",
        params={
            "stat_category": "points",
            "games": 15
        }
    )

    # Test 9: Get player stats (different category)
    tester.test(
        "Get Player Stats (Assists, Last 10)",
        "GET",
        "/api/players/jamesle01/stats",
        params={
            "stat_category": "assists",
            "games": 10
        }
    )

    # Test 10: Calculate hit rate
    tester.test(
        "Calculate Hit Rate (Points, line=25.5)",
        "GET",
        "/api/players/jamesle01/hit-rate",
        params={
            "stat_category": "points",
            "line": 25.5,
            "games": 15
        }
    )

    # Test 11: Calculate hit rate (different line)
    tester.test(
        "Calculate Hit Rate (Assists, line=7.5)",
        "GET",
        "/api/players/jamesle01/hit-rate",
        params={
            "stat_category": "assists",
            "line": 7.5,
            "games": 15
        }
    )

    # Test 12: Recent games
    tester.test(
        "Get Recent Games",
        "GET",
        "/api/players/jamesle01/recent",
        params={"limit": 5}
    )

    # Test 13: Invalid player (should fail gracefully)
    print(f"\n{YELLOW}Testing error handling:{RESET}")
    tester.test(
        "Get Invalid Player (404 expected)",
        "GET",
        "/api/players/invalidplayer123",
        expected_status=404
    )

    # Print summary and exit
    success = tester.print_summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
