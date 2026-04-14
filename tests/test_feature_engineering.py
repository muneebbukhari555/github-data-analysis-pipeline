#Unit tests for the feature engineering module.
import unittest
import pandas as pd
import numpy as np
from analysis.feature_engineering import FeatureEngineer

class TestFeatureEngineer(unittest.TestCase):
    #Tests for FeatureEngineer class
    def setUp(self):
        #Set up test data simulating MongoDB records
        self.engineer = FeatureEngineer()
        self.test_data = pd.DataFrame([
            {
                "name": "test/repo1",
                "stars": 1000,
                "forks": 200,
                "issues": 50,
                "open_issues": 50,
                "language": "Python",
                "created_at": "2020-01-01T00:00:00Z",
                "updated_at": "2024-06-01T00:00:00Z",
                "contributors": [
                    {"login": "alice", "contributions": 500},
                    {"login": "bob", "contributions": 300},
                    {"login": "charlie", "contributions": 200},
                ],
                "recent_commits": [
                    {
                        "sha": "abc",
                        "commit": {"author": {"name": "Alice", "date": "2024-01-15T10:00:00Z"}},
                        "author": {"login": "alice"},
                    },
                    {
                        "sha": "def",
                        "commit": {"author": {"name": "Bob", "date": "2024-01-20T14:00:00Z"}},
                        "author": {"login": "bob"},
                    },
                ],
            },
            {
                "name": "test/repo2",
                "stars": 500,
                "forks": 100,
                "issues": 30,
                "open_issues": 30,
                "language": "Go",
                "created_at": "2021-06-01T00:00:00Z",
                "updated_at": "2024-08-01T00:00:00Z",
                "contributors": [
                    {"login": "dave", "contributions": 900},
                    {"login": "eve", "contributions": 100},
                ],
                "recent_commits": [
                    {
                        "sha": "ghi",
                        "commit": {"author": {"name": "Dave", "date": "2024-02-01T09:00:00Z"}},
                        "author": {"login": "dave"},
                    },
                ],
            },
        ])

    def test_engineer_features_returns_dataframe(self):
        #Test that engineer_features returns a DataFrame with new columns.
        result = self.engineer.engineer_features(self.test_data)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result.columns), len(self.test_data.columns))

    def test_temporal_features_computed(self):
        #Test that temporal features are added.
        result = self.engineer.engineer_features(self.test_data)
        self.assertIn("age_days", result.columns)
        self.assertIn("stars_per_day", result.columns)
        self.assertIn("forks_per_day", result.columns)
        self.assertTrue((result["age_days"] > 0).all())

    def test_contributor_features_extracted(self):
        #Test contributor feature extraction from nested lists.
        result = self.engineer.engineer_features(self.test_data)
        self.assertIn("contributors_count", result.columns)
        self.assertIn("total_contributions", result.columns)
        self.assertIn("top_contributor_share", result.columns)
        self.assertEqual(result.iloc[0]["contributors_count"], 3)
        self.assertEqual(result.iloc[0]["total_contributions"], 1000)

    def test_commit_features_extracted(self):
        #Test commit feature extraction from nested JSON.
        result = self.engineer.engineer_features(self.test_data)
        self.assertIn("commit_count", result.columns)
        self.assertIn("commit_frequency", result.columns)
        self.assertIn("unique_commit_authors", result.columns)
        self.assertEqual(result.iloc[0]["commit_count"], 2)

    def test_derived_metrics_computed(self):
        #Test that derived metrics are computed correctly.
        result = self.engineer.engineer_features(self.test_data)
        self.assertIn("engagement_ratio", result.columns)
        self.assertIn("stability_score", result.columns)
        self.assertIn("bus_factor_estimate", result.columns)
        self.assertIn("community_health", result.columns)

    def test_commit_frequency_calculation(self):
        #Test time-window based commit frequency.
        freq = FeatureEngineer._compute_commit_frequency([
            pd.Timestamp("2024-01-01", tz="UTC"),
            pd.Timestamp("2024-01-11", tz="UTC"),
        ])
        # 2 commits over 10 days = 0.2
        self.assertAlmostEqual(freq, 0.2, places=1)

    def test_empty_contributors_handled(self):
        #Test graceful handling of empty contributor lists.
        df = pd.DataFrame([{
            "name": "test/empty",
            "stars": 10, "forks": 5, "issues": 1, "open_issues": 1,
            "language": "Rust",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "contributors": [],
            "recent_commits": [],
        }])
        result = self.engineer.engineer_features(df)
        self.assertEqual(result.iloc[0]["contributors_count"], 0)
        self.assertEqual(result.iloc[0]["commit_count"], 0)

if __name__ == "__main__":
    unittest.main()
