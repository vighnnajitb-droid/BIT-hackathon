"""
scouting.py
RR Scouting Room logic:
- Reliable role derivation (Top-order, Middle-order, Finisher, All-Rounder, Pace, Spin, Death Specialist).
- Multi-criteria transparent scoring model with configurable user weights.
- Shortlist state management and shortlist evaluation.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any

def derive_player_roles(df_bb: pd.DataFrame, df_bat: pd.DataFrame, df_bowl: pd.DataFrame) -> pd.DataFrame:
    """
    Derives realistic player primary and secondary roles based on actual observed data:
    - Batting order distribution (positions 1-3 = Top Order, 4-5 = Middle Order, 6+ = Lower Order / Finisher)
    - Bowling workload (balls bowled, pace vs spin)
    - All-rounder classification (meaningful output in both batting and bowling)
    """
    roles = {}

    # 1. Batting order profile
    order_profile = {}
    if not df_bb.empty and 'striker_name' in df_bb.columns and 'batting_order' in df_bb.columns:
        valid_orders = df_bb[df_bb['striker_name'].notna() & df_bb['batting_order'].notna()]
        median_orders = valid_orders.groupby('striker_name')['batting_order'].median().to_dict()
        order_profile = median_orders

    # 2. Bowling type & pace/spin
    bowling_styles = {}
    if not df_bowl.empty:
        for _, row in df_bowl.iterrows():
            bowling_styles[row['bowler_name']] = {
                'pace_or_spin': row.get('pace_or_spin', 'Unknown'),
                'bowling_type': row.get('bowling_type', 'Unknown'),
                'wickets': row.get('wickets', 0),
                'balls': row.get('balls', 0),
                'economy': row.get('economy', np.nan)
            }

    # Combine unique players
    all_players = set()
    if not df_bat.empty:
        all_players.update(df_bat['striker_name'].dropna().tolist())
    if not df_bowl.empty:
        all_players.update(df_bowl['bowler_name'].dropna().tolist())

    bat_map = df_bat.set_index('striker_name').to_dict('index') if not df_bat.empty else {}

    roster = []
    for player in sorted(all_players):
        b_data = bat_map.get(player, {})
        w_data = bowling_styles.get(player, {})

        runs = b_data.get('runs', 0)
        balls_faced = b_data.get('balls', 0)
        sr = b_data.get('strike_rate', 0.0)
        avg = b_data.get('batting_average', np.nan)
        med_order = order_profile.get(player, 5.0)

        wickets = w_data.get('wickets', 0)
        balls_bowled = w_data.get('balls', 0)
        econ = w_data.get('economy', np.nan)
        p_or_s = w_data.get('pace_or_spin', 'Unknown')
        b_type = w_data.get('bowling_type', 'Unknown')

        # Role logic
        is_significant_bat = runs >= 100 or balls_faced >= 75
        is_significant_bowl = balls_bowled >= 72 or wickets >= 5

        if is_significant_bat and is_significant_bowl:
            role = f"All-Rounder ({p_or_s})"
        elif is_significant_bowl:
            if p_or_s.lower() == 'spin' or 'spin' in b_type.lower() or 'break' in b_type.lower() or 'orthodox' in b_type.lower():
                role = "Spin Bowler"
            else:
                role = "Pace Bowler"
        elif is_significant_bat:
            if med_order <= 3.2:
                role = "Top-Order Batter"
            elif med_order <= 5.2:
                role = "Middle-Order Batter"
            else:
                role = "Finisher / Lower-Order"
        else:
            role = "Emerging / Reserve"

        roster.append({
            'player_name': player,
            'derived_role': role,
            'median_batting_order': round(med_order, 1) if player in order_profile else np.nan,
            'runs': runs,
            'balls_faced': balls_faced,
            'strike_rate': sr,
            'batting_average': avg,
            'wickets': wickets,
            'balls_bowled': balls_bowled,
            'economy': econ,
            'pace_or_spin': p_or_s,
            'bowling_type': b_type
        })

    return pd.DataFrame(roster)

def compute_scouting_score(
    df_roster: pd.DataFrame,
    role_filter: str = "All",
    w_bat: float = 0.35,
    w_bowl: float = 0.35,
    w_sr: float = 0.15,
    w_econ: float = 0.15,
    min_deliveries: int = 30
) -> pd.DataFrame:
    """
    Computes a customizable, transparent scouting rating (0-100)
    balancing batting output, bowling output, strike rate, and economy.
    """
    if df_roster.empty:
        return pd.DataFrame()

    df = df_roster.copy()
    if role_filter != "All":
        df = df[df['derived_role'].str.contains(role_filter, case=False, na=False)].copy()

    # Deliveries filter (either balls faced or balls bowled >= min)
    df = df[(df['balls_faced'] >= min_deliveries) | (df['balls_bowled'] >= min_deliveries)].copy()
    if df.empty:
        return pd.DataFrame()

    def norm(s):
        s_min = s.min()
        s_max = s.max()
        if s_max == s_min:
            return pd.Series(50.0, index=s.index)
        return ((s - s_min) / (s_max - s_min)) * 100

    def norm_neg(s):
        s_min = s.min()
        s_max = s.max()
        if s_max == s_min:
            return pd.Series(50.0, index=s.index)
        return ((s_max - s) / (s_max - s_min)) * 100

    norm_runs = norm(df['runs'])
    norm_wickets = norm(df['wickets'])
    norm_sr = norm(df['strike_rate'].clip(60, 220))
    norm_econ = norm_neg(df['economy'].fillna(12.0).clip(5.0, 12.0))

    score = (
        w_bat * norm_runs +
        w_bowl * norm_wickets +
        w_sr * norm_sr +
        w_econ * norm_econ
    )
    total_w = w_bat + w_bowl + w_sr + w_econ
    if total_w > 0:
        score = score / total_w

    df['scouting_score'] = score.round(1)
    return df.sort_values(by='scouting_score', ascending=False)
