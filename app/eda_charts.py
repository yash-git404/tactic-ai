"""
Day 3 - Task: Generate exploratory charts from the cleaned data.

Run: python app/eda_charts.py
Charts will be saved inside the 'docs/charts' folder as .png images.
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # so it works without a display window
import matplotlib.pyplot as plt

CLEANED_FOLDER = "data/cleaned"
CHARTS_FOLDER = "docs/charts"


def chart_most_winners(worldcups):
    counts = worldcups["Winner"].value_counts()

    plt.figure(figsize=(8, 5))
    counts.plot(kind="bar", color="#2E86AB")
    plt.title("World Cup Wins by Country (1930-2022)")
    plt.xlabel("Country")
    plt.ylabel("Number of Titles")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(f"{CHARTS_FOLDER}/most_winners.png")
    plt.close()
    print("✅ Saved: most_winners.png")


def chart_goals_trend(worldcups):
    df = worldcups.sort_values("Year")

    plt.figure(figsize=(9, 5))
    plt.plot(df["Year"], df["GoalsScored"], marker="o", color="#E63946")
    plt.title("Total Goals Scored per World Cup Over the Years")
    plt.xlabel("Year")
    plt.ylabel("Goals Scored")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{CHARTS_FOLDER}/goals_trend.png")
    plt.close()
    print("✅ Saved: goals_trend.png")


def chart_attendance_trend(worldcups):
    df = worldcups.sort_values("Year")

    plt.figure(figsize=(9, 5))
    plt.bar(df["Year"].astype(str), df["Attendance"], color="#06A77D")
    plt.title("Total Attendance per World Cup Over the Years")
    plt.xlabel("Year")
    plt.ylabel("Attendance")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(f"{CHARTS_FOLDER}/attendance_trend.png")
    plt.close()
    print("✅ Saved: attendance_trend.png")


def chart_top_scorers(players):
    # Only rows where a goal event happened contain "G" in the Event column
    goal_rows = players[players["Event"].str.contains("G", na=False)]

    top_scorers = goal_rows["Player Name"].value_counts().head(10)

    plt.figure(figsize=(9, 5))
    top_scorers.sort_values().plot(kind="barh", color="#F4A261")
    plt.title("Top 10 Goal Scorers - World Cup History")
    plt.xlabel("Goals")
    plt.tight_layout()
    plt.savefig(f"{CHARTS_FOLDER}/top_scorers.png")
    plt.close()
    print("✅ Saved: top_scorers.png")


if __name__ == "__main__":
    os.makedirs(CHARTS_FOLDER, exist_ok=True)

    worldcups = pd.read_csv(f"{CLEANED_FOLDER}/worldcups_clean.csv")
    players = pd.read_csv(f"{CLEANED_FOLDER}/players_clean.csv")

    chart_most_winners(worldcups)
    chart_goals_trend(worldcups)
    chart_attendance_trend(worldcups)
    chart_top_scorers(players)

    print(f"\n🎉 All charts saved inside '{CHARTS_FOLDER}/' folder")
