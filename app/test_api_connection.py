"""
Day 1 - Task: Verify API-Football connection is working.

Steps before running:
1. Sign up at https://dashboard.api-football.com/register (free tier)
2. Find your key under Account -> My Access
3. Rename .env.example to .env, paste key inside
4. Run: pip install -r requirements.txt
5. Run: python app/test_api_connection.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_FOOTBALL_KEY")

BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY,
}


def test_connection():
    """Simple check: fetch today's fixtures to confirm API key + connection work."""
    url = f"{BASE_URL}/fixtures"
    params = {"date": "2026-07-14"}  # World Cup semi-final date, good test day

    response = requests.get(url, headers=HEADERS, params=params, timeout=10)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Connection successful. Matches found: {data.get('results', 0)}")
        if data.get("response"):
            first_match = data["response"][0]
            teams = first_match["teams"]
            print(f"Sample match: {teams['home']['name']} vs {teams['away']['name']}")
    else:
        print(f"❌ Failed. Status code: {response.status_code}")
        print(response.text)


def fetch_live_fixtures():
    """Fetch currently live matches (use this during actual live match testing)."""
    url = f"{BASE_URL}/fixtures"
    params = {"live": "all"}

    response = requests.get(url, headers=HEADERS, params=params, timeout=10)

    if response.status_code == 200:
        data = response.json()
        print(f"Live matches right now: {data.get('results', 0)}")
        for match in data.get("response", []):
            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            score_home = match["goals"]["home"]
            score_away = match["goals"]["away"]
            elapsed = match["fixture"]["status"]["elapsed"]
            print(f"{home} {score_home} - {score_away} {away} ({elapsed}')")
    else:
        print(f"❌ Failed. Status code: {response.status_code}")


if __name__ == "__main__":
    print("Testing API-Football connection...\n")
    test_connection()
    print("\nChecking for any live matches...\n")
    fetch_live_fixtures()
