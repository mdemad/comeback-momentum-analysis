# Comeback Momentum, Chart Re-Entry, and Fandom Intensity Analysis

An analytics pipeline and interactive Streamlit web dashboard analyzing South Korea's daily Spotify Top 50 playlist data (May 18, 2024 – November 27, 2025). This project models song re-entry behaviors, measures comeback momentum surges, and calculates a **Fandom Intensity Score** to optimize release and promotion strategies for Atlantic Recording Corporation.

---

## Project Structure

```
kpop_momentum_analysis/
├── data/
│   └── spotify_south_korea_playlist.csv   # Normalized daily playlist dataset
├── src/
│   ├── __init__.py
│   ├── data_loader.py                     # Data loaders, deduplication, and cleaners
│   ├── analytics.py                       # Re-entry detection algorithms & KPI math
│   ├── verify_pipeline.py                 # Pipeline test and validation script
│   └── run_stats.py                       # CLI statistics summary reporter
├── app.py                                 # Streamlit dashboard application
├── requirements.txt                       # Python dependencies
├── README.md                              # This file
└── deliverables/
    ├── research_paper.md                  # Comprehensive academic/business report
    └── executive_summary.md               # 2-page briefing for government stakeholders
```

---

## Features

- **Executive KPI Dashboard**: Immediate insights on chart longevity, re-entry counts, peak comeback momentum, and average retention.
- **Re-Entry Timeline Visualizer**: A custom chart showing a song's exact rank trajectory, tracking its exits and comebacks over time.
- **Momentum Spike Analyzer**: A bubble chart plotting rank jump velocity vs. popularity gain, isolating fandom-driven climbs.
- **Fandom Intensity Leaderboard**: Song and artist rankings based on a compound score of re-entry frequency and velocity.
- **Content Attribute Analyzer**: Correlation studies investigating how release format (singles vs. album tracks), track duration, and content rating (explicit vs. clean) impact comeback success.

---

## Local Setup & Installation

### Prerequisites
- Python 3.9 or higher installed.

### Setup Steps
1. **Navigate to the Project Directory**:
   ```bash
   cd kpop_momentum_analysis
   ```

2. **Create a Virtual Environment**:
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the Virtual Environment**:
   - macOS / Linux:
     ```bash
     source .venv/bin/activate
     ```
   - Windows:
     ```cmd
     .venv\Scripts\activate
     ```

4. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   ```
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Verification Script**:
   Verify that the pipeline is executing correctly and generating analytics:
   ```bash
   python src/verify_pipeline.py
   ```

6. **Run the Streamlit Dashboard**:
   ```bash
   streamlit run app.py
   ```
   The dashboard will automatically open in your default browser at `http://localhost:8501`.

---

## How to Add to GitHub

To submit your internship project, follow these steps to push this code to a public GitHub repository:

1. **Create a new, empty repository on GitHub** (do not initialize with README, license, or `.gitignore` since they are already provided here).
2. **Open your terminal** in the project folder and run:
   ```bash
   # Initialize git repository
   git init

   # Add all files to staging
   git add .

   # Commit changes
   git commit -m "Initial commit: K-Pop playlist comeback momentum analysis"

   # Rename branch to main
   git branch -M main

   # Link your local repository to your remote GitHub repository
   # (Replace URL with your own repo URL)
   git remote add origin https://github.com/YOUR_USERNAME/kpop_momentum_analysis.git

   # Push changes to GitHub
   git push -u origin main
   ```

---

## How to Deploy the Streamlit Dashboard

To host your dashboard live for submission:

1. Go to [Share Streamlit](https://share.streamlit.io/) and log in using your GitHub account.
2. Click **New app**.
3. Select your repository (`kpop_momentum_analysis`), branch (`main`), and main file path (`app.py`).
4. Click **Deploy!** 
5. Copy your live dashboard URL (which will look like `https://xxx.streamlit.app`) for your submission link.

---

## Deliverables

Detailed reports are available in the `deliverables/` directory:
- **[Research Paper](file:///Users/mohamedemad/.gemini/antigravity/scratch/kpop_momentum_analysis/deliverables/research_paper.md)**: A detailed analytical paper explaining our methodology, mathematical models, empirical findings (such as the 4.2x clean content advantage), and strategic marketing recommendations.
- **[Executive Summary](file:///Users/mohamedemad/.gemini/antigravity/scratch/kpop_momentum_analysis/deliverables/executive_summary.md)**: An executive briefing tailored for government and industry policy stakeholders, summarizing how fandom-driven streaming acts as a digital export driver.
