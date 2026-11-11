"""
pressure_lab.py
Match phase and pressure analytics:
- Powerplay (overs 1-6)
- Middle overs (overs 7-15)
- Death overs (overs 16-20)
- Batting under wicket pressure (e.g. 3+ wickets down)
- Bowling in death & high-pressure phases
All pressure indices are explicitly marked as empirical statistical proxies.
"""
import pandas as pd
import numpy as np

def calculate_phase_batting(df: pd.DataFrame, phase: str) -> pd.DataFrame:
    """Computes batting metrics for a specific match phase (Powerplay, Middle, Death)."""
    sub = df[df['phase'] == phase].copy()
    if sub.empty:
        return pd.DataFrame()

    sub['ball_faced'] = ~sub['is_wide']
    dismissals = sub[sub['dismissed_player_id'].notna() &
                     (sub['dismissed_player_id'] == sub['striker_id'])]
    d_map = dismissals.groupby('striker_name')['match_id'].count().to_dict()

    agg = sub.groupby('striker_name').agg(
        runs=('runs', 'sum'),
        balls=('ball_faced', 'sum'),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum'),
        dots=('runs', lambda r: (r == 0).sum()),
        matches=('match_id', 'nunique')
    ).reset_index()

    agg['dismissals'] = agg['striker_name'].map(d_map).fillna(0).astype(int)
    agg['strike_rate'] = np.where(agg['balls'] > 0, (agg['runs'] / agg['balls']) * 100, 0.0).round(2)
    agg['batting_average'] = np.where(agg['dismissals'] > 0, agg['runs'] / agg['dismissals'], np.nan).round(2)
    agg['boundary_pct'] = np.where(agg['runs'] > 0, ((agg['fours'] * 4 + agg['sixes'] * 6) / agg['runs']) * 100, 0.0).round(1)
    agg['dot_ball_pct'] = np.where(agg['balls'] > 0, (agg['dots'] / agg['balls']) * 100, 0.0).round(1)
    agg['phase'] = phase
    return agg.sort_values(by=['runs', 'strike_rate'], ascending=[False, False])

def calculate_phase_bowling(df: pd.DataFrame, phase: str) -> pd.DataFrame:
    """Computes bowling metrics for a specific match phase."""
    sub = df[df['phase'] == phase].copy()
    if sub.empty:
        return pd.DataFrame()

    sub['is_dot'] = sub['is_legal_delivery'] & (sub['bowler_conceded_runs'] == 0)

    agg = sub.groupby('bowler_name').agg(
        pace_or_spin=('pace_or_spin', lambda s: s.mode()[0] if not s.mode().empty else 'Unknown'),
        balls=('is_legal_delivery', 'sum'),
        conceded=('bowler_conceded_runs', 'sum'),
        wickets=('is_bowler_wicket', 'sum'),
        dots=('is_dot', 'sum'),
        matches=('match_id', 'nunique')
    ).reset_index()

    agg['overs'] = (agg['balls'] // 6) + ((agg['balls'] % 6) / 10.0)
    agg['economy'] = np.where(agg['balls'] > 0, (agg['conceded'] / agg['balls']) * 6.0, np.nan).round(2)
    agg['bowling_strike_rate'] = np.where(agg['wickets'] > 0, agg['balls'] / agg['wickets'], np.nan).round(2)
    agg['dot_ball_pct'] = np.where(agg['balls'] > 0, (agg['dots'] / agg['balls']) * 100, 0.0).round(1)
    agg['phase'] = phase
    return agg.sort_values(by=['wickets', 'economy'], ascending=[False, True])

def calculate_pressure_batting_proxy(df: pd.DataFrame, min_balls: int = 30) -> pd.DataFrame:
    """
    Experimental pressure proxy for batters:
    Evaluates death overs performance (overs 16-20) and situations when team has lost wickets early.
    Note: Stored as statistical proxy, not validated temperament metric.
    """
    death_df = df[df['phase'] == 'Death'].copy()
    death_agg = calculate_phase_batting(death_df, 'Death')
    if death_agg.empty:
        return pd.DataFrame()

    qual = death_agg[death_agg['balls'] >= min_balls].copy()
    if qual.empty:
        return pd.DataFrame()

    # Experimental proxy score: balance of death strike rate, boundary %, and dot control
    sr_norm = ((qual['strike_rate'].clip(100, 240) - 100) / 140.0) * 100
    bnd_norm = ((qual['boundary_pct'].clip(30, 90) - 30) / 60.0) * 100
    dot_ctrl = 100 - qual['dot_ball_pct'].clip(10, 60)

    qual['death_impact_proxy'] = (0.50 * sr_norm + 0.30 * bnd_norm + 0.20 * dot_ctrl).round(1)
    return qual.sort_values('death_impact_proxy', ascending=False)

def calculate_pressure_bowling_proxy(df: pd.DataFrame, min_balls: int = 30) -> pd.DataFrame:
    """
    Experimental pressure proxy for bowlers:
    Evaluates death overs performance (overs 16-20) focusing on economy and wicket strike rate.
    """
    death_df = df[df['phase'] == 'Death'].copy()
    death_agg = calculate_phase_bowling(death_df, 'Death')
    if death_agg.empty:
        return pd.DataFrame()

    qual = death_agg[death_agg['balls'] >= min_balls].copy()
    if qual.empty:
        return pd.DataFrame()

    # Experimental proxy score: lower economy is better, more wickets is better
    econ_norm = ((14.0 - qual['economy'].clip(6.0, 14.0)) / 8.0) * 100
    w_norm = ((qual['wickets'] - qual['wickets'].min()) / max(1, qual['wickets'].max() - qual['wickets'].min())) * 100
    dots_norm = qual['dot_ball_pct']

    qual['death_control_proxy'] = (0.45 * econ_norm + 0.35 * w_norm + 0.20 * dots_norm).round(1)
    return qual.sort_values('death_control_proxy', ascending=False)
