"""
player_comparison.py
Head-to-head comparison logic for 2 or more players:
- Batting side-by-side
- Bowling side-by-side
- Phase comparison
- Radar chart data preparation
- Automated strengths & limitations generation
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import List, Dict, Any

def get_player_full_profile(player_name: str, df_bat: pd.DataFrame, df_bowl: pd.DataFrame, df_roster: pd.DataFrame) -> Dict[str, Any]:
    """Extracts batting, bowling, and role stats for a specific player."""
    profile = {'player_name': player_name}

    if not df_bat.empty:
        b = df_bat[df_bat['striker_name'].str.lower() == player_name.lower()]
        if not b.empty:
            row = b.iloc[0]
            profile['batting'] = {
                'runs': int(row.get('runs', 0)),
                'balls': int(row.get('balls', 0)),
                'strike_rate': float(row.get('strike_rate', 0.0)),
                'batting_average': float(row['batting_average']) if pd.notna(row.get('batting_average')) else None,
                'fours': int(row.get('fours', 0)),
                'sixes': int(row.get('sixes', 0)),
                'boundary_pct': float(row.get('boundary_pct', 0.0)),
                'dot_ball_pct': float(row.get('dot_ball_pct', 0.0)),
                'matches': int(row.get('matches', 0)),
                'innings': int(row.get('innings', 0))
            }
        else:
            profile['batting'] = None
    else:
        profile['batting'] = None

    if not df_bowl.empty:
        w = df_bowl[df_bowl['bowler_name'].str.lower() == player_name.lower()]
        if not w.empty:
            row = w.iloc[0]
            profile['bowling'] = {
                'wickets': int(row.get('wickets', 0)),
                'balls': int(row.get('balls', 0)),
                'overs': float(row.get('overs', 0.0)),
                'conceded': int(row.get('conceded', 0)),
                'economy': float(row['economy']) if pd.notna(row.get('economy')) else None,
                'bowling_average': float(row['bowling_average']) if pd.notna(row.get('bowling_average')) else None,
                'bowling_strike_rate': float(row['bowling_strike_rate']) if pd.notna(row.get('bowling_strike_rate')) else None,
                'dot_ball_pct': float(row.get('dot_ball_pct', 0.0)),
                'matches': int(row.get('matches', 0)),
                'innings': int(row.get('innings', 0)),
                'pace_or_spin': row.get('pace_or_spin', 'Unknown'),
                'bowling_type': row.get('bowling_type', 'Unknown')
            }
        else:
            profile['bowling'] = None
    else:
        profile['bowling'] = None

    if not df_roster.empty:
        r = df_roster[df_roster['player_name'].str.lower() == player_name.lower()]
        profile['role'] = r.iloc[0]['derived_role'] if not r.empty else "Unknown"
    else:
        profile['role'] = "Unknown"

    return profile

def generate_player_radar_chart(players_profiles: List[Dict[str, Any]]) -> go.Figure:
    """Creates a multi-axis comparison radar chart for selected players."""
    categories = ['Batting Output', 'Strike Rate', 'Boundary Power', 'Bowling Output', 'Economy Control', 'Dot Efficiency']

    fig = go.Figure()

    palette = ['#e83e82', '#55d6e8', '#f4c76b', '#c084fc', '#34d399']

    for idx, p in enumerate(players_profiles):
        name = p['player_name']
        b = p.get('batting') or {}
        w = p.get('bowling') or {}

        # 0-100 normalized score estimations for the radar
        runs = b.get('runs', 0)
        sr = b.get('strike_rate', 0.0)
        bnd = b.get('boundary_pct', 0.0)
        wickets = w.get('wickets', 0)
        econ = w.get('economy', 10.0) or 10.0
        dots = w.get('dot_ball_pct', 0.0)

        val_runs = min(100.0, (runs / 1000.0) * 100)
        val_sr = min(100.0, max(0.0, ((sr - 100.0) / 100.0) * 100))
        val_bnd = min(100.0, (bnd / 75.0) * 100)
        val_wkts = min(100.0, (wickets / 50.0) * 100)
        val_econ = min(100.0, max(0.0, ((12.0 - econ) / 6.0) * 100))
        val_dots = min(100.0, (dots / 60.0) * 100)

        values = [val_runs, val_sr, val_bnd, val_wkts, val_econ, val_dots]
        values.append(values[0]) # close radar loop

        color = palette[idx % len(palette)]
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=name,
            line=dict(color=color, width=2),
            opacity=0.65
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color='rgba(255,255,255,0.4)', gridcolor='rgba(255,255,255,0.1)'),
            angularaxis=dict(color='#dce4f2', gridcolor='rgba(255,255,255,0.15)')
        ),
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#dce4f2', family='DM Sans'),
        height=450,
        margin=dict(l=40, r=40, t=30, b=30)
    )
    return fig

def summarize_strengths_limitations(p_profile: Dict[str, Any]) -> Dict[str, List[str]]:
    """Synthesizes factual strengths and limitations directly from actual observed metrics."""
    strengths = []
    limitations = []

    b = p_profile.get('batting')
    w = p_profile.get('bowling')

    if b:
        if b['runs'] >= 500:
            strengths.append(f"Proven volume run scorer ({b['runs']:,} runs in {b['matches']} matches)")
        if b['strike_rate'] >= 140.0:
            strengths.append(f"High-impact scoring rate (SR {b['strike_rate']:.1f})")
        if b['boundary_pct'] >= 60.0:
            strengths.append(f"Strong boundary dependency ({b['boundary_pct']:.1f}% runs from boundaries)")
        if b['batting_average'] and b['batting_average'] >= 32.0:
            strengths.append(f"High batting consistency (Avg {b['batting_average']:.1f})")

        if b['strike_rate'] < 120.0 and b['balls'] >= 40:
            limitations.append(f"Sub-par scoring acceleration (SR {b['strike_rate']:.1f})")
        if b['dot_ball_pct'] >= 45.0:
            limitations.append(f"High dot ball accumulation ({b['dot_ball_pct']:.1f}%)")
        if b['balls'] < 50:
            limitations.append(f"Limited batting sample size ({b['balls']} balls faced)")
    else:
        limitations.append("No recorded batting deliveries in selected sample")

    if w:
        if w['wickets'] >= 20:
            strengths.append(f"High-volume wicket taker ({w['wickets']} wkts)")
        if w['economy'] and w['economy'] <= 7.8:
            strengths.append(f"Exceptional run prevention (Econ {w['economy']:.2f})")
        if w['dot_ball_pct'] >= 40.0:
            strengths.append(f"High dot ball creation rate ({w['dot_ball_pct']:.1f}%)")

        if w['economy'] and w['economy'] >= 9.5 and w['balls'] >= 60:
            limitations.append(f"Expensive run concession (Econ {w['economy']:.2f})")
        if w['balls'] < 60:
            limitations.append(f"Limited bowling sample size ({w['balls']} legal balls)")
    else:
        limitations.append("No recorded bowling deliveries in selected sample")

    return {'strengths': strengths, 'limitations': limitations}
