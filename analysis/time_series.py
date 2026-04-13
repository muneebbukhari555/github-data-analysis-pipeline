import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from config.settings import Settings


class TimeSeriesAnalyzer:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.logger = self.settings.get_logger("TimeSeriesAnalyzer")

    def analyze_commit_timeline(self, df: pd.DataFrame) -> pd.DataFrame:
        #Analyze commit activity over time for each repository.
        self.logger.info("Analyzing commit timelines")
        timelines = []
        for _, row in df.iterrows():
            dates = row.get("commit_dates", [])
            if not dates:
                continue
            commit_df = pd.DataFrame({"date": dates})
            commit_df["date"] = pd.to_datetime(commit_df["date"], utc=True)
            commit_df["month"] = commit_df["date"].dt.to_period("M")

            monthly = commit_df.groupby("month").size().reset_index(name="commits")
            monthly["repo_name"] = row["name"]
            monthly["month_str"] = monthly["month"].astype(str)
            timelines.append(monthly)
        if not timelines:
            return pd.DataFrame()

        result = pd.concat(timelines, ignore_index=True)
        self.logger.info("Generated timeline data: %d monthly data points", len(result))
        return result

    def compute_commit_velocity(self, df: pd.DataFrame) -> pd.DataFrame:
        #Compute commit velocity metrics for each repository
        df = df.copy()
        df["weekly_commit_rate"] = df["commit_dates"].apply(self._weekly_commit_rate)
        df["commit_velocity_trend"] = df["commit_dates"].apply(self._velocity_trend)
        self.logger.debug("Commit velocity metrics computed")
        return df

    def analyze_snapshot_trends(self, snapshots: List[Dict[str, Any]]) -> pd.DataFrame:
        #Analyze trends from historical MongoDB snapshots.
        if not snapshots:
            self.logger.warning("No snapshots available for trend analysis")
            return pd.DataFrame()

        snap_df = pd.DataFrame(snapshots)
        snap_df["snapshot_date"] = pd.to_datetime(snap_df["snapshot_date"])
        trends = []
        for name, group in snap_df.groupby("name"):
            group = group.sort_values("snapshot_date")
            if len(group) < 2:
                continue
            trend = {
                "name": name,
                "snapshots_count": len(group),
                "first_snapshot": group["snapshot_date"].min(),
                "last_snapshot": group["snapshot_date"].max(),
            }

            # Compute growth for each metric
            for metric in ["stars", "forks", "open_issues", "contributors_count"]:
                if metric in group.columns:
                    first_val = group[metric].iloc[0]
                    last_val = group[metric].iloc[-1]
                    if first_val > 0:
                        trend[f"{metric}_growth_pct"] = round(
                            ((last_val - first_val) / first_val) * 100, 2
                        )
                    else:
                        trend[f"{metric}_growth_pct"] = 0.0
                    trend[f"{metric}_delta"] = last_val - first_val
            trends.append(trend)
        result = pd.DataFrame(trends)
        self.logger.info("Computed trends for %d repositories", len(result))
        return result

    def get_activity_heatmap_data(self, df: pd.DataFrame) -> pd.DataFrame:
        #Generate data for a commit activity heatmap.
        all_dates = []
        for _, row in df.iterrows():
            for d in row.get("commit_dates", []):
                if isinstance(d, datetime):
                    all_dates.append({
                        "repo": row["name"],
                        "day_of_week": d.strftime("%A"),
                        "hour": d.hour,
                    })
        if not all_dates:
            return pd.DataFrame()

        heatmap_df = pd.DataFrame(all_dates)
        return heatmap_df.groupby(["day_of_week", "hour"]).size().reset_index(name="count")

    @staticmethod
    def _weekly_commit_rate(dates: list) -> float:
        #Compute average commits per week
        if len(dates) < 2:
            return 0.0
        dates_sorted = sorted(dates)
        weeks = (dates_sorted[-1] - dates_sorted[0]).days / 7
        return round(len(dates) / max(weeks, 1), 2)

    @staticmethod
    def _velocity_trend(dates: list) -> str:
        #Determine if commit velocity is increasing, stable, or decreasing.
        if len(dates) < 4:
            return "insufficient_data"

        dates_sorted = sorted(dates)
        mid = len(dates_sorted) // 2
        first_half = dates_sorted[:mid]
        second_half = dates_sorted[mid:]

        first_span = (first_half[-1] - first_half[0]).days or 1
        second_span = (second_half[-1] - second_half[0]).days or 1

        first_rate = len(first_half) / first_span
        second_rate = len(second_half) / second_span

        ratio = second_rate / first_rate if first_rate > 0 else 1
        if ratio > 1.2:
            return "accelerating"
        elif ratio < 0.8:
            return "decelerating"
        return "stable"
    
