# SupeRR Selector — Season 2
### *Decode Performance. Discover Potential. Build the Winning Squad.*

A premier sports-tech cricket intelligence and player scouting platform designed for Rajasthan Royals (RR) and IPL auction preparation.

---

## 🌟 Executive Summary

**SupeRR Selector Season 2** is a franchise-grade cricket intelligence platform built to evaluate cricket performances, compare players across eras and match phases, unearth emerging talent, and support evidence-based IPL auction decisions.

Engineered with a bespoke **Rajasthan Royals** visual identity—featuring deep midnight navy, royal pink accents, electric cyan indicators, glassmorphic cards, and interactive Plotly visualizations.

---

## 🚀 Key Modules & Architecture

The application is structured into 9 dedicated operational workspaces:

1. **Executive Overview**
   Dataset-level telemetry and verified aggregate performance metrics: total deliveries analyzed, matches covered, unique batters & bowlers, boundary distributions, season trends, and competition volumes.

2. **Batting Intelligence**
   Comprehensive batting analytics: runs, balls faced (excluding wides), strike rate, batting average (accurately tracking dismissals and not-outs), boundary percentages, dot-ball percentages, and a transparent, user-weighted **Batting Performance Score (0–100)**.

3. **Bowling Intelligence**
   Precise bowling performance analytics: wickets (excluding run-outs and non-bowler dismissals), legal balls, overs bowled, accurately calculated bowler conceded runs (including wide and no-ball penalties), economy rates, bowling averages, dot-ball percentages, and a configurable **Bowling Performance Score (0–100)**.

4. **Pressure Lab**
   Detailed match-phase breakdowns:
   - **Powerplay** (Overs 1–6)
   - **Middle Overs** (Overs 7–15)
   - **Death Overs** (Overs 16–20)
   Includes empirical statistical proxies for death overs batting impact and bowling control.

5. **Player Explorer**
   Individual 360-degree player dossier: multi-season career trajectory, phase-by-phase scoring rates, bowling economy, tournament registrations, and team mappings.

6. **RR Scouting Room** *(Central Feature)*
   Targeted scouting engine with role classification:
   - Top-Order Batters
   - Middle-Order Batters
   - Finishers / Lower-Order
   - All-Rounders (Pace & Spin)
   - Pace Bowlers & Spin Bowlers
   Features a multi-metric scoring model with configurable sliders, an interactive candidate shortlist manager with session persistence, and instant CSV export.

7. **Player Comparison**
   Head-to-head comparison workspace supporting 2 to 5 players simultaneously:
   - Multidimensional skill radar chart
   - Direct side-by-side metric tables
   - Factual algorithmic summary of statistical strengths and limitations.

8. **Auction Intelligence**
   IPL war room strategy board featuring:
   - Scouting shortlist role composition
   - Customizable mock purse budget and squad slot planner
   - Strict analytical integrity policy: **zero fabricated prices, retention lists, or budgets**; all financials are explicit user-configurable planning parameters.
   - Downloadable auction war room dossier.

9. **Data Quality & Methodology**
   Full audit trail of all source CSV datasets (row counts, column dimensions, null distributions, duplicates) alongside explicit definitions and formulas for all cricket metrics.

---

## 📂 Project Directory Structure

```text
SupeRR_Selector_Season2/
│
├── app.py                     # Main Streamlit application
├── requirements.txt           # Project dependencies
├── README.md                  # Comprehensive documentation
├── .gitignore                 # Version control configuration
│
├── data/                      # Original verified CSV datasets
│   ├── ball_by_ball.csv       # 200,999 delivery records
│   ├── matches.csv            # 883 match records
│   ├── competitions.csv       # 141 competitions (IPL + T20/T20I)
│   ├── teams.csv              # Franchise and national teams
│   ├── playing_eleven.csv     # Lineup and player status records
│   └── competition_team_player_mapping.csv
│
├── assets/                    # Styling assets and branding
│
├── modules/                   # Reusable modular logic
│   ├── data_loader.py         # Data loading, merge, and cleaning
│   ├── batting.py             # Batting metrics and scoring
│   ├── bowling.py             # Bowling metrics and scoring
│   ├── pressure_lab.py        # Phase splits and pressure proxies
│   ├── scouting.py            # Role derivation and scouting model
│   ├── player_comparison.py   # Comparison logic and radar charts
│   ├── auction.py             # Auction planner and dossier generator
│   ├── methodology.py         # Integrity audit and formula dictionary
│   └── ui_theme.py            # Rajasthan Royals custom CSS and theme
│
└── tests/
    └── test_calculations.py   # Automated unit tests (7 test suites)
```

---

## ⚡ Installation & Local Setup

### 1. Prerequisites
- Python 3.10+ (Python 3.11 or 3.12 recommended)

### 2. Environment Setup
```bash
# Clone or extract repository
cd SupeRR_Selector_Season2

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows PowerShell:
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Testing and Validation

Run the automated test suite:
```bash
python -m unittest discover tests
```
The test suite validates:
- Dataset integrity and relational joins across 200,999 deliveries.
- Batting strike rate, average, and boundary formulas.
- Bowling legal deliveries, conceded runs, and economy rates.
- Match phase segmentation and pressure proxy calculations.
- Role derivation and scouting multi-metric weighting.
- Head-to-head comparison profiles and factual strengths/limitations.
- Data quality audit outputs and metric formulas.

---

## 📐 Cricket Analytics Methodology & Formulas

- **Batting Balls Faced:** In strict adherence to MCC Law 22, **wides are excluded** from balls faced. No-balls are included.
- **Batting Average:** Calculated as `Runs / Dismissals`. Undefeated batters (0 dismissals) are handled without division-by-zero errors.
- **Bowler Conceded Runs:** Calculated as `Batter Runs off the bat + Wide Extras + No-ball Penalties + Boundary Extra Runs`. Leg-byes and byes are **not** attributed to the bowler.
- **Bowling Economy:** Calculated as `(Runs Conceded / Legal Deliveries) × 6`.
- **Match Phases:**
  - **Powerplay:** Overs 1 to 6
  - **Middle:** Overs 7 to 15
  - **Death:** Overs 16 to 20
- **Pressure Proxies:** Stated explicitly as empirical observational proxies, not validated psychological measures.

---

## 🛡️ License & Acknowledgements
Built for the **SupeRR Selector Season 2 Hackathon**. Inspired by Rajasthan Royals high-performance analytics.
