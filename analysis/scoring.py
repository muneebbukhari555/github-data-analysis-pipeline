
import pandas as pd
import numpy as np
from typing import Optional, Dict
from config.settings import Settings

class RepositoryScorer:
    # Score weights for each dimension
    ACTIVITY_WEIGHTS = {
        "commit_count": 0.35,
        "commit_frequency": 0.25,
        "active_commit_days": 0.20,
        "unique_commit_authors": 0.20,
    }
    SUCCESS_WEIGHTS = {
        "stars": 0.40,
        "forks": 0.30,
        "contributors_count": 0.20,
        "watchers": 0.10,
    }
    INFLUENCE_WEIGHTS = {
        "total_contributions": 0.30,
        "avg_contributions_per_person": 0.25,
        "contribution_efficiency": 0.25,
        "commits_per_author": 0.20,
    }
    COMMUNITY_WEIGHTS = {
        "contributors_count": 0.25,
        "contributor_diversity": 0.25,
        "engagement_ratio": 0.20,
        "bus_factor_estimate": 0.15,
        "active_lifespan_ratio": 0.15,
    }
    OVERALL_WEIGHTS = {
        "activity_score": 0.30,
        "success_score": 0.25,
        "community_strength_score": 0.25,
        "developer_influence_score": 0.20,
    }
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.logger = self.settings.get_logger("RepositoryScorer")

    def compute_all_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        self.logger.info("Computing scores for %d repositories", len(df))
        df = df.copy()
        df = self._compute_dimension_score(df, "activity_score", self.ACTIVITY_WEIGHTS)
        df = self._compute_dimension_score(df, "success_score", self.SUCCESS_WEIGHTS)
        df = self._compute_dimension_score(df, "developer_influence_score", self.INFLUENCE_WEIGHTS)
        df = self._compute_dimension_score(df, "community_strength_score", self.COMMUNITY_WEIGHTS)
        df = self._compute_overall_score(df)
        df = self._assign_ranks(df)
        self.logger.info("All scores computed successfully")
        return df

    def _compute_dimension_score(
        self, df: pd.DataFrame, score_name: str, weights: Dict[str, float]
    ) -> pd.DataFrame:
        df = df.copy()
        score = pd.Series(0.0, index=df.index)

        for metric, weight in weights.items():
            if metric in df.columns:
                # Percentile rank normalization: handles different scales
                normalized = df[metric].rank(pct=True).fillna(0)
                score += normalized * weight
            else:
                self.logger.warning("Missing metric '%s' for score '%s'", metric, score_name)

        # Scale to 0-100
        df[score_name] = (score * 100).round(2)
        return df
    
    def _compute_overall_score(self, df: pd.DataFrame) -> pd.DataFrame:
        #Compute weighted overall score from dimension scores.
        df = df.copy()
        overall = pd.Series(0.0, index=df.index)

        for score_col, weight in self.OVERALL_WEIGHTS.items():
            if score_col in df.columns:
                overall += df[score_col] * weight
        df["overall_score"] = overall.round(2)
        return df

    def _assign_ranks(self, df: pd.DataFrame) -> pd.DataFrame:
        #Assign rank positions for each scoring dimension.
        df = df.copy()
        score_cols = [
            "activity_score", "success_score",
            "developer_influence_score", "community_strength_score",
            "overall_score"
        ]
        for col in score_cols:
            if col in df.columns:
                df[f"{col}_rank"] = df[col].rank(ascending=False, method="min").astype(int)
        return df

    def get_score_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        #Generate a concise summary table of all scores and ranks.
        score_cols = [
            "name", "overall_score", "activity_score", "success_score",
            "developer_influence_score", "community_strength_score",
            "overall_score_rank"
        ]
        available = [c for c in score_cols if c in df.columns]
        return df[available].sort_values("overall_score", ascending=False)

    def get_dimension_leaders(self, df: pd.DataFrame) -> Dict[str, str]:
        #Identify the top repository in each scoring dimension
        dimensions = {
            "Activity": "activity_score",
            "Success": "success_score",
            "Developer Influence": "developer_influence_score",
            "Community Strength": "community_strength_score",
            "Overall": "overall_score",
        }
        leaders = {}
        for dim_name, col in dimensions.items():
            if col in df.columns:
                idx = df[col].idxmax()
                leaders[dim_name] = df.loc[idx, "name"]
        return leaders
    