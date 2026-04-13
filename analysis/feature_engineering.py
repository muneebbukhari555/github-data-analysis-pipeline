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
        #Parse string dates into datetime objects
        df = df.copy()
        for col in ["created_at", "updated_at"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
        return df

    def _compute_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        #Compute time based features from repository creation and update dates
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
        # Contributor diversity ratio of total contributions
        df["contributor_diversity"] = df["contributors"].apply(
            self._compute_contributor_diversity
        )
        self.logger.debug("Contributor features extracted")
        return df
    
    def _extract_commit_features(self, df: pd.DataFrame) -> pd.DataFrame:
        #Extract features from nested commit list JSON
        df = df.copy()
        # Ensure recent_commits column contains lists
        df["recent_commits"] = df["recent_commits"].apply(
            lambda x: x if isinstance(x, list) else []
        )
        # Basic commit count
        df["commit_count"] = df["recent_commits"].apply(len)
        # Extract commit dates from nested JSON
        df["commit_dates"] = df["recent_commits"].apply(self._extract_commit_dates)
        # Commit frequency (commits per day within the observed time window)
        df["commit_frequency"] = df["commit_dates"].apply(self._compute_commit_frequency)
        # Number of unique active days
        df["active_commit_days"] = df["commit_dates"].apply(
            lambda dates: len(set(d.date() for d in dates)) if dates else 0
        )
        # Unique commit authors
        df["unique_commit_authors"] = df["recent_commits"].apply(
            lambda commits: len(set(
                c.get("author", {}).get("login", "")
                for c in commits
                if isinstance(c.get("author"), dict) and c["author"].get("login")
            ))
        )
        # Commits per author ratio
        df["commits_per_author"] = (
            df["commit_count"] / df["unique_commit_authors"].replace(0, 1)
        )
        self.logger.debug("Commit features extracted")
        return df

    def _compute_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        #Compute higher-order derived metrics from base features
        df = df.copy()
        #Engagement ratio forks relative to stars
        df["engagement_ratio"] = df["forks"] / df["stars"].replace(0, 1)
        #Contribution efficiency total output per contributor
        df["contribution_efficiency"] = (
            df["total_contributions"] / df["contributors_count"].replace(0, 1)
        )
        #Issue density: open issues relative to repository size/activity
        open_issues_col = "open_issues" if "open_issues" in df.columns else "issues"
        if open_issues_col in df.columns:
            df["issue_density"] = df[open_issues_col] / df["stars"].replace(0, 1)
        # Stability score: stars to issues ratio
        if open_issues_col in df.columns:
            df["stability_score"] = df["stars"] / df[open_issues_col].replace(0, 1)
        # Bus factor estimate: 1 / top_contributor_share (higher = more distributed)
        df["bus_factor_estimate"] = 1 / df["top_contributor_share"].replace(0, 1)
        df["bus_factor_estimate"] = df["bus_factor_estimate"].clip(upper=100)
        #Community health composite
        df["community_health"] = (
            df["contributors_count"].rank(pct=True) * 0.3 +
            df["contributor_diversity"].rank(pct=True) * 0.3 +
            df["commit_frequency"].rank(pct=True) * 0.2 +
            df["engagement_ratio"].rank(pct=True) * 0.2
        )
        self.logger.debug("Derived metrics computed")
        return df

    @staticmethod
    def _extract_commit_dates(commits: list) -> list:
        #Extract datetime objects from nested commit JSON
        dates = []
        for c in commits:
            try:
                date_str = c["commit"]["author"]["date"]
                dates.append(pd.to_datetime(date_str, utc=True))
            except (KeyError, TypeError, ValueError):
                continue
        return dates

    @staticmethod
    def _compute_commit_frequency(dates: list) -> float:
        #Compute commit frequency per day
        if len(dates) < 2:
            return 0.0
        dates_sorted = sorted(dates)
        time_span_days = (dates_sorted[-1] - dates_sorted[0]).days
        if time_span_days <= 0:
            return float(len(dates))
        return round(len(dates) / time_span_days, 4)

    @staticmethod
    def _compute_top_contributor_share(contributors: list) -> float:
        #Compute the fraction of total contributions.
        if not contributors:
            return 0.0
        total = sum(c.get("contributions", 0) for c in contributors)
        if total == 0:
            return 0.0
        top = max(c.get("contributions", 0) for c in contributors)
        return round(top / total, 4)

    @staticmethod
    def _compute_contributor_diversity(contributors: list) -> float:
        #Compute contributor diversity meaningful contributions
        if not contributors:
            return 0.0
        total = sum(c.get("contributions", 0) for c in contributors)
        if total == 0:
            return 0.0
        threshold = total * 0.01
        meaningful = sum(1 for c in contributors if c.get("contributions", 0) > threshold)
        return round(meaningful / len(contributors), 4)
