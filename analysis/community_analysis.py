"""
Community strength analysis module.
Evaluates the health, diversity, and resilience of open-source communities
around each repository.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Any
from config.settings import Settings


class CommunityAnalyzer:
    """
    Analyzes community health and strength for repositories.

    Metrics:
    - Community Size Score
    - Diversity Index (contributor distribution)
    - Engagement Quality (fork-to-star ratio, issue activity)
    - Resilience Score (bus factor, contributor spread)
    - Overall Community Grade
    """

    # Grading thresholds
    GRADE_THRESHOLDS = {
        "A+": 90, "A": 80, "B+": 70, "B": 60,
        "C+": 50, "C": 40, "D": 30, "F": 0,
    }

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.logger = self.settings.get_logger("CommunityAnalyzer")

    def analyze_community(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Run full community analysis pipeline.

        Args:
            df: DataFrame with engineered features.

        Returns:
            DataFrame with community metrics and grades.
        """
        self.logger.info("Starting community analysis for %d repos", len(df))

        df = df.copy()
        df = self._compute_size_score(df)
        df = self._compute_diversity_index(df)
        df = self._compute_engagement_quality(df)
        df = self._compute_resilience_score(df)
        df = self._compute_community_grade(df)

        return df

    def _compute_size_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Community size score based on contributors, watchers, and stars.
        Normalized via percentile ranking.
        """
        df["community_size_score"] = (
            df["contributors_count"].rank(pct=True) * 0.4 +
            df["stars"].rank(pct=True) * 0.3 +
            df["forks"].rank(pct=True) * 0.3
        ) * 100
        df["community_size_score"] = df["community_size_score"].round(2)
        return df

    def _compute_diversity_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute a diversity index based on contributor distribution.
        Uses Gini-like coefficient from contributor share data.
        """
        df["diversity_index"] = df["contributors"].apply(self._gini_diversity)
        df["diversity_index_score"] = df["diversity_index"].rank(pct=True) * 100
        return df

    def _compute_engagement_quality(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Measure quality of community engagement.
        High fork:star ratio suggests active contribution vs passive observation.
        """
        df["engagement_quality_score"] = (
            df["engagement_ratio"].rank(pct=True) * 0.4 +
            df["commit_frequency"].rank(pct=True) * 0.3 +
            df["unique_commit_authors"].rank(pct=True) * 0.3
        ) * 100
        df["engagement_quality_score"] = df["engagement_quality_score"].round(2)
        return df

    def _compute_resilience_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Community resilience: ability to sustain without key individuals.
        Inverse of contributor dominance + contributor count.
        """
        # Lower top_contributor_share = higher resilience
        if "top_contributor_share" in df.columns:
            df["resilience_raw"] = 1 - df["top_contributor_share"]
        else:
            df["resilience_raw"] = 0.5

        df["resilience_score"] = (
            df["resilience_raw"].rank(pct=True) * 0.5 +
            df["contributors_count"].rank(pct=True) * 0.3 +
            df["contributor_diversity"].rank(pct=True) * 0.2
        ) * 100
        df["resilience_score"] = df["resilience_score"].round(2)
        return df

    def _compute_community_grade(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute overall community grade (A+ to F) from all community scores.
        """
        df["community_total_score"] = (
            df["community_size_score"] * 0.25 +
            df["diversity_index_score"] * 0.25 +
            df["engagement_quality_score"] * 0.25 +
            df["resilience_score"] * 0.25
        ).round(2)

        df["community_grade"] = df["community_total_score"].apply(self._score_to_grade)
        return df

    def get_community_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get a summary table of community metrics."""
        cols = [
            "name", "community_total_score", "community_grade",
            "community_size_score", "diversity_index_score",
            "engagement_quality_score", "resilience_score",
        ]
        available = [c for c in cols if c in df.columns]
        return df[available].sort_values("community_total_score", ascending=False)

    def get_community_insights(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generate natural language insights about community patterns.
        """
        insights = []

        if "community_grade" in df.columns:
            a_repos = df[df["community_grade"].isin(["A+", "A"])]["name"].tolist()
            if a_repos:
                insights.append({
                    "type": "strength",
                    "message": f"Strong communities: {', '.join(a_repos)}",
                    "repos": a_repos,
                })

            weak_repos = df[df["community_grade"].isin(["D", "F"])]["name"].tolist()
            if weak_repos:
                insights.append({
                    "type": "concern",
                    "message": f"Weak community health: {', '.join(weak_repos)}",
                    "repos": weak_repos,
                })

        if "top_contributor_share" in df.columns:
            high_risk = df[df["top_contributor_share"] > 0.5]["name"].tolist()
            if high_risk:
                insights.append({
                    "type": "risk",
                    "message": f"High bus-factor risk (single contributor >50%): {', '.join(high_risk)}",
                    "repos": high_risk,
                })

        return insights

    # --- Helper methods ---

    @staticmethod
    def _gini_diversity(contributors: list) -> float:
        """
        Compute diversity using inverted Gini coefficient.
        0 = all contributions from one person; 1 = perfectly distributed.
        """
        if not isinstance(contributors, list) or not contributors:
            return 0.0

        contributions = sorted([c.get("contributions", 0) for c in contributors])
        n = len(contributions)
        if n == 0 or sum(contributions) == 0:
            return 0.0

        cumulative = np.cumsum(contributions)
        gini = (2 * sum((i + 1) * c for i, c in enumerate(contributions))) / (
            n * sum(contributions)
        ) - (n + 1) / n

        # Invert: high gini = unequal; we want high = diverse
        return round(max(0, 1 - gini), 4)

    @staticmethod
    def _score_to_grade(score: float) -> str:
        """Convert numeric score to letter grade."""
        for grade, threshold in sorted(
            CommunityAnalyzer.GRADE_THRESHOLDS.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if score >= threshold:
                return grade
        return "F"
