"""
Day 11 - Task: Test edge cases in the core logic.

Run: python app/test_edge_cases.py
This checks that functions handle unusual/invalid inputs gracefully
instead of crashing.
"""

import pandas as pd
import numpy as np

CLEANED_FOLDER = "data/cleaned"


def cosine_similarity(vec1, vec2):
    vec1, vec2 = np.array(vec1), np.array(vec2)
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def run_tests():
    matches = pd.read_csv(f"{CLEANED_FOLDER}/matches_clean.csv")
    profiles = pd.read_csv(f"{CLEANED_FOLDER}/player_profiles.csv")

    passed = 0
    failed = 0

    def check(description, condition):
        nonlocal passed, failed
        if condition:
            print(f"✅ PASS: {description}")
            passed += 1
        else:
            print(f"❌ FAIL: {description}")
            failed += 1

    # Test 1: Team that doesn't exist in the dataset
    fake_team_matches = matches[matches["Home Team Name"] == "Wakanda"]
    check("Non-existent team returns empty result (not a crash)", len(fake_team_matches) == 0)

    # Test 2: Same team selected as both team1 and team2
    same_team_h2h = matches[
        (matches["Home Team Name"] == "Brazil") & (matches["Away Team Name"] == "Brazil")
    ]
    check("Same team vs itself returns no matches (expected, no self-play)", len(same_team_h2h) == 0)

    # Test 3: Cosine similarity with a zero vector (a player with all-zero scores)
    zero_vec = [0, 0, 0, 0, 0]
    normal_vec = [50, 60, 70, 80, 90]
    similarity = cosine_similarity(zero_vec, normal_vec)
    check("Cosine similarity handles a zero vector without crashing (returns 0)", similarity == 0)

    # Test 4: Player name that doesn't exist
    missing_player = profiles[profiles["Player Name"] == "NOT A REAL PLAYER"]
    check("Searching for a non-existent player returns empty (not a crash)", len(missing_player) == 0)

    # Test 5: Case sensitivity - does "brazil" (lowercase) match "Brazil"?
    lowercase_match = matches[matches["Home Team Name"].str.lower() == "brazil"]
    exact_match = matches[matches["Home Team Name"] == "Brazil"]
    check(
        "Lowercase team name search finds same results as exact case (case sensitivity check)",
        len(lowercase_match) == len(exact_match)
    )

    # Test 6: Missing/null values don't break aggregation
    null_check = profiles["Goals"].isnull().sum()
    check("No missing values in Goals column after cleaning", null_check == 0)

    # Test 7: Player profile scores are within expected 0-100 range
    score_cols = ["Goals_Score", "Appearances_Score", "Attack_Score", "Experience_Score", "Discipline_Score"]
    out_of_range = False
    for col in score_cols:
        if (profiles[col] < 0).any() or (profiles[col] > 100).any():
            out_of_range = True
    check("All normalized scores are within 0-100 range", not out_of_range)

    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'=' * 40}")


if __name__ == "__main__":
    run_tests()
