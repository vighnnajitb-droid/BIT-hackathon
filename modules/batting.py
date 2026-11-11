"""
batting.py
Batting intelligence calculations, aggregations, metrics, and scoring models.
"""
import pandas as pd
import numpy as np

def calculate_batting_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes player batting metrics from ball-by-ball delivery data.
    - Excludes wides from balls faced.
    - Correctly accounts for dismissals and not-outs in batting average.
    """
    if df.empty or 'striker_name' not in df.columns:
        return pd.DataFrame()

    valid_batters = df[df['striker_name'].notna()].copy()
    if valid_batters.empty:
        return pd.DataFrame()

    # Balls faced: in cricket, wides do NOT count as balls faced by the batter.
    # No-balls DO count as balls faced by the batter.
    valid_batters['ball_faced'] = ~valid_batters['is_wide']

    # Innings identification: unique (match_id, innings) pair per batter
    valid_batters['match_innings'] = valid_batters['match_id'].astype(str) + "_" + valid_batters['innings'].astype(str)

    # Batter dismissals: dismissed_player_id matches striker_id
    # Or dismissed_player_id is not null and matches striker
    dismissals = valid_batters[valid_batters['dismissed_player_id'].notna() &
                               (valid_batters['dismissed_player_id'] == valid_batters['striker_id'])]
    dismissal_counts = dismissals.groupby('striker_name')['match_id'].count().to_dict()

    # Aggregate by striker
    agg = valid_batters.groupby('striker_name').agg(
        player_id=('striker_id', 'first'),
        runs=('runs', 'sum'),
        balls=('ball_faced', 'sum'),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum'),
        matches=('match_id', 'nunique'),
        innings=('match_innings', 'nunique'),
        dots=('runs', lambda r: (r == 0).sum())
    ).reset_index()

    agg['dismissals'] = agg['striker_name'].map(dismissal_counts).fillna(0).astype(int)
    agg['not_outs'] = np.maximum(0, agg['innings'] - agg['dismissals'])

    # Batting average
    agg['batting_average'] = np.where(agg['dismissals'] > 0, agg['runs'] / agg['dismissals'], np.nan)

    # Strike rate (runs per 100 balls)
    agg['strike_rate'] = np.where(agg['balls'] > 0, (agg['runs'] / agg['balls']) * 100, 0.0)

    # Boundary metrics
    agg['boundary_runs'] = (agg['fours'] * 4) + (agg['sixes'] * 6)
    agg['boundary_pct'] = np.where(agg['runs'] > 0, (agg['boundary_runs'] / agg['runs']) * 100, 0.0)
    agg['boundary_ball_pct'] = np.where(agg['balls'] > 0, ((agg['fours'] + agg['sixes']) / agg['balls']) * 100, 0.0)
    agg['dot_ball_pct'] = np.where(agg['balls'] > 0, (agg['dots'] / agg['balls']) * 100, 0.0)

    # Runs per innings
    agg['runs_per_innings'] = np.where(agg['innings'] > 0, agg['runs'] / agg['innings'], 0.0)

    # Rounding
    agg['strike_rate'] = agg['strike_rate'].round(2)
    agg['batting_average'] = agg['batting_average'].round(2)
    agg['boundary_pct'] = agg['boundary_pct'].round(1)
    agg['dot_ball_pct'] = agg['dot_ball_pct'].round(1)
    agg['runs_per_innings'] = agg['runs_per_innings'].round(1)

    return agg.sort_values(by=['runs', 'strike_rate'], ascending=[False, False])

def compute_batting_score(
    df_bat: pd.DataFrame,
    w_runs: float = 0.25,
    w_sr: float = 0.30,
    w_avg: float = 0.25,
    w_boundary: float = 0.10,
    w_consistency: float = 0.10,
    min_balls: int = 30
) -> pd.DataFrame:
    """
    Computes a transparent 0-100 batting performance score using configurable weights.
    Min-max normalizes metrics within the qualified pool and applies user weights.
    """
    if df_bat.empty:
        return df_bat

    df = df_bat.copy()
    qual = df[df['balls'] >= min_balls].copy()
    if qual.empty:
        df['batting_score'] = 0.0
        return df

    def norm(series):
        s_min = series.min()
        s_max = series.max()
        if s_max == s_min:
            return pd.Series(50.0, index=series.index)
        return ((series - s_min) / (s_max - s_min)) * 100

    # Fill NA average with runs or median for normalization
    avg_filled = qual['batting_average'].fillna(qual['runs'])

    score = (
        w_runs * norm(qual['runs']) +
        w_sr * norm(qual['sr_clipped'] if 'sr_clipped' in qual else qual['strike_rate'].clip(80, 220)) +
        w_avg * norm(avg_filled.clip(10, 60)) +
        w_boundary * norm(qual['boundary_pct']) +
        w_consistency * norm(qual['runs_per_innings'])
    )
    # Re-scale weights sum if user weights don't sum to 1
    total_w = w_runs + w_sr + w_avg + w_boundary + w_consistency
    if total_w > 0:
        score = score / total_w

    qual['batting_score'] = score.round(1)
    df = df.merge(qual[['striker_name', 'batting_score']], on='striker_name', how='left')
    df['batting_score'] = df['batting_score'].fillna(0.0)
    return df.sort_values(by='batting_score', ascending=False)

def get_season_batting_trends(df: pd.DataFrame, striker_name: str) -> pd.DataFrame:
    """Calculates year-by-year batting stats for a specific player."""
    player_data = df[df['striker_name'].str.lower() == striker_name.lower()].copy()
    if player_data.empty:
        return pd.DataFrame()

    player_data['ball_faced'] = ~player_data['is_wide']
    dismissals = player_data[player_data['dismissed_player_id'].notna() &
                             (player_data['dismissed_player_id'] == player_data['striker_id'])]
    d_map = dismissals.groupby('season')['match_id'].count().to_dict()

    agg = player_data.groupby('season').agg(
        runs=('runs', 'sum'),
        balls=('ball_faced', 'sum'),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum'),
        matches=('match_id', 'nunique'),
        innings=('match_id', lambda x: player_data.loc[x.index, 'match_id'].astype(str) + "_" + player_data.loc[x.index, 'innings'].astype(str)).nunique()
    ).reset_index()

    agg['dismissals'] = agg['season'].map(d_map).fillna(0).astype(int)
    agg['batting_average'] = np.where(agg['dismissals'] > 0, agg['runs'] / agg['dismissals'], np.nan).round(2)
    agg['strike_rate'] = np.where(agg['balls'] > 0, (agg['runs'] / agg['balls']) * 100, 0.0).round(2)
    return agg.sort_values('season')
