#Unit tests for the multi-dimensional scoring module.

import unittest
import pandas as pd
from analysis.scoring import RepositoryScorer

class TestRepositoryScorer(unittest.TestCase):
    #Tests for RepositoryScorer class.
    def setUp(self):
        """Set up test DataFrame with pre-computed features."""
        self.scorer = RepositoryScorer()
        self.test_df = pd.DataFrame([
            {
                "name": "repo/a",
                "commit_count": 100, "commit_frequency": 2.5,
                "active_commit_days": 30, "unique_commit_authors": 15,
                "stars": 5000, "forks": 1000, "contributors_count": 200,
                "watchers": 4000,
                "total_contributions": 8000, "avg_contributions_per_person": 40,
                "contribution_efficiency": 40, "commits_per_author": 6.67,
                "contributor_diversity": 0.6, "engagement_ratio": 0.2,
                "bus_factor_estimate": 5, "active_lifespan_ratio": 0.9,
                "top_contributor_share": 0.2,
            },
            {
                "name": "repo/b",
                "commit_count": 50, "commit_frequency": 1.0,
                "active_commit_days": 15, "unique_commit_authors": 5,
                "stars": 2000, "forks": 300, "contributors_count": 50,
                "watchers": 1500,
                "total_contributions": 3000, "avg_contributions_per_person": 60,
                "contribution_efficiency": 60, "commits_per_author": 10,
                "contributor_diversity": 0.3, "engagement_ratio": 0.15,
                "bus_factor_estimate": 2, "active_lifespan_ratio": 0.7,
                "top_contributor_share": 0.5,
            },
        ])

    def test_compute_all_scores(self):
        #Test that all score columns are created.
        result = self.scorer.compute_all_scores(self.test_df)
        expected_cols = [
            "activity_score", "success_score",
            "developer_influence_score", "community_strength_score",
            "overall_score",
        ]
        for col in expected_cols:
            self.assertIn(col, result.columns)

    def test_scores_between_0_and_100(self):
        #Test that all scores fall within valid range.
        result = self.scorer.compute_all_scores(self.test_df)
        for col in ["activity_score", "success_score", "overall_score"]:
            self.assertTrue((result[col] >= 0).all())
            self.assertTrue((result[col] <= 100).all())

    def test_ranks_assigned(self):
        #Test that rank columns are created.
        result = self.scorer.compute_all_scores(self.test_df)
        self.assertIn("overall_score_rank", result.columns)
        self.assertTrue((result["overall_score_rank"] >= 1).all())

    def test_get_dimension_leaders(self):
        #Test dimension leaders identification.
        result = self.scorer.compute_all_scores(self.test_df)
        leaders = self.scorer.get_dimension_leaders(result)
        self.assertIn("Overall", leaders)
        self.assertIn("Activity", leaders)

if __name__ == "__main__":
    unittest.main()
