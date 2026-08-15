"""
Bonus - Task: Fetch recent World Cup match data (2018, 2022, 2026) from
API-Football and merge it with the historical 1930-2014 dataset.

Run: python app/fetch_recent_matches.py

Note: Uses your existing .env API key. The World Cup league ID in
API-Football is 1. Free tier allows 100 requests/day - this script only
uses 3 requests (one per season), so it's safe to run.
"""

import os
import sys
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

WORLD_CUP_LEAGUE_ID = 1
SEASONS = [2018, 2022, 2026]

CLEANED_FOLDER = "data/cleaned"


def fetch_season_fixtures(season):
    response = requests.get(
        f"{BASE_URL}/fixtures",
        headers=HEADERS,
        params={"league": WORLD_CUP_LEAGUE_ID, "season": season},
        timeout=15,
    )
    if response.status_code != 200:
        print(f"❌ Failed to fetch season {season}: status {response.status_code}")
        return []
    data = response.json()
    print(f"✅ Season {season}: {data.get('results', 0)} fixtures found")
    return data.get("response", [])


def parse_fixtures_to_rows(fixtures, year):
    rows = []
    for f in fixtures:
        fixture = f["fixture"]
        teams = f["teams"]
        goals = f["goals"]
        league = f["league"]

        # Only keep matches that have actually been played (finished)
        if fixture["status"]["short"] != "FT":
            continue

        rows.append({
            "Year": year,
            "Datetime": fixture["date"],
            "Stage": league.get("round", "Unknown"),
            "Stadium": fixture["venue"].get("name", "Unknown"),
            "City": fixture["venue"].get("city", "Unknown"),
            "Home Team Name": teams["home"]["name"],
            "Home Team Goals": goals["home"],
            "Away Team Goals": goals["away"],
            "Away Team Name": teams["away"]["name"],
            "Win conditions": "",
            "Attendance": None,
            "Half-time Home Goals": None,
            "Half-time Away Goals": None,
            "Referee": fixture.get("referee", "Unknown"),
            "Assistant 1": "",
            "Assistant 2": "",
            "RoundID": None,
            "MatchID": fixture["id"],
            "Home Team Initials": teams["home"]["name"][:3].upper(),
            "Away Team Initials": teams["away"]["name"][:3].upper(),
        })
    return rows


if __name__ == "__main__":
    if not API_KEY:
        print("❌ No API key found. Make sure your .env file is set up correctly.")
        exit()

    all_rows = []
    for season in SEASONS:
        fixtures = fetch_season_fixtures(season)
        rows = parse_fixtures_to_rows(fixtures, season)
        all_rows.extend(rows)
        print(f"   → {len(rows)} completed matches added for {season}\n")

    if not all_rows:
        print("No recent match data was fetched. Check your API key and internet connection.")
        exit()

    recent_df = pd.DataFrame(all_rows)

    # Load existing historical data and combine
    historical_df = pd.read_csv(f"{CLEANED_FOLDER}/matches_clean.csv")

    combined_df = pd.concat([historical_df, recent_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=["MatchID"], keep="first")

    combined_df.to_csv(f"{CLEANED_FOLDER}/matches_clean.csv", index=False)

    print(f"\n🎉 Combined dataset saved: {combined_df.shape[0]} total matches")
    print(f"   (was {historical_df.shape[0]} historical + {len(all_rows)} recent)")
