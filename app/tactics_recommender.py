"""
Day 7 - Task: Tactics recommender - suggest strategy based on two teams.

Run: python app/tactics_recommender.py "Team A" "Team B"
Example: python app/tactics_recommender.py "Brazil" "Germany"
"""

import sys
import pandas as pd

# Fix for Windows terminal not displaying special characters (É, Ü, etc.) correctly
sys.stdout.reconfigure(encoding="utf-8")

CLEANED_FOLDER = "data/cleaned"


def load_data():
    matches = pd.read_csv(f"{CLEANED_FOLDER}/matches_clean.csv")
    players = pd.read_csv(f"{CLEANED_FOLDER}/players_clean.csv")
    profiles = pd.read_csv(f"{CLEANED_FOLDER}/player_profiles.csv")
    return matches, players, profiles


def get_team_initials(matches, team_name):
    home_match = matches[matches["Home Team Name"].str.contains(team_name, case=False, na=False)]
    if not home_match.empty:
        return home_match.iloc[0]["Home Team Initials"]
    away_match = matches[matches["Away Team Name"].str.contains(team_name, case=False, na=False)]
    if not away_match.empty:
        return away_match.iloc[0]["Away Team Initials"]
    return None


def head_to_head(matches, team1, team2):
    h2h = matches[
        ((matches["Home Team Name"].str.contains(team1, case=False, na=False)) &
         (matches["Away Team Name"].str.contains(team2, case=False, na=False))) |
        ((matches["Home Team Name"].str.contains(team2, case=False, na=False)) &
         (matches["Away Team Name"].str.contains(team1, case=False, na=False)))
    ]
    return h2h


def team_attack_defense_profile(matches, team_name):
    home_games = matches[matches["Home Team Name"].str.contains(team_name, case=False, na=False)]
    away_games = matches[matches["Away Team Name"].str.contains(team_name, case=False, na=False)]

    goals_scored = home_games["Home Team Goals"].sum() + away_games["Away Team Goals"].sum()
    goals_conceded = home_games["Away Team Goals"].sum() + away_games["Home Team Goals"].sum()
    total_games = len(home_games) + len(away_games)

    if total_games == 0:
        return None

    return {
        "games": total_games,
        "avg_scored": goals_scored / total_games,
        "avg_conceded": goals_conceded / total_games,
    }


def get_top_players(players, profiles, team_initials, top_n=3):
    team_players = players[players["Team Initials"] == team_initials]["Player Name"].unique()
    team_profiles = profiles[
        (profiles["Player Name"].isin(team_players)) &
        (profiles["Team Initials"] == team_initials)
    ]
    team_profiles = team_profiles.sort_values("Goals", ascending=False)
    # Some names appear more than once due to data quirks (e.g. inconsistent
    # match-linking in the source data). Keep only the strongest record per name.
    team_profiles = team_profiles.drop_duplicates(subset="Player Name", keep="first")
    return team_profiles.head(top_n)


def recommend_strategy(team1, team2):
    matches, players, profiles = load_data()

    print("=" * 65)
    print(f"TACTICAL ANALYSIS: {team1} vs {team2}")
    print("=" * 65)

    # 1. Head-to-head history
    h2h = head_to_head(matches, team1, team2)
    print(f"\n📊 Head-to-Head History ({len(h2h)} matches found):")
    if len(h2h) > 0:
        team1_wins = 0
        team2_wins = 0
        draws = 0
        for _, row in h2h.iterrows():
            if row["Home Team Name"].strip().lower() == team1.lower():
                home_goals, away_goals = row["Home Team Goals"], row["Away Team Goals"]
            else:
                home_goals, away_goals = row["Away Team Goals"], row["Home Team Goals"]
            if home_goals > away_goals:
                team1_wins += 1
            elif home_goals < away_goals:
                team2_wins += 1
            else:
                draws += 1
        print(f"   {team1} wins: {team1_wins} | {team2} wins: {team2_wins} | Draws: {draws}")
    else:
        print("   No previous meetings found in the dataset.")

    # 2. Attack/Defense profile
    t1_profile = team_attack_defense_profile(matches, team1)
    t2_profile = team_attack_defense_profile(matches, team2)

    print(f"\n⚔️ Attack/Defense Profile:")
    if t1_profile:
        print(f"   {team1}: avg {t1_profile['avg_scored']:.2f} goals scored, {t1_profile['avg_conceded']:.2f} conceded per match ({t1_profile['games']} matches)")
    if t2_profile:
        print(f"   {team2}: avg {t2_profile['avg_scored']:.2f} goals scored, {t2_profile['avg_conceded']:.2f} conceded per match ({t2_profile['games']} matches)")

    # 3. Key players
    t1_initials = get_team_initials(matches, team1)
    t2_initials = get_team_initials(matches, team2)

    print(f"\n⭐ Key Players to Watch:")
    if t1_initials is not None:
        top1 = get_top_players(players, profiles, t1_initials)
        print(f"   {team1}: {', '.join(top1['Player Name'].tolist())}")
    if t2_initials is not None:
        top2 = get_top_players(players, profiles, t2_initials)
        print(f"   {team2}: {', '.join(top2['Player Name'].tolist())}")

    # 4. Rule-based tactical suggestion
    print(f"\n🎯 Suggested Strategy for {team1}:")
    if t1_profile and t2_profile:
        if t1_profile["avg_scored"] > t2_profile["avg_conceded"]:
            print(f"   → {team2}'s defense has historically conceded goals at a rate {team1} can exploit.")
            print(f"     Recommendation: Play an attacking, possession-based approach.")
        else:
            print(f"   → {team2}'s defense is historically solid against similar attacking output.")
            print(f"     Recommendation: Focus on defensive solidity and quick counter-attacks.")

        if t2_profile["avg_scored"] > t1_profile["avg_conceded"]:
            print(f"   → Caution: {team2} historically scores at a rate that could trouble {team1}'s defense.")
            print(f"     Recommendation: Prioritize defensive shape, avoid high defensive line.")
    else:
        print("   → Not enough historical data to generate a data-backed suggestion.")

    print("\n" + "=" * 65)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        recommend_strategy(sys.argv[1], sys.argv[2])
    else:
        print("No teams given, running example: Brazil vs Germany\n")
        recommend_strategy("Brazil", "Germany")
