# ⚽ TacticAI — Player Analytics & Match Strategy Recommender

A football analytics and tactical decision-support system combining historical
FIFA World Cup data (1930-2022) with live match data, delivered through an
interactive Streamlit dashboard.

**Live demo:** [Add your Streamlit Cloud link here once deployed]

## Features

- **Match Strategy** — Select any two teams to see head-to-head history,
  attack/defense profiles, key players, and a rule-based strategic recommendation.
- **Player Analytics** — Search any player for a radar-chart profile, or
  compare two players side-by-side with a cosine-similarity score.
- **Player Clustering** — Players are grouped into style-based categories
  using K-Means clustering on 5 normalized performance metrics.
- **Live Match** — Real-time scores, win probability, and a live stats
  comparison for any currently live match, powered by API-Football.

## Tech Stack

Python · Pandas · NumPy · Scikit-learn · Plotly · Matplotlib · Streamlit ·
API-Football (REST API)

## Project Structure
```
tacticai/
├── app/
│   ├── dashboard.py            # Main Streamlit app (run this)
│   ├── clean_data.py           # Data cleaning pipeline
│   ├── player_profiles.py      # Builds normalized player profile scores
│   ├── cluster_players.py      # K-Means clustering of players
│   ├── tactics_recommender.py  # CLI version of the strategy recommender
│   ├── compare_players.py      # CLI player comparison tool
│   ├── fetch_recent_matches.py # Enriches historical data with 2018-2026 matches
│   ├── eda_charts.py           # Generates exploratory data analysis charts
│   └── test_edge_cases.py      # Automated tests for core logic
├── data/
│   └── cleaned/                # Cleaned CSVs used by the dashboard
├── docs/
│   ├── assets/                 # Images used in the dashboard/report
│   ├── charts/                 # Generated EDA and cluster visualizations
│   ├── interview_prep.md       # Full Q&A interview preparation guide
│   └── revision_sheet.md       # Quick-reference revision sheet
├── .streamlit/
│   └── config.toml             # Dashboard theme configuration
├── requirements.txt
└── .env.example                # Template for your API key (never commit .env itself)
```

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/yash-git404/tactic-ai.git
cd tactic-ai
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get a free API-Football key
1. Go to **https://dashboard.api-football.com/register** and sign up (free tier)
2. After logging in, go to **Account → My Access** to find your API key
3. Rename `.env.example` to `.env` and paste your key:
```
API_FOOTBALL_KEY=your_key_here
```

### 5. Run the dashboard
```bash
streamlit run app/dashboard.py
```
This opens the app in your browser at `http://localhost:8501`.

## Data Sources

- **Historical data (1930-2014):** Kaggle FIFA World Cup dataset
- **Recent matches (2022):** Fetched via `app/fetch_recent_matches.py` using API-Football
- **Live data:** API-Football REST API (real-time scores, stats, predictions)

## Testing

Run the automated edge-case test suite:
```bash
python app/test_edge_cases.py
```

## Known Limitations

- The free API-Football tier restricts historical fixture access for some
  seasons (2018 and current 2026 fixtures are not fully available).
- Player-level statistics for 2018-2026 tournaments are not included, only
  match-level results — the historical player dataset covers 1930-2014.
- Free tier API rate limits (100 requests/day) mean live features are cached
  for 30-60 seconds rather than fetched on every interaction.

## Future Scope

- "What-if" formation simulator to model tactical changes
- Richer player-level stats (passing, positional data) via a paid API tier
- Replace the rule-based recommender with a supervised ML model trained on
  match outcomes

---

Built as a B.Tech final year project (Data Science).
