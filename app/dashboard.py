"""
Day 8-9 - TacticAI dashboard: Match Strategy + Player Analytics tabs.

Run: streamlit run app/dashboard.py
This will open a browser window automatically.
"""

import os
import sys
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

API_KEY = os.getenv("API_FOOTBALL_KEY")
API_BASE_URL = "https://v3.football.api-sports.io"
API_HEADERS = {"x-apisports-key": API_KEY}

CLEANED_FOLDER = "data/cleaned"

SCORE_COLUMNS = [
    "Goals_Score",
    "Appearances_Score",
    "Attack_Score",
    "Experience_Score",
    "Discipline_Score",
]
RADAR_LABELS = ["Goals", "Appearances", "Attack", "Experience", "Discipline"]


@st.cache_data
def load_data():
    matches = pd.read_csv(f"{CLEANED_FOLDER}/matches_clean.csv")
    players = pd.read_csv(f"{CLEANED_FOLDER}/players_clean.csv")
    profiles = pd.read_csv(f"{CLEANED_FOLDER}/player_profiles.csv")
    return matches, players, profiles


def get_team_list(matches):
    teams = pd.concat([matches["Home Team Name"], matches["Away Team Name"]]).dropna().unique()
    return sorted(teams)


def get_team_initials(matches, team_name):
    home_match = matches[matches["Home Team Name"] == team_name]
    if not home_match.empty:
        return home_match.iloc[0]["Home Team Initials"]
    away_match = matches[matches["Away Team Name"] == team_name]
    if not away_match.empty:
        return away_match.iloc[0]["Away Team Initials"]
    return None


def head_to_head(matches, team1, team2):
    return matches[
        ((matches["Home Team Name"] == team1) & (matches["Away Team Name"] == team2)) |
        ((matches["Home Team Name"] == team2) & (matches["Away Team Name"] == team1))
    ]


def team_attack_defense_profile(matches, team_name):
    home_games = matches[matches["Home Team Name"] == team_name]
    away_games = matches[matches["Away Team Name"] == team_name]
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
    team_profiles = team_profiles.drop_duplicates(subset="Player Name", keep="first")
    return team_profiles.head(top_n)


def make_radar_figure(player_rows):
    """player_rows: list of profile rows (pandas Series), one trace per player."""
    fig = go.Figure()
    colors = ["#D4AF37", "#7FB3D5", "#8FD9A8"]
    for i, row in enumerate(player_rows):
        values = [row[col] for col in SCORE_COLUMNS]
        values += values[:1]
        labels = RADAR_LABELS + [RADAR_LABELS[0]]
        fig.add_trace(go.Scatterpolar(
            r=values, theta=labels, fill="toself",
            name=f"{row['Player Name']} ({row['Team Initials']})",
            line_color=colors[i % len(colors)],
            line_width=2.5,
        ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=13, color="#C7C2B5")),
            angularaxis=dict(tickfont=dict(size=16, color="#F0EDE4", family="Inter")),
        ),
        showlegend=True,
        legend=dict(font=dict(size=15, color="#F0EDE4"), orientation="h", y=-0.1),
        height=480,
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=30),
    )
    return fig


def cosine_similarity(vec1, vec2):
    vec1, vec2 = np.array(vec1), np.array(vec2)
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


@st.cache_data(ttl=30)  # re-fetch from the API at most every 30 seconds
def fetch_live_fixtures():
    try:
        response = requests.get(
            f"{API_BASE_URL}/fixtures", headers=API_HEADERS, params={"live": "all"}, timeout=10
        )
        if response.status_code == 200:
            return response.json().get("response", []), None
        return [], f"API returned status code {response.status_code}"
    except Exception as e:
        return [], str(e)


@st.cache_data(ttl=30)
def fetch_fixture_stats(fixture_id):
    try:
        response = requests.get(
            f"{API_BASE_URL}/fixtures/statistics",
            headers=API_HEADERS,
            params={"fixture": fixture_id},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json().get("response", []), None
        return [], f"API returned status code {response.status_code}"
    except Exception as e:
        return [], str(e)


@st.cache_data(ttl=60)
def fetch_predictions(fixture_id):
    try:
        response = requests.get(
            f"{API_BASE_URL}/predictions",
            headers=API_HEADERS,
            params={"fixture": fixture_id},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json().get("response", []), None
        return [], f"API returned status code {response.status_code}"
    except Exception as e:
        return [], str(e)


def render_win_probability(home_name, away_name, home_pct, draw_pct, away_pct):
    html = f"""
    <style>
        .prob-card {{
            background-color: #123625;
            border: 1px solid rgba(212,175,55,0.25);
            border-radius: 6px;
            padding: 18px 22px;
            margin-bottom: 16px;
        }}
        .prob-title {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #C7C2B5;
            text-align: center;
            margin-bottom: 12px;
        }}
        .prob-labels {{
            display: flex;
            justify-content: space-between;
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            font-size: 1.15rem;
            margin-bottom: 8px;
        }}
        .prob-home {{ color: #D4AF37; }}
        .prob-draw {{ color: #A9A497; }}
        .prob-away {{ color: #7FB3D5; }}
        .prob-bar {{
            display: flex;
            height: 10px;
            border-radius: 5px;
            overflow: hidden;
        }}
        .prob-bar-home {{ background-color: #D4AF37; }}
        .prob-bar-draw {{ background-color: #4A6B5A; }}
        .prob-bar-away {{ background-color: #7FB3D5; }}
    </style>
    <div class="prob-card">
        <div class="prob-title">Live Win Probability</div>
        <div class="prob-labels">
            <span class="prob-home">{home_name} {home_pct}%</span>
            <span class="prob-draw">Draw {draw_pct}%</span>
            <span class="prob-away">{away_name} {away_pct}%</span>
        </div>
        <div class="prob-bar">
            <div class="prob-bar-home" style="width:{home_pct}%;"></div>
            <div class="prob-bar-draw" style="width:{draw_pct}%;"></div>
            <div class="prob-bar-away" style="width:{away_pct}%;"></div>
        </div>
    </div>
    """
    html = "\n".join(line.strip() for line in html.split("\n"))
    st.markdown(html, unsafe_allow_html=True)


STAT_TYPE_TO_LABEL = {
    "Total Shots": "Shots",
    "Shots on Goal": "Shots on target",
    "Ball Possession": "Possession",
    "Total passes": "Passes",
    "Passes %": "Pass accuracy",
    "Fouls": "Fouls",
    "Yellow Cards": "Yellow cards",
    "Red Cards": "Red cards",
    "Offsides": "Offsides",
    "Corner Kicks": "Corners",
}
STAT_ORDER = ["Shots", "Shots on target", "Possession", "Passes", "Pass accuracy",
              "Fouls", "Yellow cards", "Red cards", "Offsides", "Corners"]


def _clean_stat_value(value):
    if value is None:
        return 0
    return value


def _numeric_value(value):
    if value is None:
        return 0
    if isinstance(value, str) and "%" in value:
        try:
            return float(value.replace("%", ""))
        except ValueError:
            return 0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0


def render_stat_comparison(home_name, away_name, home_raw_stats, away_raw_stats):
    home_map = {STAT_TYPE_TO_LABEL.get(s["type"], s["type"]): _clean_stat_value(s["value"]) for s in home_raw_stats}
    away_map = {STAT_TYPE_TO_LABEL.get(s["type"], s["type"]): _clean_stat_value(s["value"]) for s in away_raw_stats}

    rows_html = ""
    for label in STAT_ORDER:
        h_val = home_map.get(label, 0)
        a_val = away_map.get(label, 0)
        h_num, a_num = _numeric_value(h_val), _numeric_value(a_val)

        h_class = "stat-lead" if h_num > a_num else "stat-plain"
        a_class = "stat-lead" if a_num > h_num else "stat-plain"

        if label == "Possession":
            h_pct = h_num if h_num > 0 else 50
            a_pct = 100 - h_pct
            rows_html += f"""
            <div class="stat-row">
                <div class="stat-val {h_class}">{h_val}</div>
                <div class="stat-label">{label}</div>
                <div class="stat-val {a_class}">{a_val}</div>
            </div>
            <div class="possession-bar">
                <div class="possession-home" style="width:{h_pct}%;"></div>
                <div class="possession-away" style="width:{a_pct}%;"></div>
            </div>
            """
        else:
            rows_html += f"""
            <div class="stat-row">
                <div class="stat-val {h_class}">{h_val}</div>
                <div class="stat-label">{label}</div>
                <div class="stat-val {a_class}">{a_val}</div>
            </div>
            """

    html = f"""
    <style>
        .stat-card {{
            background-color: #123625;
            border: 1px solid rgba(212,175,55,0.25);
            border-radius: 6px;
            padding: 20px 24px;
        }}
        .stat-teams {{
            display: flex;
            justify-content: space-between;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            font-size: 1.15rem;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: #D4AF37;
            margin-bottom: 14px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(212,175,55,0.25);
        }}
        .stat-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            font-family: 'Inter', sans-serif;
        }}
        .stat-val {{
            width: 70px;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            font-size: 1.1rem;
        }}
        .stat-val.stat-lead {{
            color: #0B2818;
            background-color: #D4AF37;
            border-radius: 10px;
            text-align: center;
            padding: 4px 0;
        }}
        .stat-val.stat-plain {{
            color: #F0EDE4;
            text-align: center;
            opacity: 0.85;
        }}
        .stat-label {{
            flex: 1;
            text-align: center;
            font-size: 1rem;
            color: #C7C2B5;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .possession-bar {{
            display: flex;
            height: 6px;
            border-radius: 3px;
            overflow: hidden;
            margin-bottom: 4px;
        }}
        .possession-home {{ background-color: #D4AF37; }}
        .possession-away {{ background-color: #4A6B5A; }}
    </style>
    <div class="stat-card">
        <div class="stat-teams"><span>{home_name}</span><span>{away_name}</span></div>
        {rows_html}
    </div>
    """
    # Strip leading whitespace from each line - otherwise Streamlit's markdown
    # renderer treats indented lines as a code block instead of rendering the HTML
    html = "\n".join(line.strip() for line in html.split("\n"))
    st.markdown(html, unsafe_allow_html=True)


# ---------------- UI STARTS HERE ----------------

st.set_page_config(page_title="TacticAI", page_icon="⚽", layout="centered")

# Custom styling — "tactics board" identity: pitch green, chalk white, scoreboard gold
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main .block-container {
        padding-top: 1.5rem;
        max-width: 850px;
    }

    /* Subtle mowed-pitch stripe texture across the whole app */
    .stApp {
        background-image: repeating-linear-gradient(
            100deg,
            rgba(255,255,255,0.012) 0px,
            rgba(255,255,255,0.012) 60px,
            transparent 60px,
            transparent 120px
        );
    }

    /* Hero title area with a faint pitch-marking watermark + corner arcs */
    .hero-banner {
        position: relative;
        background-image:
            radial-gradient(circle at 50% 120px, rgba(212,175,55,0.10) 0, transparent 90px),
            repeating-linear-gradient(0deg, transparent, transparent 39px, rgba(240,237,228,0.035) 40px);
        border-bottom: 2px solid rgba(212,175,55,0.35);
        padding: 8px 0 20px 0;
        margin-bottom: 18px;
        overflow: hidden;
    }
    .hero-banner::before, .hero-banner::after {
        content: "";
        position: absolute;
        width: 36px;
        height: 36px;
        border: 2px solid rgba(212,175,55,0.3);
        top: -18px;
    }
    .hero-banner::before {
        left: -18px;
        border-radius: 0 0 36px 0;
        border-top: none;
        border-left: none;
    }
    .hero-banner::after {
        right: -18px;
        border-radius: 0 0 0 36px;
        border-top: none;
        border-right: none;
    }
    .hero-banner h1 {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 3rem;
        letter-spacing: 3px;
        color: #F0EDE4;
        margin-bottom: 0;
    }
    .hero-banner .eyebrow {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #D4AF37;
    }
    .hero-banner .subtitle {
        color: #A9A497;
        font-size: 0.95rem;
        margin-top: -6px;
    }

    /* Section headers styled like a scoreboard / matchday sheet */
    h2, h3 {
        font-family: 'Bebas Neue', sans-serif !important;
        letter-spacing: 1.5px;
        color: #F0EDE4 !important;
    }
    h2 { font-size: 2.1rem !important; margin-top: 1.2rem !important; }
    h3 { font-size: 1.7rem !important; }

    /* Body text and captions - bump up from Streamlit's small defaults */
    p, .stMarkdown, div[data-testid="stMarkdownContainer"] p {
        font-size: 1.05rem !important;
        line-height: 1.6;
    }
    div[data-testid="stCaptionContainer"] p, [data-testid="stCaptionContainer"] {
        font-size: 1rem !important;
        color: #C7C2B5 !important;
    }
    /* Radio / checkbox / selectbox label text */
    div[data-testid="stWidgetLabel"] p {
        font-size: 1.05rem !important;
        font-weight: 600;
    }
    div[data-baseweb="select"] * {
        font-size: 1.05rem !important;
    }

    /* Metric tiles = scoreboard cards, made larger and bolder */
    div[data-testid="stMetric"] {
        background-color: #123625;
        border: 1px solid rgba(212,175,55,0.25);
        border-left: 4px solid #D4AF37;
        border-radius: 6px;
        padding: 16px 20px;
    }
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 2.4rem !important;
    }
    div[data-testid="stMetricLabel"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem !important;
        letter-spacing: 1px;
        text-transform: uppercase;
        opacity: 0.85;
    }

    /* Buttons: referee-card energy, bigger and bolder */
    .stButton > button {
        border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        font-size: 1rem;
        padding: 10px 22px;
        border: 1.5px solid #D4AF37;
    }

    /* Tabs styled like a matchday selector strip, bigger */
    div[data-testid="stTabs"] button {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.05rem;
        letter-spacing: 0.5px;
        font-weight: 600;
        padding: 10px 6px;
    }
    div[data-testid="stTabs"] button p {
        font-size: 1.05rem !important;
    }

    /* Banner image styling */
    div[data-testid="stImage"] img {
        border-radius: 8px;
        border: 1px solid rgba(212,175,55,0.3);
    }
    section[data-testid="stSidebar"] h3 {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #D4AF37 !important;
    }
</style>

<div class="hero-banner">
    <h1>⚽ TACTICAI</h1>
    <div class="subtitle">AI-powered tactical decision support for football strategy</div>
</div>
""", unsafe_allow_html=True)

_banner_path = "docs/assets/banner.jpg"
if os.path.exists(_banner_path):
    st.image(_banner_path, width='stretch')

# Sidebar branding
with st.sidebar:
    st.markdown("### ⚽ TacticAI")
    st.caption("Player Analytics & Match Strategy Recommender")
    st.divider()
    st.markdown("**Built by:** [Your Name]")
    st.divider()
    st.markdown("**Tech Stack**")
    st.markdown("- Python, Pandas, Scikit-learn")
    st.markdown("- Streamlit + Plotly")
    st.markdown("- API-Football (live data)")
    st.divider()
    st.markdown("**Data Source**")
    st.caption("FIFA World Cup historical dataset (1930-2022) + live World Cup 2026 API")

matches, players, profiles = load_data()
team_list = get_team_list(matches)

tab1, tab2, tab3 = st.tabs(["🎯 Match Strategy", "👤 Player Analytics", "🔴 Live Match"])

with tab1:
    st.caption("Select two teams to see historical analysis and a suggested strategy")

    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("Your Team", team_list, index=team_list.index("Brazil") if "Brazil" in team_list else 0)
    with col2:
        team2 = st.selectbox("Opponent Team", team_list, index=team_list.index("Germany") if "Germany" in team_list else 1)

    if st.button("Analyze Match", type="primary"):
        if team1 == team2:
            st.warning("Please select two different teams.")
        else:
            st.divider()

            # Head to head
            st.subheader("📊 Head-to-Head History")
            h2h = head_to_head(matches, team1, team2)
            if len(h2h) > 0:
                t1_wins = t2_wins = draws = 0
                for _, row in h2h.iterrows():
                    if row["Home Team Name"] == team1:
                        hg, ag = row["Home Team Goals"], row["Away Team Goals"]
                    else:
                        hg, ag = row["Away Team Goals"], row["Home Team Goals"]
                    if hg > ag:
                        t1_wins += 1
                    elif hg < ag:
                        t2_wins += 1
                    else:
                        draws += 1
                c1, c2, c3 = st.columns(3)
                c1.metric(f"{team1} wins", t1_wins)
                c2.metric("Draws", draws)
                c3.metric(f"{team2} wins", t2_wins)
            else:
                st.info("No previous meetings found in the dataset.")

            # Attack/defense profile
            st.subheader("⚔️ Attack / Defense Profile")
            t1_profile = team_attack_defense_profile(matches, team1)
            t2_profile = team_attack_defense_profile(matches, team2)
            c1, c2 = st.columns(2)
            if t1_profile:
                c1.metric(f"{team1} avg goals scored", f"{t1_profile['avg_scored']:.2f}")
                c1.metric(f"{team1} avg goals conceded", f"{t1_profile['avg_conceded']:.2f}")
            if t2_profile:
                c2.metric(f"{team2} avg goals scored", f"{t2_profile['avg_scored']:.2f}")
                c2.metric(f"{team2} avg goals conceded", f"{t2_profile['avg_conceded']:.2f}")

            # Key players
            st.subheader("⭐ Key Players to Watch")
            t1_initials = get_team_initials(matches, team1)
            t2_initials = get_team_initials(matches, team2)
            c1, c2 = st.columns(2)
            if t1_initials is not None:
                top1 = get_top_players(players, profiles, t1_initials)
                c1.write(f"**{team1}**")
                for _, p in top1.iterrows():
                    c1.write(f"- {p['Player Name']} ({int(p['Goals'])} goals)")
            if t2_initials is not None:
                top2 = get_top_players(players, profiles, t2_initials)
                c2.write(f"**{team2}**")
                for _, p in top2.iterrows():
                    c2.write(f"- {p['Player Name']} ({int(p['Goals'])} goals)")

            # Strategy suggestion
            st.subheader(f"🎯 Suggested Strategy for {team1}")
            if t1_profile and t2_profile:
                if t1_profile["avg_scored"] > t2_profile["avg_conceded"]:
                    st.success(f"{team2}'s defense has historically conceded goals at a rate {team1} can exploit. **Recommendation: Play an attacking, possession-based approach.**")
                else:
                    st.info(f"{team2}'s defense is historically solid. **Recommendation: Focus on defensive solidity and quick counter-attacks.**")

                if t2_profile["avg_scored"] > t1_profile["avg_conceded"]:
                    st.warning(f"Caution: {team2} historically scores at a rate that could trouble {team1}'s defense. **Recommendation: Prioritize defensive shape.**")
            else:
                st.info("Not enough historical data to generate a suggestion.")

with tab2:
    st.caption("Search for players, view their radar profile, and compare two players")

    # Only show players with a reasonable number of appearances, so the
    # dropdown isn't cluttered with one-match players
    searchable_profiles = profiles[profiles["Appearances"] >= 2].copy()
    searchable_profiles["Display"] = searchable_profiles["Player Name"] + " (" + searchable_profiles["Team Initials"] + ")"
    player_display_list = sorted(searchable_profiles["Display"].unique())

    compare_mode = st.checkbox("Compare two players")

    if not compare_mode:
        default_index = 0
        for i, name in enumerate(player_display_list):
            if "RONALDO" in name and "BRA" in name:
                default_index = i
                break
        selected = st.selectbox("Select a player", player_display_list, index=default_index)
        row = searchable_profiles[searchable_profiles["Display"] == selected].iloc[0]

        st.plotly_chart(make_radar_figure([row]), width='stretch')

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Goals", int(row["Goals"]))
        c2.metric("Appearances", int(row["Appearances"]))
        c3.metric("Tournaments", int(row["Tournaments"]))
        c4.metric("Cards", int(row["Cards"]))

    else:
        c1, c2 = st.columns(2)
        with c1:
            selected1 = st.selectbox("Player 1", player_display_list, index=0)
        with c2:
            selected2 = st.selectbox("Player 2", player_display_list, index=1)

        row1 = searchable_profiles[searchable_profiles["Display"] == selected1].iloc[0]
        row2 = searchable_profiles[searchable_profiles["Display"] == selected2].iloc[0]

        st.plotly_chart(make_radar_figure([row1, row2]), width='stretch')

        similarity = cosine_similarity(row1[SCORE_COLUMNS].values, row2[SCORE_COLUMNS].values)
        st.metric("Similarity Score", f"{similarity * 100:.1f}%")

        stat_table = pd.DataFrame({
            "Stat": ["Goals", "Appearances", "Tournaments", "Cards"],
            selected1: [row1["Goals"], row1["Appearances"], row1["Tournaments"], row1["Cards"]],
            selected2: [row2["Goals"], row2["Appearances"], row2["Tournaments"], row2["Cards"]],
        })
        st.table(stat_table)

with tab3:
    st.caption("Live scores fetched from API-Football (auto-refreshes every 30 seconds)")

    if st.button("🔄 Refresh Live Matches"):
        fetch_live_fixtures.clear()

    live_matches, error = fetch_live_fixtures()

    if error:
        st.error(f"Could not fetch live matches: {error}")
    elif not live_matches:
        st.info("No matches are live right now. Check back during a scheduled match.")
    else:
        st.success(f"{len(live_matches)} match(es) live right now")

        match_labels = []
        for m in live_matches:
            home = m["teams"]["home"]["name"]
            away = m["teams"]["away"]["name"]
            match_labels.append(f"{home} vs {away}")

        selected_label = st.selectbox("Select a match for details", match_labels)
        selected_match = live_matches[match_labels.index(selected_label)]

        home = selected_match["teams"]["home"]["name"]
        away = selected_match["teams"]["away"]["name"]
        home_goals = selected_match["goals"]["home"]
        away_goals = selected_match["goals"]["away"]
        elapsed = selected_match["fixture"]["status"]["elapsed"]

        c1, c2, c3 = st.columns([2, 1, 2])
        c1.metric(home, home_goals)
        c2.metric("Minute", f"{elapsed}'" if elapsed else "-")
        c3.metric(away, away_goals)

        fixture_id = selected_match["fixture"]["id"]

        predictions, pred_error = fetch_predictions(fixture_id)
        if predictions and not pred_error:
            percent = predictions[0]["predictions"]["percent"]
            home_pct = int(percent["home"].replace("%", ""))
            draw_pct = int(percent["draw"].replace("%", ""))
            away_pct = int(percent["away"].replace("%", ""))
            render_win_probability(home, away, home_pct, draw_pct, away_pct)

        st.subheader("📈 Live Match Stats")
        stats, stats_error = fetch_fixture_stats(fixture_id)

        if stats_error:
            st.warning(f"Could not fetch detailed stats: {stats_error}")
        elif not stats or len(stats) < 2:
            st.info("Detailed stats not available yet for this match.")
        else:
            home_raw = stats[0]["statistics"]
            away_raw = stats[1]["statistics"]
            render_stat_comparison(home, away, home_raw, away_raw)

st.divider()
st.caption("TacticAI — Data-driven football tactics & analytics")
