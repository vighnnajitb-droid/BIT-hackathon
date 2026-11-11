"""
methodology.py
Data Quality, integrity validation, and mathematical documentation.
"""
import pandas as pd
from typing import Dict, Any, List

def audit_datasets(bb, matches, comps, mapping, teams) -> List[Dict[str, Any]]:
    """Performs integrity checks and computes summary stats for all input tables."""
    datasets = [
        ('ball_by_ball.csv', bb),
        ('matches.csv', matches),
        ('competitions.csv', comps),
        ('competition_team_player_mapping.csv', mapping),
        ('teams.csv', teams)
    ]

    report = []
    for name, df in datasets:
        if df is None or df.empty:
            report.append({
                'Dataset': name,
                'Rows': 0,
                'Columns': 0,
                'Null Values': 0,
                'Duplicate Rows': 0,
                'Status': 'Empty or Missing'
            })
            continue

        total_cells = df.size
        null_count = int(df.isna().sum().sum())
        null_pct = round((null_count / total_cells) * 100, 1) if total_cells > 0 else 0
        dup_count = int(df.duplicated().sum())

        report.append({
            'Dataset': name,
            'Rows': len(df),
            'Columns': len(df.columns),
            'Null Values': f"{null_count:,} ({null_pct}%)",
            'Duplicate Rows': dup_count,
            'Status': 'Verified & Active'
        })

    return report

def get_formula_definitions() -> List[Dict[str, str]]:
    """Returns cricket statistical formula documentation."""
    return [
        {
            'Metric': 'Batting Strike Rate',
            'Formula': '(Runs Scored / Legal Balls Faced) × 100',
            'Analytical Note': 'Wides are strictly excluded from balls faced. No-balls are included.'
        },
        {
            'Metric': 'Batting Average',
            'Formula': 'Runs Scored / Dismissals',
            'Analytical Note': 'Not-outs do not increment dismissals. Undefeated batters with 0 dismissals show as undefined/infinite.'
        },
        {
            'Metric': 'Boundary Percentage',
            'Formula': '((Fours × 4 + Sixes × 6) / Runs Scored) × 100',
            'Analytical Note': 'Measures proportion of total scoring produced in boundaries.'
        },
        {
            'Metric': 'Bowling Economy Rate',
            'Formula': '(Runs Conceded / Legal Balls Bowled) × 6',
            'Analytical Note': 'Bowler runs include batter runs off the bat + wide extras + no-ball extras. Leg-byes and byes are excluded.'
        },
        {
            'Metric': 'Bowling Strike Rate',
            'Formula': 'Legal Balls Bowled / Bowler Wickets',
            'Analytical Note': 'Excludes non-bowler wickets (Run Out, Retire Out, Obstructing the Field).'
        },
        {
            'Metric': 'Dot Ball Percentage',
            'Formula': '(Dot Deliveries / Legal Deliveries) × 100',
            'Analytical Note': 'Calculates dot-ball frequency (deliveries resulting in 0 runs conceded).'
        },
        {
            'Metric': 'Match Phase Segmentation',
            'Formula': 'Powerplay: Overs 1–6 | Middle: Overs 7–15 | Death: Overs 16–20',
            'Analytical Note': 'Derived directly from overid in ball_by_ball data.'
        },
        {
            'Metric': 'Experimental Pressure Proxy',
            'Formula': 'Weighted composite of phase scoring/conceding rate and boundary control',
            'Analytical Note': 'Described strictly as an empirical proxy, not an absolute temperament measure.'
        }
    ]
