# TacticAI — Player Analytics & Match Strategy Recommender

## Day 1 — Environment Setup (do this today)

### 1. Project folder structure (already created for you)
```
tacticai/
├── data/         # raw and cleaned datasets go here
├── notebooks/    # Jupyter notebooks for EDA and experiments
├── app/          # Python scripts and Streamlit app
├── docs/         # report, screenshots, diagrams
├── requirements.txt
├── .env.example
└── .gitignore
```

### 2. Create a virtual environment
```bash
cd tacticai
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install all required libraries
```bash
pip install -r requirements.txt
```

### 4. Initialize Git repo
```bash
git init
git add .
git commit -m "Day 1: project setup"
```
Push it to GitHub (create a new repo on github.com first, then):
```bash
git remote add origin <your-repo-url>
git push -u origin main
```

### 5. Sign up for API-Football (needed for Day 2, but do it today so key is ready)
1. Go to https://rapidapi.com/api-sports/api/api-football
2. Sign up (free tier gives 100 requests/day — enough for development)
3. Copy your API key
4. Rename `.env.example` to `.env` and paste your key inside

### Day 1 checklist
- [ ] Folder structure created
- [ ] Virtual environment working
- [ ] All libraries installed without errors
- [ ] Git repo initialized and pushed to GitHub
- [ ] RapidAPI account created, key saved in `.env`

Tomorrow (Day 2) we'll test the API connection and start pulling Kaggle datasets.
