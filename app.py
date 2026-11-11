"""
SupeRR Selector — Season 2
Ultimate Premium Dashboard Upgrade
Rajasthan Royals Scouting & Auction Analytics Platform
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Setup Page Configuration
st.set_page_config(
    page_title="SupeRR Selector Season 2 | RR Cricket Intelligence",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import internal modular analytics
from modules.ui_theme import apply_custom_theme, render_hero_banner, render_kpi
from modules.data_loader import get_complete_data
from modules.batting import calculate_batting_aggregates, compute_batting_score, get_season_batting_trends
from modules.bowling import calculate_bowling_aggregates, compute_bowling_score, get_season_bowling_trends
from modules.pressure_lab import calculate_phase_batting, calculate_phase_bowling, calculate_pressure_batting_proxy, calculate_pressure_bowling_proxy
from modules.scouting import derive_player_roles, compute_scouting_score
from modules.player_comparison import get_player_full_profile, generate_player_radar_chart, summarize_strengths_limitations
from modules.auction import create_initial_auction_plan, analyze_shortlist_composition, generate_auction_report_df
from modules.methodology import audit_datasets, get_formula_definitions

# Apply RR Theme styling
apply_custom_theme()

# Load Data with Streamlit Caching
@st.cache_data(show_spinner="Loading cricket datasets and building relational indices...")
def load_all_data():
    return get_complete_data()

try:
    bb, matches, comps, mapping, teams, p11 = load_all_data()
except Exception as e:
    st.error(f"Error loading datasets: {e}")
    st.stop()

# Initialize Session State
if 'shortlist' not in st.session_state:
    st.session_state.shortlist = []
if 'auction_plan' not in st.session_state:
    st.session_state.auction_plan = create_initial_auction_plan()

# ----------------- SIDEBAR BRANDING & NAVIGATION -----------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 16px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 16px;">
        <div style="font-size: 10px; font-weight: 800; letter-spacing: 0.18em; color: #FF78AD; text-transform: uppercase;">Rajasthan Royals Analytics</div>
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 800; color: #FFFFFF; line-height: 1.1; margin-top: 4px;">
            SupeRR <span style="color:#E83E82">Selector</span>
        </div>
        <div style="font-size: 11px; color: #94A3B8; margin-top: 4px;">Season 2 · Cricket Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    # 9 Application Sections
    SECTIONS = [
        "1. Executive Overview",
        "2. Batting Intelligence",
        "3. Bowling Intelligence",
        "4. Pressure Lab",
        "5. Player Explorer",
        "6. RR Scouting Room",
        "7. Player Comparison",
        "8. Auction Intelligence",
        "9. Data Quality & Methodology"
    ]
    current_section = st.radio("Navigation", SECTIONS, label_visibility="collapsed")

    st.markdown("<hr style='margin:16px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:11px; font-weight:700; letter-spacing:0.12em; color:#94A3B8; text-transform:uppercase; margin-bottom:10px;'>Global Dataset Filters</div>", unsafe_allow_html=True)

    # Filter: Match Format
    all_formats = sorted(bb['match_format'].dropna().unique().tolist())
    selected_formats = st.multiselect("Format", all_formats, default=all_formats)

    # Filter: Season
    all_seasons = sorted(bb['season'].dropna().astype(str).unique().tolist())
    selected_seasons = st.multiselect("Season", all_seasons, default=all_seasons)

    # Filter: Competition
    all_comps = sorted(bb['comp_name'].dropna().unique().tolist())
    ipl_defaults = [c for c in all_comps if 'IPL' in c]
    selected_comps = st.multiselect("Competition", all_comps, default=ipl_defaults if ipl_defaults else all_comps[:5])

    # Filter: Team
    all_teams = sorted(list(set(bb['batting_team_name'].dropna().unique().tolist()) | set(bb['bowling_team_name'].dropna().unique().tolist())))
    if 'Unknown' in all_teams:
        all_teams.remove('Unknown')
    selected_teams = st.multiselect("Teams (Optional)", all_teams, default=[])

    # Reset Filters Button
    if st.button("↺ Reset Filters", use_container_width=True):
        st.rerun()

    # Shortlist quick widget in sidebar
    st.markdown("<hr style='margin:16px 0;'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background: rgba(232, 62, 130, 0.08); border: 1px solid rgba(232, 62, 130, 0.25); border-radius: 12px; padding: 12px 14px;">
        <div style="font-size: 10px; font-weight: 700; text-transform: uppercase; color: #FF78AD; letter-spacing: 0.12em;">RR Shortlist Tracker</div>
        <div style="font-size: 20px; font-weight: 700; color: #FFFFFF; font-family: 'Space Grotesk';">{len(st.session_state.shortlist)} Players</div>
        <div style="font-size: 11px; color: #94A3B8; margin-top: 2px;">Ready for Auction War Room</div>
    </div>
    """, unsafe_allow_html=True)

# ----------------- APPLY GLOBAL FILTERS -----------------
f_bb = bb.copy()
if selected_formats:
    f_bb = f_bb[f_bb['match_format'].isin(selected_formats)]
if selected_seasons:
    f_bb = f_bb[f_bb['season'].astype(str).isin(selected_seasons)]
if selected_comps:
    f_bb = f_bb[f_bb['comp_name'].isin(selected_comps)]
if selected_teams:
    f_bb = f_bb[f_bb['batting_team_name'].isin(selected_teams) | f_bb['bowling_team_name'].isin(selected_teams)]

# Precalculate filtered aggregates
bat_agg = calculate_batting_aggregates(f_bb)
bowl_agg = calculate_bowling_aggregates(f_bb)
roster_df = derive_player_roles(f_bb, bat_agg, bowl_agg)

# -------------------------------------------------------------
# 1. EXECUTIVE OVERVIEW
# -------------------------------------------------------------
if current_section == "1. Executive Overview":
    render_hero_banner(
        title="SupeRR Selector <span style='color:#E83E82'>/</span> Executive Overview",
        subtitle="High-level telemetry and verified aggregate dataset performance. Decode multi-season cricket output, team profiles, and delivery volume across premier T20 tournaments.",
        badge1="EXECUTIVE SUITE",
        badge2=f"{f_bb['match_id'].nunique()} MATCHES ANALYZED"
    )

    # Top-Level Verified KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi("Total Deliveries", f"{len(f_bb):,}", f"Out of {len(bb):,} recorded")
    with k2:
        render_kpi("Matches Covered", f"{f_bb['match_id'].nunique():,}", f"Across {f_bb['comp_id'].nunique()} competitions")
    with k3:
        unique_batters = f_bb['striker_id'].nunique()
        render_kpi("Unique Batters", f"{unique_batters:,}", "Active in filtered window")
    with k4:
        unique_bowlers = f_bb['bowler_id'].nunique()
        render_kpi("Unique Bowlers", f"{unique_bowlers:,}", "Active in filtered window")

    k5, k6, k7, k8 = st.columns(4)
    with k5:
        total_runs = int(f_bb['runs'].sum() + f_bb['is_wide'].sum() + f_bb['is_noball'].sum() + pd.to_numeric(f_bb['extras_2_runs'], errors='coerce').fillna(0).sum())
        render_kpi("Total Match Runs", f"{total_runs:,}", "Includes extras")
    with k6:
        total_wickets = int(f_bb['is_bowler_wicket'].sum())
        render_kpi("Bowler Wickets", f"{total_wickets:,}", "Excludes run-outs")
    with k7:
        total_fours = int(f_bb['is_four'].sum())
        render_kpi("Total 4s Hit", f"{total_fours:,}", f"{(total_fours*4):,} runs")
    with k8:
        total_sixes = int(f_bb['is_six'].sum())
        render_kpi("Total 6s Hit", f"{total_sixes:,}", f"{(total_sixes*6):,} runs")

    st.markdown("<br>", unsafe_allow_html=True)

    # Visual Trends & Charts
    c_left, c_right = st.columns([1.3, 1])

    with c_left:
        st.markdown("<div class='rr-panel'><div class='rr-panel-header'>🏆 Competition Match Volume & Coverage</div>", unsafe_allow_html=True)
        comp_counts = f_bb.groupby('comp_name')['match_id'].nunique().sort_values(ascending=True).tail(10).reset_index()
        comp_counts.columns = ['Competition', 'Matches']
        fig_comp = px.bar(
            comp_counts,
            x='Matches',
            y='Competition',
            orientation='h',
            text='Matches',
            color='Matches',
            color_continuous_scale=['#4C1D95', '#E83E82', '#55D6E8']
        )
        fig_comp.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#dce4f2', family='Plus Jakarta Sans'),
            height=380,
            margin=dict(l=10, r=20, t=10, b=10),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_comp, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c_right:
        st.markdown("<div class='rr-panel'><div class='rr-panel-header'>⚡ Match Format & Deliveries Breakdown</div>", unsafe_allow_html=True)
        fmt_counts = f_bb['match_format'].fillna('Unknown').value_counts().reset_index()
        fmt_counts.columns = ['Format', 'Balls']
        fig_fmt = px.pie(
            fmt_counts,
            names='Format',
            values='Balls',
            hole=0.65,
            color_discrete_sequence=['#E83E82', '#55D6E8', '#F4C76B', '#A855F7']
        )
        fig_fmt.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#dce4f2', family='Plus Jakarta Sans'),
            height=380,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation='h', yanchor='bottom', y=-0.1, xanchor='center', x=0.5)
        )
        fig_fmt.add_annotation(
            text=f"<b>{len(f_bb):,}</b><br><span style='font-size:11px;color:#94a3b8;'>Deliveries</span>",
            x=0.5, y=0.5, showarrow=False, font=dict(size=18, color='#FFFFFF')
        )
        st.plotly_chart(fig_fmt, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Season Wise Trends
    st.markdown("<div class='rr-panel'><div class='rr-panel-header'>📈 Season-by-Season Trajectory (Runs & Wickets)</div>", unsafe_allow_html=True)
    season_trends = f_bb.groupby('season').agg(
        runs=('runs', 'sum'),
        wickets=('is_bowler_wicket', 'sum'),
        matches=('match_id', 'nunique')
    ).reset_index()
    fig_st = px.line(
        season_trends,
        x='season',
        y=['runs', 'wickets'],
        markers=True,
        color_discrete_sequence=['#E83E82', '#55D6E8'],
        labels={'value': 'Count', 'variable': 'Metric', 'season': 'Season'}
    )
    fig_st.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#dce4f2', family='Plus Jakarta Sans'),
        height=320,
        margin=dict(l=10, r=20, t=20, b=10),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    )
    st.plotly_chart(fig_st, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Quick Leaderboards
    lead1, lead2 = st.columns(2)
    with lead1:
        st.markdown("### 🏏 Top Run Scorers")
        top_b = bat_agg.head(8)[['striker_name', 'runs', 'balls', 'strike_rate', 'batting_average', 'matches']]
        st.dataframe(top_b.rename(columns={
            'striker_name': 'Player', 'runs': 'Runs', 'balls': 'Balls Faced',
            'strike_rate': 'Strike Rate', 'batting_average': 'Average', 'matches': 'Matches'
        }), hide_index=True, use_container_width=True)
    with lead2:
        st.markdown("### ⚡ Top Wicket Takers")
        top_w = bowl_agg.head(8)[['bowler_name', 'wickets', 'balls', 'economy', 'bowling_average', 'matches']]
        st.dataframe(top_w.rename(columns={
            'bowler_name': 'Player', 'wickets': 'Wickets', 'balls': 'Balls Bowled',
            'economy': 'Economy', 'bowling_average': 'Average', 'matches': 'Matches'
        }), hide_index=True, use_container_width=True)

# -------------------------------------------------------------
# 2. BATTING INTELLIGENCE
# -------------------------------------------------------------
elif current_section == "2. Batting Intelligence":
    render_hero_banner(
        title="Batting Intelligence <span style='color:#E83E82'>/</span> Performance Room",
        subtitle="Deep evaluation of batting output, scoring efficiency, acceleration profiles, boundary dependency, and transparent multi-factor scoring.",
        badge1="BATTING LAB",
        badge2="EVIDENCE-BASED METRICS"
    )

    if bat_agg.empty:
        st.warning("No batting records found matching the active filters.")
    else:
        # Configuration Controls
        with st.expander("⚙️ Customizable Batting Performance Model & Minimum Filters", expanded=False):
            fc1, fc2, fc3, fc4, fc5 = st.columns(5)
            with fc1:
                w_runs = st.slider("Weight: Runs Scored", 0.0, 1.0, 0.25, 0.05)
            with fc2:
                w_sr = st.slider("Weight: Strike Rate", 0.0, 1.0, 0.30, 0.05)
            with fc3:
                w_avg = st.slider("Weight: Average", 0.0, 1.0, 0.25, 0.05)
            with fc4:
                w_bnd = st.slider("Weight: Boundary %", 0.0, 1.0, 0.10, 0.05)
            with fc5:
                w_cons = st.slider("Weight: Consistency", 0.0, 1.0, 0.10, 0.05)

            min_balls_faced = st.slider("Minimum Balls Faced Threshold", 10, 500, 50, 10)

        # Compute batting score
        scored_bat = compute_batting_score(
            bat_agg,
            w_runs=w_runs,
            w_sr=w_sr,
            w_avg=w_avg,
            w_boundary=w_bnd,
            w_consistency=w_cons,
            min_balls=min_balls_faced
        )

        # Scatter Plot: Runs vs Strike Rate
        st.markdown("<div class='rr-panel'><div class='rr-panel-header'>🎯 Strike Rate vs Batting Average Scatter Matrix</div>", unsafe_allow_html=True)
        view_bat = scored_bat[scored_bat['balls'] >= min_balls_faced].copy()
        fig_scatter = px.scatter(
            view_bat,
            x='strike_rate',
            y='batting_average',
            size='runs',
            color='batting_score',
            hover_name='striker_name',
            hover_data=['runs', 'balls', 'fours', 'sixes', 'boundary_pct'],
            color_continuous_scale=['#4C1D95', '#E83E82', '#55D6E8', '#F4C76B'],
            labels={'strike_rate': 'Strike Rate (Runs/100 Balls)', 'batting_average': 'Batting Average', 'batting_score': 'Bat Score (0-100)'}
        )
        fig_scatter.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#dce4f2', family='Plus Jakarta Sans'),
            height=460,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)')
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Leaderboard Table & Export
        st.markdown(f"### 📋 Batting Leaderboard ({len(view_bat)} Qualifiers)")
        display_bat = view_bat[['striker_name', 'runs', 'balls', 'strike_rate', 'batting_average', 'fours', 'sixes', 'boundary_pct', 'dot_ball_pct', 'batting_score', 'matches']]
        display_bat = display_bat.rename(columns={
            'striker_name': 'Player', 'runs': 'Runs', 'balls': 'Balls Faced',
            'strike_rate': 'SR', 'batting_average': 'Avg', 'fours': '4s',
            'sixes': '6s', 'boundary_pct': 'Bnd %', 'dot_ball_pct': 'Dot %',
            'batting_score': 'Score', 'matches': 'Matches'
        })
        st.dataframe(display_bat, hide_index=True, use_container_width=True, height=400)

        # CSV Export
        csv_bat = display_bat.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Batting Leaderboard (CSV)",
            data=csv_bat,
            file_name="SupeRR_Batting_Leaderboard.csv",
            mime="text/csv"
        )

# -------------------------------------------------------------
# 3. BOWLING INTELLIGENCE
# -------------------------------------------------------------
elif current_section == "3. Bowling Intelligence":
    render_hero_banner(
        title="Bowling Intelligence <span style='color:#55D6E8'>/</span> Arsenal Analytics",
        subtitle="Comprehensive bowling metrics: legal deliveries, overs bowled, accurately reconciled bowler conceded runs, economy rates, and customizable bowling scores.",
        badge1="BOWLING ARSENAL",
        badge2="LEGAL BALLS & CONCEDED RUNS"
    )

    if bowl_agg.empty:
        st.warning("No bowling records found matching the active filters.")
    else:
        with st.expander("⚙️ Customizable Bowling Performance Model & Minimum Filters", expanded=False):
            bc1, bc2, bc3, bc4, bc5 = st.columns(5)
            with bc1:
                w_wkts = st.slider("Weight: Wickets", 0.0, 1.0, 0.30, 0.05)
            with bc2:
                w_econ = st.slider("Weight: Economy", 0.0, 1.0, 0.25, 0.05)
            with bc3:
                w_bavg = st.slider("Weight: Average", 0.0, 1.0, 0.20, 0.05)
            with bc4:
                w_bsr = st.slider("Weight: Strike Rate", 0.0, 1.0, 0.15, 0.05)
            with bc5:
                w_dots = st.slider("Weight: Dot Ball %", 0.0, 1.0, 0.10, 0.05)

            min_balls_bowled = st.slider("Minimum Legal Deliveries Bowled", 12, 300, 48, 6)

        scored_bowl = compute_bowling_score(
            bowl_agg,
            w_wickets=w_wkts,
            w_econ=w_econ,
            w_avg=w_bavg,
            w_sr=w_bsr,
            w_dots=w_dots,
            min_balls=min_balls_bowled
        )

        view_bowl = scored_bowl[scored_bowl['balls'] >= min_balls_bowled].copy()

        # Scatter Plot: Economy vs Wickets
        st.markdown("<div class='rr-panel'><div class='rr-panel-header'>🎯 Economy Rate vs Wickets Taken</div>", unsafe_allow_html=True)
        fig_b_scatter = px.scatter(
            view_bowl,
            x='economy',
            y='wickets',
            size='balls',
            color='bowling_score',
            hover_name='bowler_name',
            hover_data=['conceded', 'overs', 'dot_ball_pct', 'pace_or_spin'],
            color_continuous_scale=['#4C1D95', '#55D6E8', '#F4C76B'],
            labels={'economy': 'Economy Rate (Runs/Over)', 'wickets': 'Wickets', 'bowling_score': 'Bowl Score (0-100)'}
        )
        fig_b_scatter.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#dce4f2', family='Plus Jakarta Sans'),
            height=460,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)')
        )
        st.plotly_chart(fig_b_scatter, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Leaderboard Table & Export
        st.markdown(f"### 📋 Bowling Leaderboard ({len(view_bowl)} Qualifiers)")
        display_bowl = view_bowl[['bowler_name', 'pace_or_spin', 'wickets', 'overs', 'balls', 'conceded', 'economy', 'bowling_average', 'bowling_strike_rate', 'dot_ball_pct', 'bowling_score', 'matches']]
        display_bowl = display_bowl.rename(columns={
            'bowler_name': 'Player', 'pace_or_spin': 'Type', 'wickets': 'Wkts',
            'overs': 'Overs', 'balls': 'Legal Balls', 'conceded': 'Runs Conceded',
            'economy': 'Econ', 'bowling_average': 'Avg', 'bowling_strike_rate': 'SR',
            'dot_ball_pct': 'Dot %', 'bowling_score': 'Score', 'matches': 'Matches'
        })
        st.dataframe(display_bowl, hide_index=True, use_container_width=True, height=400)

        csv_bowl = display_bowl.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Bowling Leaderboard (CSV)",
            data=csv_bowl,
            file_name="SupeRR_Bowling_Leaderboard.csv",
            mime="text/csv"
        )

# -------------------------------------------------------------
# 4. PRESSURE LAB
# -------------------------------------------------------------
elif current_section == "4. Pressure Lab":
    render_hero_banner(
        title="PRESSURE LAB <span style='color:#FF78AD'>/</span> Phase & High-Leverage Analysis",
        subtitle="Empirical performance across match phases: Powerplay (overs 1-6), Middle (7-15), and Death (16-20). Transparent statistical proxies for clutch decision-making.",
        badge1="EXPERIMENTAL PROXIES",
        badge2="MATCH PHASE INTELLIGENCE"
    )

    st.info("ℹ️ **Methodology Notice:** Pressure-performance indicators are empirical statistical proxies derived from delivery situational context (phase, scoring requirements, dot ball pressure). They represent observed output and should not be treated as deterministic measures of psychological temperament.")

    phase_choice = st.selectbox("Select Match Phase Focus", ["Death (Overs 16-20)", "Powerplay (Overs 1-6)", "Middle (Overs 7-15)"])
    phase_clean = phase_choice.split()[0]

    min_phase_balls = st.slider("Minimum Deliveries in Phase", 12, 180, 30, 6)

    p_col1, p_col2 = st.columns(2)

    with p_col1:
        st.markdown(f"### 🏏 {phase_clean} Phase Batting Output")
        p_bat = calculate_phase_batting(f_bb, phase_clean)
        if not p_bat.empty:
            p_bat_view = p_bat[p_bat['balls'] >= min_phase_balls].head(15)[['striker_name', 'runs', 'balls', 'strike_rate', 'boundary_pct', 'dot_ball_pct', 'matches']]
            st.dataframe(p_bat_view.rename(columns={
                'striker_name': 'Batter', 'runs': 'Runs', 'balls': 'Balls Faced',
                'strike_rate': 'Phase SR', 'boundary_pct': 'Bnd %', 'dot_ball_pct': 'Dot %', 'matches': 'Matches'
            }), hide_index=True, use_container_width=True)
        else:
            st.write("No batting records available.")

    with p_col2:
        st.markdown(f"### ⚡ {phase_clean} Phase Bowling Output")
        p_bowl = calculate_phase_bowling(f_bb, phase_clean)
        if not p_bowl.empty:
            p_bowl_view = p_bowl[p_bowl['balls'] >= min_phase_balls].head(15)[['bowler_name', 'pace_or_spin', 'wickets', 'overs', 'economy', 'dot_ball_pct', 'matches']]
            st.dataframe(p_bowl_view.rename(columns={
                'bowler_name': 'Bowler', 'pace_or_spin': 'Style', 'wickets': 'Wkts',
                'overs': 'Overs', 'economy': 'Phase Econ', 'dot_ball_pct': 'Dot %', 'matches': 'Matches'
            }), hide_index=True, use_container_width=True)
        else:
            st.write("No bowling records available.")

    # Death Over Proxies
    st.markdown("---")
    st.markdown("### 🎯 Death Overs Pressure Proxy Rankings (Overs 16–20)")
    dp1, dp2 = st.columns(2)
    with dp1:
        st.caption("Death Batting Impact Proxy (Balances SR, boundary conversion & low dot rate)")
        d_bat_proxy = calculate_pressure_batting_proxy(f_bb, min_balls=min_phase_balls)
        if not d_bat_proxy.empty:
            st.dataframe(d_bat_proxy.head(10)[['striker_name', 'runs', 'balls', 'strike_rate', 'death_impact_proxy']].rename(columns={
                'striker_name': 'Batter', 'runs': 'Runs', 'balls': 'Balls', 'strike_rate': 'SR', 'death_impact_proxy': 'Impact Proxy'
            }), hide_index=True, use_container_width=True)
    with dp2:
        st.caption("Death Bowling Control Proxy (Balances economy suppression & wicket impact)")
        d_bowl_proxy = calculate_pressure_bowling_proxy(f_bb, min_balls=min_phase_balls)
        if not d_bowl_proxy.empty:
            st.dataframe(d_bowl_proxy.head(10)[['bowler_name', 'wickets', 'overs', 'economy', 'death_control_proxy']].rename(columns={
                'bowler_name': 'Bowler', 'wickets': 'Wkts', 'overs': 'Overs', 'economy': 'Econ', 'death_control_proxy': 'Control Proxy'
            }), hide_index=True, use_container_width=True)

# -------------------------------------------------------------
# 5. PLAYER EXPLORER
# -------------------------------------------------------------
elif current_section == "5. Player Explorer":
    render_hero_banner(
        title="Player Explorer <span style='color:#E83E82'>/</span> Individual Dossier",
        subtitle="Comprehensive 360-degree player inspection: career splits, pace vs spin matchups, phase breakdown, and tournament appearances.",
        badge1="SCOUTING PROFILE",
        badge2="INDIVIDUAL INTELLIGENCE"
    )

    all_names = sorted(list(set(bat_agg['striker_name'].dropna()) | set(bowl_agg['bowler_name'].dropna())))
    if not all_names:
        st.warning("No players found matching current filters.")
    else:
        selected_player = st.selectbox("Search & Select Player Dossier", all_names, index=0)

        # Player Profile Header
        profile = get_player_full_profile(selected_player, bat_agg, bowl_agg, roster_df)
        b_info = profile.get('batting')
        w_info = profile.get('bowling')

        st.markdown(f"""
        <div class='rr-panel'>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span class="rr-badge-pink">{profile['role']}</span>
                    <h2 style="margin: 8px 0 2px 0;">{selected_player}</h2>
                    <div style="font-size:12.5px; color:#94A3B8;">Detailed tournament output in active filtered selection</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Metrics row
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        with m1:
            render_kpi("Runs", f"{b_info['runs']:,}" if b_info else "—", "Batting output")
        with m2:
            render_kpi("Strike Rate", f"{b_info['strike_rate']:.1f}" if b_info else "—", "Runs / 100 balls")
        with m3:
            avg_str = f"{b_info['batting_average']:.1f}" if (b_info and b_info['batting_average']) else "—"
            render_kpi("Batting Avg", avg_str, "Consistency")
        with m4:
            render_kpi("Wickets", f"{w_info['wickets']:,}" if w_info else "—", "Bowling output")
        with m5:
            econ_str = f"{w_info['economy']:.2f}" if (w_info and w_info['economy']) else "—"
            render_kpi("Economy", econ_str, "Runs / Over")
        with m6:
            render_kpi("Matches", f"{b_info['matches'] if b_info else (w_info['matches'] if w_info else 0)}", "Appearances")

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabs for Splits & Trends
        t_season, t_phase, t_history = st.tabs(["📅 Season Trends", "⚡ Phase Breakdown", "🏆 Competitions & Teams"])

        with t_season:
            s1, s2 = st.columns(2)
            with s1:
                st.markdown("#### Batting by Season")
                b_trends = get_season_batting_trends(f_bb, selected_player)
                if not b_trends.empty:
                    st.dataframe(b_trends, hide_index=True, use_container_width=True)
                else:
                    st.caption("No seasonal batting records.")
            with s2:
                st.markdown("#### Bowling by Season")
                w_trends = get_season_bowling_trends(f_bb, selected_player)
                if not w_trends.empty:
                    st.dataframe(w_trends, hide_index=True, use_container_width=True)
                else:
                    st.caption("No seasonal bowling records.")

        with t_phase:
            st.markdown("#### Output Across Match Phases")
            phase_records = []
            for p in ['Powerplay', 'Middle', 'Death']:
                p_sub = f_bb[f_bb['phase'] == p]
                p_b = calculate_phase_batting(p_sub, p)
                p_w = calculate_phase_bowling(p_sub, p)
                b_row = p_b[p_b['striker_name'].str.lower() == selected_player.lower()] if not p_b.empty else pd.DataFrame()
                w_row = p_w[p_w['bowler_name'].str.lower() == selected_player.lower()] if not p_w.empty else pd.DataFrame()

                phase_records.append({
                    'Phase': p,
                    'Runs': int(b_row['runs'].iloc[0]) if not b_row.empty else 0,
                    'Balls Faced': int(b_row['balls'].iloc[0]) if not b_row.empty else 0,
                    'Strike Rate': float(b_row['strike_rate'].iloc[0]) if not b_row.empty else 0.0,
                    'Wickets': int(w_row['wickets'].iloc[0]) if not w_row.empty else 0,
                    'Overs': float(w_row['overs'].iloc[0]) if not w_row.empty else 0.0,
                    'Economy': float(w_row['economy'].iloc[0]) if (not w_row.empty and pd.notna(w_row['economy'].iloc[0])) else None,
                })
            st.dataframe(pd.DataFrame(phase_records), hide_index=True, use_container_width=True)

        with t_history:
            st.markdown("#### Tournament and Squad Registrations")
            mapped_rows = mapping[mapping['player_name'].str.lower() == selected_player.lower()]
            if not mapped_rows.empty:
                st.dataframe(mapped_rows[['comp_name', 'team_name']].drop_duplicates(), hide_index=True, use_container_width=True)
            else:
                st.caption("No mapping records found.")

# -------------------------------------------------------------
# 6. RR SCOUTING ROOM
# -------------------------------------------------------------
elif current_section == "6. RR Scouting Room":
    render_hero_banner(
        title="RR SCOUTING ROOM <span style='color:#E83E82'>/</span> Talent Evaluation Hub",
        subtitle="The central decision engine for Rajasthan Royals. Role-classified talent discovery, customizable multi-metric scoring, and interactive shortlist builder.",
        badge1="RAJASTHAN ROYALS SQUAD BUILDER",
        badge2="EVIDENCE-BACKED"
    )

    r_col1, r_col2 = st.columns([1.2, 1])

    with r_col1:
        st.markdown("### 🔎 Role-Based Candidate Search")
        role_categories = [
            "All",
            "Top-Order Batter",
            "Middle-Order Batter",
            "Finisher / Lower-Order",
            "All-Rounder (Pace)",
            "All-Rounder (Spin)",
            "Pace Bowler",
            "Spin Bowler"
        ]
        selected_role = st.selectbox("Filter Target Scouting Category", role_categories, index=0)

    with r_col2:
        st.markdown("### ⚙️ Scouting Formula Calibration")
        with st.popover("Tune Scoring Weights"):
            sc_w_bat = st.slider("Batting Weight", 0.0, 1.0, 0.35, 0.05)
            sc_w_bowl = st.slider("Bowling Weight", 0.0, 1.0, 0.35, 0.05)
            sc_w_sr = st.slider("Strike Rate Weight", 0.0, 1.0, 0.15, 0.05)
            sc_w_econ = st.slider("Economy Weight", 0.0, 1.0, 0.15, 0.05)
            sc_min_balls = st.slider("Minimum Workload (Balls)", 12, 200, 30, 6)

    # Compute candidate scores
    scouted_pool = compute_scouting_score(
        roster_df,
        role_filter=selected_role,
        w_bat=sc_w_bat,
        w_bowl=sc_w_bowl,
        w_sr=sc_w_sr,
        w_econ=sc_w_econ,
        min_deliveries=sc_min_balls
    )

    st.markdown(f"#### Identified Candidates ({len(scouted_pool)} Players)")
    if not scouted_pool.empty:
        display_pool = scouted_pool[['player_name', 'derived_role', 'scouting_score', 'runs', 'balls_faced', 'strike_rate', 'batting_average', 'wickets', 'balls_bowled', 'economy']]
        st.dataframe(display_pool.rename(columns={
            'player_name': 'Candidate', 'derived_role': 'Derived Role', 'scouting_score': 'Scout Score',
            'runs': 'Runs', 'balls_faced': 'Balls Faced', 'strike_rate': 'SR', 'batting_average': 'Bat Avg',
            'wickets': 'Wkts', 'balls_bowled': 'Balls Bowled', 'economy': 'Econ'
        }), hide_index=True, use_container_width=True, height=360)

        # Interactive Shortlist Manager
        st.markdown("---")
        st.markdown("### 📌 Manage Rajasthan Royals Shortlist")
        cand_list = scouted_pool['player_name'].tolist()

        s_act1, s_act2, s_act3 = st.columns([2, 1, 1])
        with s_act1:
            player_to_add = st.selectbox("Select Player to Add / Remove", cand_list)
        with s_act2:
            if st.button("➕ Add to Shortlist", use_container_width=True):
                if player_to_add not in st.session_state.shortlist:
                    st.session_state.shortlist.append(player_to_add)
                    st.success(f"Added {player_to_add} to shortlist.")
                else:
                    st.info(f"{player_to_add} is already shortlisted.")
        with s_act3:
            if st.button("🗑️ Remove", use_container_width=True):
                if player_to_add in st.session_state.shortlist:
                    st.session_state.shortlist.remove(player_to_add)
                    st.warning(f"Removed {player_to_add}.")

        # Current Shortlist Table
        if st.session_state.shortlist:
            st.markdown(f"#### Active Shortlist ({len(st.session_state.shortlist)} Candidates)")
            sl_sub = scouted_pool[scouted_pool['player_name'].isin(st.session_state.shortlist)]
            st.dataframe(sl_sub[['player_name', 'derived_role', 'scouting_score', 'runs', 'strike_rate', 'wickets', 'economy']], hide_index=True, use_container_width=True)

            # Export Shortlist
            sl_csv = sl_sub.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export RR Shortlist (CSV)",
                data=sl_csv,
                file_name="RR_Scouting_Shortlist.csv",
                mime="text/csv"
            )
        else:
            st.caption("No players currently shortlisted. Select a player above and click 'Add to Shortlist'.")
    else:
        st.warning("No players matched the selected criteria.")

# -------------------------------------------------------------
# 7. PLAYER COMPARISON
# -------------------------------------------------------------
elif current_section == "7. Player Comparison":
    render_hero_banner(
        title="Player Comparison <span style='color:#55D6E8'>/</span> Head-to-Head Analytics",
        subtitle="Side-by-side metric comparison, multidimensional radar visualizer, and algorithmic synthesis of factual strengths and limitations.",
        badge1="HEAD TO HEAD",
        badge2="RADAR & PROFILES"
    )

    all_names = sorted(list(set(bat_agg['striker_name'].dropna()) | set(bowl_agg['bowler_name'].dropna())))
    default_compare = [all_names[0], all_names[1]] if len(all_names) >= 2 else all_names

    selected_players = st.multiselect("Select 2 to 5 Players to Compare", all_names, default=default_compare[:2])

    if len(selected_players) < 2:
        st.info("Please select at least 2 players to enable side-by-side comparison.")
    else:
        # Collect Profiles
        profiles = [get_player_full_profile(p, bat_agg, bowl_agg, roster_df) for p in selected_players]

        # Radar Chart
        st.markdown("<div class='rr-panel'><div class='rr-panel-header'>🕸️ Multidimensional Skill Radar Chart</div>", unsafe_allow_html=True)
        fig_radar = generate_player_radar_chart(profiles)
        st.plotly_chart(fig_radar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Side-by-Side Comparison Cards
        st.markdown("### 📊 Direct Metrics Comparison")
        comp_cols = st.columns(len(selected_players))

        for idx, col in enumerate(comp_cols):
            with col:
                p_prof = profiles[idx]
                b = p_prof.get('batting') or {}
                w = p_prof.get('bowling') or {}
                st.markdown(f"""
                <div class='rr-panel' style='border-top: 3px solid #E83E82;'>
                    <span class='rr-badge-pink'>{p_prof['role']}</span>
                    <h3 style='margin: 8px 0 14px 0;'>{p_prof['player_name']}</h3>
                    <div style='font-size:12px; margin-bottom: 6px;'><b>Runs:</b> {b.get('runs', 0):,}</div>
                    <div style='font-size:12px; margin-bottom: 6px;'><b>Strike Rate:</b> {b.get('strike_rate', 0.0):.1f}</div>
                    <div style='font-size:12px; margin-bottom: 6px;'><b>Batting Avg:</b> {b.get('batting_average') if b.get('batting_average') else '—'}</div>
                    <div style='font-size:12px; margin-bottom: 6px;'><b>Boundary %:</b> {b.get('boundary_pct', 0.0):.1f}%</div>
                    <hr style='margin: 10px 0;'>
                    <div style='font-size:12px; margin-bottom: 6px;'><b>Wickets:</b> {w.get('wickets', 0)}</div>
                    <div style='font-size:12px; margin-bottom: 6px;'><b>Economy:</b> {w.get('economy') if w.get('economy') else '—'}</div>
                    <div style='font-size:12px; margin-bottom: 6px;'><b>Dot Ball %:</b> {w.get('dot_ball_pct', 0.0):.1f}%</div>
                </div>
                """, unsafe_allow_html=True)

        # Strengths and Limitations Breakdown
        st.markdown("### 🔍 Fact-Based Scouting Insights")
        eval_cols = st.columns(len(selected_players))
        for idx, col in enumerate(eval_cols):
            with col:
                p_prof = profiles[idx]
                evals = summarize_strengths_limitations(p_prof)
                st.markdown(f"**{p_prof['player_name']}**")
                st.markdown("*Key Strengths:*")
                for s in evals['strengths']:
                    st.markdown(f"• <span style='color:#72E2EF;'>{s}</span>", unsafe_allow_html=True)
                st.markdown("*Limitations:*")
                for l in evals['limitations']:
                    st.markdown(f"• <span style='color:#FF8BB9;'>{l}</span>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 8. AUCTION INTELLIGENCE
# -------------------------------------------------------------
elif current_section == "8. Auction Intelligence":
    render_hero_banner(
        title="AUCTION INTELLIGENCE <span style='color:#F4C76B'>/</span> War Room Planner",
        subtitle="IPL 2027 squad composition planning, gap analysis, and shortlist budget modeling. Zero fabricated prices or retention lists — completely configurable user assumptions.",
        badge1="IPL AUCTION STRATEGY",
        badge2="WAR ROOM PLANNER"
    )

    st.markdown("""
    <div class='rr-panel'>
        <div class='rr-panel-header'>💡 War Room Methodology & Integrity Principle</div>
        <p style='font-size: 13.5px; color: #CBD5E1; margin: 0;'>
            To uphold rigorous analytics standards, <b>never fabricate live auction purses, official retention lists, or prices</b>.
            All financial allocations and slot limits in this war room are user-configurable assumptions designed to simulate auction dynamics accurately.
        </p>
    </div>
    """, unsafe_allow_html=True)

    ap1, ap2, ap3 = st.columns(3)
    with ap1:
        total_purse = st.number_input("Total Auction Purse Budget (₹ Crores)", min_value=10.0, max_value=200.0, value=120.0, step=5.0)
    with ap2:
        total_slots = st.number_input("Target Squad Slots", min_value=15, max_value=25, value=25, step=1)
    with ap3:
        overseas_max = st.number_input("Max Overseas Slots", min_value=4, max_value=8, value=8, step=1)

    # Shortlist Review
    st.markdown("### 📋 Active Scouting Shortlist for War Room")
    if not st.session_state.shortlist:
        st.warning("Your shortlist is currently empty. Visit the **RR Scouting Room** to add candidate players.")
    else:
        sl_summary = analyze_shortlist_composition(st.session_state.shortlist, roster_df)

        # Composition KPIs
        c1, c2 = st.columns([1, 2])
        with c1:
            render_kpi("Shortlisted", f"{sl_summary['total_shortlisted']} Players", "In war room queue")
        with c2:
            st.markdown("<div class='rr-panel'><div class='rr-panel-header'>Role Distribution</div>", unsafe_allow_html=True)
            r_df = pd.DataFrame(list(sl_summary['role_counts'].items()), columns=['Role', 'Count'])
            st.dataframe(r_df, hide_index=True, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Full Shortlist Dossier Table
        st.markdown("#### Shortlist Candidate Dossier")
        sl_data = pd.DataFrame(sl_summary['players'])
        if not sl_data.empty:
            st.dataframe(sl_data[['player_name', 'derived_role', 'runs', 'strike_rate', 'wickets', 'economy']], hide_index=True, use_container_width=True)

            # Export Auction Report
            report_csv = sl_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export War Room Scouting Dossier (CSV)",
                data=report_csv,
                file_name="RR_Auction_WarRoom_Dossier.csv",
                mime="text/csv"
            )

# -------------------------------------------------------------
# 9. DATA QUALITY & METHODOLOGY
# -------------------------------------------------------------
elif current_section == "9. Data Quality & Methodology":
    render_hero_banner(
        title="DATA QUALITY & METHODOLOGY <span style='color:#72E2EF'>/</span> Analytical Rigor",
        subtitle="Full transparency into dataset schemas, row counts, missing value audits, relational joins, and cricket mathematical formulas.",
        badge1="AUDIT & INTEGRITY",
        badge2="100% TRANSPARENCY"
    )

    st.markdown("### 🔍 Raw Datasets Audit & Schema Verification")
    audit_results = audit_datasets(bb, matches, comps, mapping, teams)
    st.dataframe(pd.DataFrame(audit_results), hide_index=True, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📐 Mathematical Definitions & Cricket Formulas")
    formulas = get_formula_definitions()
    for f in formulas:
        st.markdown(f"""
        <div class='rr-panel' style='margin-bottom: 12px; padding: 14px 18px;'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span style='font-size: 15px; font-weight: 700; color: #FFFFFF;'>{f['Metric']}</span>
                <span class='rr-badge-cyan'>{f['Formula']}</span>
            </div>
            <div style='font-size: 12px; color: #94A3B8; margin-top: 6px;'><b>Analytical Rule:</b> {f['Analytical Note']}</div>
        </div>
        """, unsafe_allow_html=True)

# ----------------- FOOTER -----------------
st.markdown("<hr style='margin-top: 40px;'>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 12px; padding-bottom: 24px;">
    <b>SupeRR Selector — Season 2</b> · Decode Performance. Discover Potential. Build the Winning Squad.<br>
    Built for evidence-based IPL scouting and auction intelligence. Rajasthan Royals Concept Lab.
</div>
""", unsafe_allow_html=True)
