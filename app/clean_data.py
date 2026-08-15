"""
Day 2 - Task: Clean the raw CSV files and save cleaned versions.

Run: python app/clean_data.py
"""

import os
import pandas as pd

DATA_FOLDER = "data"
CLEANED_FOLDER = "data/cleaned"

# The source Kaggle dataset has a known encoding issue: a handful of player
# names with accented characters (like PELÉ, MÜLLER) were corrupted at the
# source, appearing as a broken "replacement character" - before we ever
# touched the file. We fix the well-known ones manually here.
NAME_CORRECTIONS = {
    "PEL\ufffd": "PELE",
    "M\ufffdLLER": "MULLER",
}


def fix_known_encoding_issues(name):
    if pd.isna(name):
        return name
    for broken, fixed in NAME_CORRECTIONS.items():
        if broken in name:
            return name.replace(broken, fixed)
    # Catch-all: any other corrupted character we don't have a specific fix
    # for, just remove it so the name stays readable instead of showing a box symbol.
    return name.replace("\ufffd", "")


def clean_matches():
    df = pd.read_csv(f"{DATA_FOLDER}/WorldCupMatches.csv", encoding="utf-8")

    # Drop fully-empty trailing rows (Year missing means the row is junk)
    df = df.dropna(subset=["Year"])

    # Year is stored as float (1930.0) - convert to int for cleanliness
    df["Year"] = df["Year"].astype(int)

    # Clean up team names (remove extra whitespace)
    df["Home Team Name"] = df["Home Team Name"].str.strip()
    df["Away Team Name"] = df["Away Team Name"].str.strip()

    print(f"✅ Matches cleaned: {df.shape[0]} valid rows (was 4572)")
    return df


def clean_players():
    df = pd.read_csv(f"{DATA_FOLDER}/WorldCupPlayers.csv", encoding="utf-8")

    # Empty Event just means no goal/card happened - that's fine, not an error.
    # Empty Position sometimes happens for non-starting lineup players - fine too.
    # We just fill them with a clear placeholder instead of blank/NaN.
    df["Event"] = df["Event"].fillna("No event")
    df["Position"] = df["Position"].fillna("Not specified")

    df["Player Name"] = df["Player Name"].str.strip()
    df["Player Name"] = df["Player Name"].apply(fix_known_encoding_issues)
    df["Team Initials"] = df["Team Initials"].str.strip()
    df["Coach Name"] = df["Coach Name"].str.strip()

    print(f"✅ Players cleaned: {df.shape[0]} rows")
    return df


def clean_worldcups():
    df = pd.read_csv(f"{DATA_FOLDER}/WorldCups.csv", encoding="utf-8")
    # Already clean (no missing values), just strip whitespace to be safe
    for col in ["Country", "Winner", "Runners-Up", "Third", "Fourth"]:
        df[col] = df[col].str.strip()

    print(f"✅ WorldCups already clean: {df.shape[0]} rows")
    return df


if __name__ == "__main__":
    os.makedirs(CLEANED_FOLDER, exist_ok=True)

    matches = clean_matches()
    players = clean_players()
    worldcups = clean_worldcups()

    matches.to_csv(f"{CLEANED_FOLDER}/matches_clean.csv", index=False)
    players.to_csv(f"{CLEANED_FOLDER}/players_clean.csv", index=False)
    worldcups.to_csv(f"{CLEANED_FOLDER}/worldcups_clean.csv", index=False)

    print(f"\n🎉 All cleaned files saved inside '{CLEANED_FOLDER}/' folder")
