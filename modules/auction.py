"""
auction.py
Auction Intelligence workspace:
- Scouting shortlist review & role composition
- Configurable auction planner (purse budget, target role slots)
- Zero fabricated prices or retention lists: strictly user-entered assumptions
- Exportable auction scouting dossier
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any

def create_initial_auction_plan(total_purse_cr: float = 120.0, total_slots: int = 25) -> Dict[str, Any]:
    """Sets up default user-configurable parameters for an auction war room."""
    return {
        'total_purse_cr': total_purse_cr,
        'remaining_purse_cr': total_purse_cr,
        'total_slots': total_slots,
        'overseas_slots_max': 8,
        'squad_targets': {
            'Top-Order Batter': 4,
            'Middle-Order Batter': 4,
            'Finisher / Lower-Order': 3,
            'All-Rounder (Pace)': 3,
            'All-Rounder (Spin)': 2,
            'Pace Bowler': 5,
            'Spin Bowler': 4,
        }
    }

def analyze_shortlist_composition(shortlist_players: List[str], df_roster: pd.DataFrame) -> Dict[str, Any]:
    """Analyzes the role breakdown and readiness of the user's shortlisted candidates."""
    if not shortlist_players or df_roster.empty:
        return {'total_shortlisted': 0, 'role_counts': {}, 'players': []}

    sub = df_roster[df_roster['player_name'].isin(shortlist_players)].copy()
    role_counts = sub['derived_role'].value_counts().to_dict()

    return {
        'total_shortlisted': len(sub),
        'role_counts': role_counts,
        'players': sub.to_dict('records')
    }

def generate_auction_report_df(shortlist_df: pd.DataFrame) -> pd.DataFrame:
    """Prepares clean data table for auction strategy export."""
    if shortlist_df.empty:
        return pd.DataFrame()

    export_cols = [
        'player_name', 'derived_role', 'runs', 'balls_faced',
        'strike_rate', 'batting_average', 'wickets', 'balls_bowled',
        'economy', 'scouting_score'
    ]
    cols = [c for c in export_cols if c in shortlist_df.columns]
    return shortlist_df[cols].copy()
