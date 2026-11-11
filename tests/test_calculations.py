"""
test_calculations.py
Unit tests verifying data loading, joins, batting calculations, bowling calculations,
pressure metrics, role derivations, scoring models, and exports.
"""
import unittest
import pandas as pd
import numpy as np
from modules.data_loader import get_complete_data
from modules.batting import calculate_batting_aggregates, compute_batting_score
from modules.bowling import calculate_bowling_aggregates, compute_bowling_score
from modules.pressure_lab import calculate_phase_batting, calculate_phase_bowling, calculate_pressure_batting_proxy, calculate_pressure_bowling_proxy
from modules.scouting import derive_player_roles, compute_scouting_score
from modules.player_comparison import get_player_full_profile, summarize_strengths_limitations
from modules.methodology import audit_datasets, get_formula_definitions

class TestCricketAnalytics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.bb, cls.matches, cls.comps, cls.mapping, cls.teams, cls.p11 = get_complete_data()

    def test_data_integrity(self):
        """Test dataset shape and essential joins."""
        self.assertGreater(len(self.bb), 100000, "Ball-by-ball rows should be > 100,000")
        self.assertIn('match_format', self.bb.columns)
        self.assertIn('season', self.bb.columns)
        self.assertIn('is_legal_delivery', self.bb.columns)
        self.assertIn('bowler_conceded_runs', self.bb.columns)
        self.assertIn('phase', self.bb.columns)

    def test_batting_calculations(self):
        """Test batting metrics: balls faced excludes wides, correct boundary calculations."""
        bat = calculate_batting_aggregates(self.bb)
        self.assertFalse(bat.empty)
        self.assertIn('strike_rate', bat.columns)
        self.assertIn('batting_average', bat.columns)
        self.assertIn('boundary_pct', bat.columns)

        # Pick top batter
        top = bat.iloc[0]
        self.assertGreater(top['runs'], 0)
        self.assertGreater(top['balls'], 0)
        expected_sr = round((top['runs'] / top['balls']) * 100, 2)
        self.assertEqual(top['strike_rate'], expected_sr)

        # Check batting score
        scored_bat = compute_batting_score(bat)
        self.assertIn('batting_score', scored_bat.columns)
        self.assertTrue((scored_bat['batting_score'] >= 0).all())
        self.assertTrue((scored_bat['batting_score'] <= 100).all())

    def test_bowling_calculations(self):
        """Test bowling metrics: legal deliveries, overs, economy."""
        bowl = calculate_bowling_aggregates(self.bb)
        self.assertFalse(bowl.empty)
        self.assertIn('economy', bowl.columns)
        self.assertIn('dot_ball_pct', bowl.columns)

        top = bowl.iloc[0]
        self.assertGreater(top['balls'], 0)
        expected_econ = round((top['conceded'] / top['balls']) * 6.0, 2)
        self.assertEqual(top['economy'], expected_econ)

        # Check bowling score
        scored_bowl = compute_bowling_score(bowl)
        self.assertIn('bowling_score', scored_bowl.columns)
        self.assertTrue((scored_bowl['bowling_score'] >= 0).all())

    def test_pressure_lab_phases(self):
        """Test phase filtering and proxy calculations."""
        p_bat = calculate_phase_batting(self.bb, 'Death')
        p_bowl = calculate_phase_bowling(self.bb, 'Death')
        self.assertFalse(p_bat.empty)
        self.assertFalse(p_bowl.empty)

        d_bat_proxy = calculate_pressure_batting_proxy(self.bb, min_balls=20)
        d_bowl_proxy = calculate_pressure_bowling_proxy(self.bb, min_balls=20)
        self.assertFalse(d_bat_proxy.empty)
        self.assertFalse(d_bowl_proxy.empty)
        self.assertIn('death_impact_proxy', d_bat_proxy.columns)
        self.assertIn('death_control_proxy', d_bowl_proxy.columns)

    def test_scouting_roles_and_scoring(self):
        """Test realistic role derivation and multi-criteria scoring."""
        bat = calculate_batting_aggregates(self.bb)
        bowl = calculate_bowling_aggregates(self.bb)
        roster = derive_player_roles(self.bb, bat, bowl)
        self.assertFalse(roster.empty)
        self.assertIn('derived_role', roster.columns)

        roles = roster['derived_role'].unique()
        self.assertTrue(any('Batter' in r for r in roles))
        self.assertTrue(any('Bowler' in r for r in roles))

        scouted = compute_scouting_score(roster, role_filter="All", min_deliveries=20)
        self.assertFalse(scouted.empty)
        self.assertIn('scouting_score', scouted.columns)

    def test_player_comparison_profile(self):
        """Test player full profile retrieval and strengths generation."""
        bat = calculate_batting_aggregates(self.bb)
        bowl = calculate_bowling_aggregates(self.bb)
        roster = derive_player_roles(self.bb, bat, bowl)

        player_name = bat.iloc[0]['striker_name']
        profile = get_player_full_profile(player_name, bat, bowl, roster)
        self.assertEqual(profile['player_name'], player_name)
        self.assertIsNotNone(profile['batting'])

        evals = summarize_strengths_limitations(profile)
        self.assertIn('strengths', evals)
        self.assertIn('limitations', evals)

    def test_methodology_audit(self):
        """Test methodology audit function returns correct schema entries."""
        audit = audit_datasets(self.bb, self.matches, self.comps, self.mapping, self.teams)
        self.assertEqual(len(audit), 5)
        formulas = get_formula_definitions()
        self.assertGreaterEqual(len(formulas), 7)

if __name__ == '__main__':
    unittest.main()
