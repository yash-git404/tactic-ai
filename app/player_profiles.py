"""
Day 4 - Task: Build player profiles and generate radar charts.

Run: python app/player_profiles.py
Charts saved inside 'docs/charts/players/' folder.
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CLEANED_FOLDER = "data/cleaned"
CHARTS_FOLDER = "docs/charts/players"


def build_player_stats(players, matches):
    # Merge to get the Year of each match, so we know which tournaments a player played in
    match_years = matches[["MatchID", "Year"]].drop_duplicates()
    df = players.merge(match_years, on="MatchID", how="left")

    # Goals: Event column has entries like "G40'" for a goal at 40th minute.
    # A player can score multiple goals in one match (multiple G's in the Event string).
    df["Goals"] = df["Event"].apply(lambda e: str(e).count("G") if e != "No event" else 0)

    # Cards: Y = yellow, R = red
    df["Cards"] = df["Event"].apply(lambda e: str(e).count("Y") + str(e).count("R") if e != "No event" else 0)

    stats = df.groupby(["Player Name", "Team Initials"]).agg(
        Appearances=("MatchID", "nunique"),
        Goals=("Goals", "sum"),
        Cards=("Cards", "sum"),
        Tournaments=("Year", "nunique"),
    ).reset_index()

    stats["Attack_Contribution"] = (stats["Goals"] / stats["Appearances"]).fillna(0)

    return stats


def normalize_0_100(series):
    if series.max() == series.min():
        return series * 0
    return (series - series.min()) / (series.max() - series.min()) * 100


def add_normalized_scores(stats):
    stats["Goals_Score"] = normalize_0_100(stats["Goals"])
    stats["Appearances_Score"] = normalize_0_100(stats["Appearances"])
    stats["Attack_Score"] = normalize_0_100(stats["Attack_Contribution"])
    stats["Experience_Score"] = normalize_0_100(stats["Tournaments"])
    # Discipline: fewer cards = higher score, so we invert it
    stats["Discipline_Score"] = 100 - normalize_0_100(stats["Cards"])
    return stats


def plot_radar(player_row, save_path):
    categories = ["Goals", "Appearances", "Attack", "Experience", "Discipline"]
    values = [
        player_row["Goals_Score"],
        player_row["Appearances_Score"],
        player_row["Attack_Score"],
        player_row["Experience_Score"],
        player_row["Discipline_Score"],
    ]
    values += values[:1]  # close the circle

    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, color="#E63946", linewidth=2)
    ax.fill(angles, values, color="#E63946", alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 100)
    ax.set_title(player_row["Player Name"], size=14, weight="bold", pad=20)

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


if __name__ == "__main__":
    os.makedirs(CHARTS_FOLDER, exist_ok=True)

    players = pd.read_csv(f"{CLEANED_FOLDER}/players_clean.csv")
    matches = pd.read_csv(f"{CLEANED_FOLDER}/matches_clean.csv")

    stats = build_player_stats(players, matches)
    stats = add_normalized_scores(stats)

    # Save the full profile table for later use (Week 2 comparison tool needs this)
    stats.to_csv(f"{CLEANED_FOLDER}/player_profiles.csv", index=False)
    print(f"✅ Player profiles saved: {stats.shape[0]} players in player_profiles.csv")

    # Generate radar charts for the top 3 goal scorers as a test
    top_3 = stats.sort_values("Goals", ascending=False).head(3)

    for _, row in top_3.iterrows():
        safe_name = row["Player Name"].replace(" ", "_").replace("/", "-")
        save_path = f"{CHARTS_FOLDER}/{safe_name}.png"
        plot_radar(row, save_path)
        print(f"✅ Radar chart saved: {save_path}")

    print(f"\n🎉 Test complete. Check '{CHARTS_FOLDER}/' for the 3 radar charts.")
