"""
data_loader.py
Module for locating, loading, caching, and merging the SupeRR Selector datasets.
"""
from pathlib import Path
import pandas as pd
import numpy as np

def get_data_dir() -> Path:
    """Detects where the CSV datasets are located."""
    possible_dirs = [
        Path(__file__).parent.parent / "data",
        Path(__file__).parent.parent,
        Path("/app/data"),
        Path("/tmp/file_attachments/SupeRR_Selector_Premium_Dashboard/rrpack"),
        Path.cwd() / "data",
        Path.cwd(),
    ]
    for d in possible_dirs:
        if (d / "ball_by_ball.csv").is_file() and (d / "matches.csv").is_file():
            return d
    return Path(__file__).parent.parent / "data"

def load_raw_datasets(data_dir: Path | None = None):
    """Loads raw CSV files from data directory."""
    if data_dir is None:
        data_dir = get_data_dir()

    bb = pd.read_csv(data_dir / "ball_by_ball.csv", low_memory=False)
    matches = pd.read_csv(data_dir / "matches.csv")
    comps = pd.read_csv(data_dir / "competitions.csv")
    mapping = pd.read_csv(data_dir / "competition_team_player_mapping.csv")

    teams_path = data_dir / "teams.csv"
    teams = pd.read_csv(teams_path) if teams_path.is_file() else pd.DataFrame(columns=["comp_id", "team_id", "team_name"])

    p11_path = data_dir / "playing_eleven.csv"
    p11 = pd.read_csv(p11_path) if p11_path.is_file() else pd.DataFrame()

    return bb, matches, comps, mapping, teams, p11

def process_and_merge_data(bb, matches, comps, mapping, teams):
    """
    Cleans types and joins matches and competitions onto ball_by_ball.
    """
    # Type normalization
    for col in ['match_id', 'innings', 'overid', 'over_ball_num', 'innings_ball_num',
                'batting_team_id', 'bowling_team_id', 'striker_id', 'non_striker_id',
                'bowler_id', 'batting_order', 'runs', 'extras1_runs', 'extras_2_runs']:
        if col in bb.columns:
            bb[col] = pd.to_numeric(bb[col], errors='coerce')

    for col in ['match_id', 'comp_id', 'home_team_id', 'away_team_id', 'win_team_id']:
        if col in matches.columns:
            matches[col] = pd.to_numeric(matches[col], errors='coerce')

    if 'comp_id' in comps.columns:
        comps['comp_id'] = pd.to_numeric(comps['comp_id'], errors='coerce')
    if 'season' in comps.columns:
        comps['season'] = comps['season'].astype(str)

    # Boolean flags
    bb['is_wicket'] = bb['is_wicket'].astype(str).str.lower().isin(['true', '1'])
    bb['is_four'] = bb['is_four'].astype(str).str.lower().isin(['true', '1'])
    bb['is_six'] = bb['is_six'].astype(str).str.lower().isin(['true', '1'])

    # Legal deliveries: excludes wides and no-balls (Overstep)
    extras_type_clean = bb['extras_type'].fillna('').astype(str).str.strip().str.lower()
    bb['is_wide'] = extras_type_clean.eq('wide')
    bb['is_noball'] = extras_type_clean.isin(['overstep', 'no ball', 'noball'])
    bb['is_legal_delivery'] = ~bb['is_wide'] & ~bb['is_noball']

    # Bowler conceded runs calculation:
    # Batter runs + 1 run penalty for wide + 1 run penalty for no-ball + any extra boundary runs (extras_2_runs)
    # Leg-byes and byes do NOT count against the bowler in cricket
    extra_runs = pd.to_numeric(bb['extras_2_runs'], errors='coerce').fillna(0)
    penalty_runs = bb['is_wide'].astype(int) + bb['is_noball'].astype(int)
    bb['bowler_conceded_runs'] = np.where(
        bb['is_wide'],
        1 + extra_runs,
        bb['runs'].fillna(0) + penalty_runs + extra_runs
    )

    # Bowler wicket: excludes RunOut, Retire Out, Obstructing the Field, etc.
    non_bowler_dismissals = {'runout', 'run out', 'retire out', 'retired out', 'obstructing the field', 'hit the ball twice', 'timed out'}
    dismissal_clean = bb['dismissal_type'].fillna('').astype(str).str.strip().str.lower()
    bb['is_bowler_wicket'] = bb['is_wicket'] & ~dismissal_clean.isin(non_bowler_dismissals)

    # Match phase classification
    # Overs 1 to 6: Powerplay, 7 to 15: Middle, 16 to 20: Death
    bb['phase'] = pd.cut(
        bb['overid'],
        bins=[0, 6, 15, 20, 100],
        labels=['Powerplay', 'Middle', 'Death', 'Other'],
        right=True
    ).astype(str)

    # Join matches metadata
    match_cols = [c for c in ['match_id', 'comp_id', 'match_date', 'stage', 'venue_country',
                              'home_team', 'away_team', 'home_team_id', 'away_team_id', 'win_team_id', 'result'] if c in matches.columns]
    bb = bb.merge(matches[match_cols], on='match_id', how='left')

    # Join competitions metadata
    comp_cols = [c for c in ['comp_id', 'comp_name', 'match_format', 'season'] if c in comps.columns]
    bb = bb.merge(comps[comp_cols], on='comp_id', how='left')

    # Create team names lookup mapping for batting_team and bowling_team
    if not teams.empty and 'team_id' in teams.columns and 'team_name' in teams.columns:
        teams_unique = teams[['team_id', 'team_name']].drop_duplicates()
        team_map = dict(zip(teams_unique['team_id'], teams_unique['team_name']))
        bb['batting_team_name'] = bb['batting_team_id'].map(team_map).fillna('Unknown')
        bb['bowling_team_name'] = bb['bowling_team_id'].map(team_map).fillna('Unknown')
    else:
        bb['batting_team_name'] = 'Unknown'
        bb['bowling_team_name'] = 'Unknown'

    return bb, matches, comps, mapping, teams

def get_complete_data():
    """Top-level helper to load and return processed data."""
    bb, matches, comps, mapping, teams, p11 = load_raw_datasets()
    bb, matches, comps, mapping, teams = process_and_merge_data(bb, matches, comps, mapping, teams)
    return bb, matches, comps, mapping, teams, p11
