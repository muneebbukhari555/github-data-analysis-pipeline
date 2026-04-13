import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from collections import Counter
from datetime import datetime
from config.settings import Settings

class FeatureEngineer:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.logger = self.settings.get_logger("FeatureEngineer")

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        self.logger.info("Starting feature engineering on %d repositories", len(df))
        df = self._parse_dates(df)
        df = self._compute_temporal_features(df)
        df = self._extract_contributor_features(df)
        df = self._extract_commit_features(df)
        df = self._compute_derived_metrics(df)
        self.logger.info("Feature engineering complete: %d features", len(df.columns))
        return df

    def _parse_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        "Parse string dates into datetime objects."
        df = df.copy()
        for col in ["created_at", "updated_at"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
        return df

    def _compute_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        "Compute time based features from repository creation and update dates"
        df = df.copy()
        now = pd.Timestamp.now(tz="UTC")

        if "created_at" in df.columns:
            df["age_days"] = (now - df["created_at"]).dt.days.fillna(0).astype(int)
            df["stars_per_day"] = df["stars"] / df["age_days"].replace(0, 1)
            df["forks_per_day"] = df["forks"] / df["age_days"].replace(0, 1)
        if "updated_at" in df.columns and "created_at" in df.columns:
            df["days_since_update"] = (now - df["updated_at"]).dt.days.fillna(0).astype(int)
            df["active_lifespan_ratio"] = 1 - (
                df["days_since_update"] / df["age_days"].replace(0, 1)
            )
            df["active_lifespan_ratio"] = df["active_lifespan_ratio"].clip(0, 1)
        self.logger.debug("Temporal features computed")
        return df

    def _extract_contributor_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # Ensure contributors column contains lists
        df["contributors"] = df["contributors"].apply(
            lambda x: x if isinstance(x, list) else []
        )
        # Basic counts
        df["contributors_count"] = df["contributors"].apply(len)
        df["total_contributions"] = df["contributors"].apply(
            lambda contribs: sum(c.get("contributions", 0) for c in contribs)
        )
        # Average contributions per contributor
        df["avg_contributions_per_person"] = (
            df["total_contributions"] / df["contributors_count"].replace(0, 1)
        )
        df["top_contributor_share"] = df["contributors"].apply(
            self._compute_top_contributor_share
        )
        # Top contributor login
        df["top_contributor"] = df["contributors"].apply(
            lambda contribs: (
                max(contribs, key=lambda x: x.get("contributions", 0)).get("login", "N/A")
                if contribs else "N/A"
            )
        )
        # Contributor diversity: ratio of contributors with >1% of total contributions
        df["contributor_diversity"] = df["contributors"].apply(
            self._compute_contributor_diversity
        )
        self.logger.debug("Contributor features extracted")
        return df

    @staticmethod
    def _compute_top_contributor_share(contributors: list) -> float:
        "Compute the fraction of total contributions made by the top contributor."
        if not contributors:
            return 0.0
        total = sum(c.get("contributions", 0) for c in contributors)
        if total == 0:
            return 0.0
        top = max(c.get("contributions", 0) for c in contributors)
        return round(top / total, 4)

    @staticmethod
    def _compute_contributor_diversity(contributors: list) -> float:
        "Compute contributor diversity fraction of contributors with meaningful contributions."
        if not contributors:
            return 0.0
        total = sum(c.get("contributions", 0) for c in contributors)
        if total == 0:
            return 0.0
        threshold = total * 0.01
        meaningful = sum(1 for c in contributors if c.get("contributions", 0) > threshold)
        return round(meaningful / len(contributors), 4)
