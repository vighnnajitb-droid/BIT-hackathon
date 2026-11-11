"""
bowling.py
Bowling intelligence calculations, aggregations, metrics, and scoring models.
"""
import pandas as pd
import numpy as np

def calculate_bowling_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes bowler performance metrics:
    - Only legal balls count towards overs bowled.
    - Bowler conceded runs include batter runs off the bat + wide extras + no-ball extras.
    - Excludes non-bowler wickets (Run Out, Retire Out, etc.).
    """
    if df.empty or 'bowler_name' not in df.columns:
        return pd.DataFrame()

    valid_bowlers = df[df['bowler_name'].notna()].copy()
    if valid_bowlers.empty:
        return pd.DataFrame()

    valid_bowlers['match_innings'] = valid_bowlers['match_id'].astype(str) + "_" + valid_bowlers['innings'].astype(str)

    # Dot ball: legal ball with 0 bowler conceded runs
    valid_bowlers['is_dot'] = valid_bowlers['is_legal_delivery'] & (valid_bowlers['bowler_conceded_runs'] == 0)

    agg = valid_bowlers.groupby('bowler_name').agg(
        player_id=('bowler_id', 'first'),
        pace_or_spin=('pace_or_spin', lambda s: s.mode()[0] if not s.mode().empty else 'Unknown'),
        bowling_type=('bowling_type', lambda s: s.mode()[0] if not s.mode().empty else 'Unknown'),
        balls=('is_legal_delivery', 'sum'),
        conceded=('bowler_conceded_runs', 'sum'),
        wickets=('is_bowler_wicket', 'sum'),
        matches=('match_id', 'nunique'),
        innings=('match_innings', 'nunique'),
        dots=('is_dot', 'sum'),
        wides=('is_wide', 'sum'),
        noballs=('is_noball', 'sum')
    ).reset_index()

    # Overs bowled (e.g. 10 balls = 1.4 overs)
    agg['overs'] = (agg['balls'] // 6) + ((agg['balls'] % 6) / 10.0)

    # Economy rate: runs conceded per 6 legal balls
    agg['economy'] = np.where(agg['balls'] > 0, (agg['conceded'] / agg['balls']) * 6.0, np.nan)

    # Bowling average: runs conceded per wicket
    agg['bowling_average'] = np.where(agg['wickets'] > 0, agg['conceded'] / agg['wickets'], np.nan)

    # Bowling strike rate: legal balls per wicket
    agg['bowling_strike_rate'] = np.where(agg['wickets'] > 0, agg['balls'] / agg['wickets'], np.nan)

    # Dot ball %
    agg['dot_ball_pct'] = np.where(agg['balls'] > 0, (agg['dots'] / agg['balls']) * 100, 0.0)

    # Wickets per innings
    agg['wickets_per_innings'] = np.where(agg['innings'] > 0, agg['wickets'] / agg['innings'], 0.0)

    # Rounding
    agg['economy'] = agg['economy'].round(2)
    agg['bowling_average'] = agg['bowling_average'].round(2)
    agg['bowling_strike_rate'] = agg['bowling_strike_rate'].round(2)
    agg['dot_ball_pct'] = agg['dot_ball_pct'].round(1)
    agg['wickets_per_innings'] = agg['wickets_per_innings'].round(2)

    return agg.sort_values(by=['wickets', 'economy'], ascending=[False, True])

def compute_bowling_score(
    df_bowl: pd.DataFrame,
    w_wickets: float = 0.30,
    w_econ: float = 0.25,
    w_avg: float = 0.20,
    w_sr: float = 0.15,
    w_dots: float = 0.10,
    min_balls: int = 36
) -> pd.DataFrame:
    """
    Computes a transparent 0-100 bowling performance score using configurable weights.
    Higher wickets & dot ball % boost the score; lower economy, average, & strike rate boost the score.
    """
    if df_bowl.empty:
        return df_bowl

    df = df_bowl.copy()
    qual = df[df['balls'] >= min_balls].copy()
    if qual.empty:
        df['bowling_score'] = 0.0
        return df

    def norm_pos(series):
        s_min = series.min()
        s_max = series.max()
        if s_max == s_min:
            return pd.Series(50.0, index=series.index)
        return ((series - s_min) / (s_max - s_min)) * 100

    def norm_neg(series):
        # Inverted normalization where lower value is better
        s_min = series.min()
        s_max = series.max()
        if s_max == s_min:
            return pd.Series(50.0, index=series.index)
        return ((s_max - series) / (s_max - s_min)) * 100

    # Fill NA average and strike rate with upper cap for normalization
    avg_filled = qual['bowling_average'].fillna(60.0).clip(12.0, 50.0)
    sr_filled = qual['bowling_strike_rate'].fillna(40.0).clip(10.0, 36.0)
    econ_clipped = qual['economy'].clip(5.0, 12.0)

    score = (
        w_wickets * norm_pos(qual['wickets']) +
        w_econ * norm_neg(econ_clipped) +
        w_avg * norm_neg(avg_filled) +
        w_sr * norm_neg(sr_filled) +
        w_dots * norm_pos(qual['dot_ball_pct'])
    )

    total_w = w_wickets + w_econ + w_avg + w_sr + w_dots
    if total_w > 0:
        score = score / total_w

    qual['bowling_score'] = score.round(1)
    df = df.merge(qual[['bowler_name', 'bowling_score']], on='bowler_name', how='left')
    df['bowling_score'] = df['bowling_score'].fillna(0.0)
    return df.sort_values(by='bowling_score', ascending=False)

def get_season_bowling_trends(df: pd.DataFrame, bowler_name: str) -> pd.DataFrame:
    """Calculates year-by-year bowling stats for a specific player."""
    player_data = df[df['bowler_name'].str.lower() == bowler_name.lower()].copy()
    if player_data.empty:
        return pd.DataFrame()

    player_data['match_innings'] = player_data['match_id'].astype(str) + "_" + player_data['innings'].astype(str)
    player_data['is_dot'] = player_data['is_legal_delivery'] & (player_data['bowler_conceded_runs'] == 0)

    agg = player_data.groupby('season').agg(
        balls=('is_legal_delivery', 'sum'),
        conceded=('bowler_conceded_runs', 'sum'),
        wickets=('is_bowler_wicket', 'sum'),
        matches=('match_id', 'nunique'),
        dots=('is_dot', 'sum')
    ).reset_index()

    agg['economy'] = np.where(agg['balls'] > 0, (agg['conceded'] / agg['balls']) * 6.0, np.nan).round(2)
    agg['bowling_average'] = np.where(agg['wickets'] > 0, agg['conceded'] / agg['wickets'], np.nan).round(2)
    agg['dot_ball_pct'] = np.where(agg['balls'] > 0, (agg['dots'] / agg['balls']) * 100, 0.0).round(1)
    return agg.sort_values('season')
