import pandas as pd
from typing import List, Dict, Any, Optional
from collections import Counter
from config.settings import Settings

class ContributorAnalyzer:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.logger = self.settings.get_logger("ContributorAnalyzer")

    def analyze_top_contributors(self, df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
        contributor_data = {}

        for _, row in df.iterrows():
            contributors = row.get("contributors", [])
            if not isinstance(contributors, list):
                continue
            for c in contributors:
                login = c.get("login")
                if not login:
                    continue

                if login not in contributor_data:
                    contributor_data[login] = {
                        "login": login,
                        "total_contributions": 0,
                        "repos": set(),
                        "avatar_url": c.get("avatar_url", ""),
                    }
                contributor_data[login]["total_contributions"] += c.get("contributions", 0)
                contributor_data[login]["repos"].add(row["name"])
        records = []
        for login, data in contributor_data.items():
            records.append({
                "login": data["login"],
                "total_contributions": data["total_contributions"],
                "repo_count": len(data["repos"]),
                "repositories": ", ".join(sorted(data["repos"])),
                "avatar_url": data["avatar_url"],
            })
        result = pd.DataFrame(records)
        if result.empty:
            return result
        result = result.sort_values("total_contributions", ascending=False).head(top_n)
        result = result.reset_index(drop=True)
        self.logger.info("Identified top %d contributors", len(result))
        return result

    def analyze_top_committers(self, df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
        commit_users = Counter()
        for _, row in df.iterrows():
            commits = row.get("recent_commits", [])
            if not isinstance(commits, list):
                continue

            for c in commits:
                try:
                    author = c.get("author")
                    if isinstance(author, dict) and author.get("login"):
                        commit_users[author["login"]] += 1
                except (TypeError, KeyError):
                    continue
        records = [
            {"login": login, "recent_commits": count}
            for login, count in commit_users.most_common(top_n)
        ]
        result = pd.DataFrame(records)
        self.logger.info("Identified top %d committers", len(result))
        return result

    def analyze_cross_repo_contributors(self, df: pd.DataFrame) -> pd.DataFrame:
        contributor_repos = {}
        for _, row in df.iterrows():
            contributors = row.get("contributors", [])
            if not isinstance(contributors, list):
                continue
            for c in contributors:
                login = c.get("login")
                if not login:
                    continue
                if login not in contributor_repos:
                    contributor_repos[login] = set()
                contributor_repos[login].add(row["name"])

        # Filter to those contributing to 2+ repos
        cross_repo = [
            {"login": login, "repo_count": len(repos), "repositories": ", ".join(sorted(repos))}
            for login, repos in contributor_repos.items()
            if len(repos) >= 2
        ]
        result = pd.DataFrame(cross_repo)
        if not result.empty:
            result = result.sort_values("repo_count", ascending=False).reset_index(drop=True)
        self.logger.info("Found %d cross-repo contributors", len(result))
        return result

    def compute_contributor_dominance(self, df: pd.DataFrame) -> pd.DataFrame:
        records = []
        for _, row in df.iterrows():
            contributors = row.get("contributors", [])
            if not isinstance(contributors, list) or not contributors:
                continue
            total = sum(c.get("contributions", 0) for c in contributors)
            if total == 0:
                continue
            sorted_contribs = sorted(
                contributors, key=lambda x: x.get("contributions", 0), reverse=True
            )
            top1 = sorted_contribs[0]
            top1_share = top1.get("contributions", 0) / total
            # Top 5 share
            top5_total = sum(c.get("contributions", 0) for c in sorted_contribs[:5])
            top5_share = top5_total / total
            records.append({
                "name": row["name"],
                "top_contributor": top1.get("login", "N/A"),
                "top1_contribution_share": round(top1_share, 4),
                "top5_contribution_share": round(top5_share, 4),
                "total_contributors": len(contributors),
                "dominance_level": (
                    "high" if top1_share > 0.5
                    else "medium" if top1_share > 0.25
                    else "low"
                ),
            })
        result = pd.DataFrame(records)
        self.logger.info("Computed dominance metrics for %d repos", len(result))
        return result

    def compute_developer_influence_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        contributor_data = {}
        for _, row in df.iterrows():
            contributors = row.get("contributors", [])
            if not isinstance(contributors, list):
                continue
            repo_total = sum(c.get("contributions", 0) for c in contributors)
            for c in contributors:
                login = c.get("login")
                if not login:
                    continue
                contribs = c.get("contributions", 0)
                if login not in contributor_data:
                    contributor_data[login] = {
                        "login": login,
                        "total_contributions": 0,
                        "repo_count": 0,
                        "max_share_in_repo": 0.0,
                    }
                contributor_data[login]["total_contributions"] += contribs
                contributor_data[login]["repo_count"] += 1
                if repo_total > 0:
                    share = contribs / repo_total
                    contributor_data[login]["max_share_in_repo"] = max(
                        contributor_data[login]["max_share_in_repo"], share
                    )
        records = list(contributor_data.values())
        result = pd.DataFrame(records)
        if result.empty:
            return result
        result["volume_score"] = result["total_contributions"].rank(pct=True)
        result["diversity_score"] = result["repo_count"].rank(pct=True)
        result["concentration_score"] = result["max_share_in_repo"].rank(pct=True)
        result["influence_score"] = (
            result["volume_score"] * 0.4 +
            result["diversity_score"] * 0.35 +
            result["concentration_score"] * 0.25
        ).round(4)
        result = result.sort_values("influence_score", ascending=False).reset_index(drop=True)
        self.logger.info("Computed influence scores for %d developers", len(result))
        return result
    
