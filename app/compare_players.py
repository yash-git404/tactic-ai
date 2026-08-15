"""
Day 5 - Task: Compare two players side-by-side and calculate a similarity score.

Run: python app/compare_players.py "PLAYER ONE" "PLAYER TWO"
Example: python app/compare_players.py "RONALDO" "Gerd MUELLER"

If you don't pass names, it will compare two example legends by default.
"""

import sys
import pandas as pd
import numpy as np

CLEANED_FOLDER = "data/cleaned"

SCORE_COLUMNS = [
    "Goals_Score",
    "Appearances_Score",
    "Attack_Score",
    "Experience_Score",
    "Discipline_Score",
]


def load_profiles():
    return pd.read_csv(f"{CLEANED_FOLDER}/player_profiles.csv")


def find_player(profiles, name):
    # Case-insensitive partial match, since dataset names are inconsistent (e.g. all caps)
    matches = profiles[profiles["Player Name"].str.contains(name, case=False, na=False)]
    if matches.empty:
        return None
    # If multiple matches, take the one with most appearances (most likely the famous one)
    return matches.sort_values("Appearances", ascending=False).iloc[0]


def cosine_similarity(vec1, vec2):
    vec1, vec2 = np.array(vec1), np.array(vec2)
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def compare(player1_name, player2_name):
    profiles = load_profiles()

    p1 = find_player(profiles, player1_name)
    p2 = find_player(profiles, player2_name)

    if p1 is None:
        print(f"❌ Could not find a player matching '{player1_name}'")
        return
    if p2 is None:
        print(f"❌ Could not find a player matching '{player2_name}'")
        return

    print("=" * 60)
    print(f"COMPARING: {p1['Player Name']}  vs  {p2['Player Name']}")
    print("=" * 60)

    raw_stats = ["Goals", "Appearances", "Cards", "Tournaments"]
    print(f"\n{'Stat':<15}{p1['Player Name']:<20}{p2['Player Name']:<20}")
    print("-" * 55)
    for stat in raw_stats:
        print(f"{stat:<15}{p1[stat]:<20}{p2[stat]:<20}")

    similarity = cosine_similarity(
        p1[SCORE_COLUMNS].values,
        p2[SCORE_COLUMNS].values,
    )

    print(f"\nSimilarity Score: {similarity * 100:.1f}% (based on playing profile)")

    if similarity > 0.9:
        print("→ These players have a very similar profile/style.")
    elif similarity > 0.7:
        print("→ These players share a moderately similar profile.")
    else:
        print("→ These players have quite different profiles.")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        compare(sys.argv[1], sys.argv[2])
    else:
        print("No player names given, comparing two example legends:\n")
        compare("RONALDO", "MUELLER")
