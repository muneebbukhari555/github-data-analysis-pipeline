import pandas as pd
from typing import Optional, List, Dict, Any
from datetime import datetime

from config.settings import Settings
from collectors.repo_collector import RepoCollector
from collectors.commit_collector import CommitCollector
from collectors.contributor_collector import ContributorCollector
from database.repository_store import RepositoryStore
from database.snapshot_store import SnapshotStore
from analysis.feature_engineering import FeatureEngineer
from analysis.scoring import RepositoryScorer
from analysis.time_series import TimeSeriesAnalyzer
from analysis.contributor_analysis import ContributorAnalyzer
from analysis.contributor_analysis import ContributorAnalyzer
from analysis.community_analysis import CommunityAnalyzer

class PipelineOrchestrator:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.logger = self.settings.get_logger("PipelineOrchestrator")
        # Initialize components
        self.repo_collector = RepoCollector(self.settings)
        self.commit_collector = CommitCollector(self.settings)
        self.contributor_collector = ContributorCollector(self.settings)
        self.repo_store = RepositoryStore(self.settings)
        self.snapshot_store = SnapshotStore(self.settings)
        self.feature_engineer = FeatureEngineer(self.settings)
        self.scorer = RepositoryScorer(self.settings)
        self.time_series_analyzer = TimeSeriesAnalyzer(self.settings)
        self.contributor_analyzer = ContributorAnalyzer(self.settings)
        self.community_analyzer = CommunityAnalyzer(self.settings)
      
    def run_collection(self, repos: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        target_repos = repos or self.settings.target_repos
        self.logger.info("Starting collection for %d repositories", len(target_repos))
        dataset = []
        for repo in target_repos:
            try:
                self.logger.info("Processing: %s", repo)
                repo_model = self.repo_collector.collect(repo)
                contributors = self.contributor_collector.collect_as_dicts(repo)
                commits = self.commit_collector.collect_as_dicts(repo)

                # Assemble complete record
                record = repo_model.to_dict()
                record["contributors"] = contributors
                record["recent_commits"] = commits
                record["timestamp"] = datetime.utcnow()

                dataset.append(record)
                self.logger.info(
                    "Collected %s: %d contributors, %d commits",
                    repo, len(contributors), len(commits)
                )
            except Exception as e:
                self.logger.error("Error collecting %s: %s", repo, str(e))
                continue
        self.logger.info("Collection complete: %d/%d repos", len(dataset), len(target_repos))
        return dataset
    
    def run_storage(self, dataset: List[Dict[str, Any]]) -> None:
        #Store collected data in MongoDB and save time-series snapshot
        self.logger.info("Storing %d repository records", len(dataset))
        self.repo_store.insert_many(dataset)
        self.snapshot_store.save_snapshot(dataset)
        self.logger.info("Storage complete")
    
    def run_analysis(self) -> Dict[str, Any]:
        self.logger.info("Starting analysis pipeline")
        # Load latest data from MongoDB
        raw_data = self.repo_store.find_latest_snapshot()
        if not raw_data:
            self.logger.error("No data in MongoDB. Run collection first.")
            return {}
        df = pd.DataFrame(raw_data)
        self.logger.info("Loaded %d repositories from MongoDB", len(df))

        # Feature Engineering
        df = self.feature_engineer.engineer_features(df)

        # Multi dimensional Scoring
        df = self.scorer.compute_all_scores(df)

        # Time-Series Analysis
        commit_timeline = self.time_series_analyzer.analyze_commit_timeline(df)
        df = self.time_series_analyzer.compute_commit_velocity(df)

        # Contributor Analysis
        top_contributors = self.contributor_analyzer.analyze_top_contributors(df)
        top_committers = self.contributor_analyzer.analyze_top_committers(df)
        cross_repo = self.contributor_analyzer.analyze_cross_repo_contributors(df)
        dominance = self.contributor_analyzer.compute_contributor_dominance(df)
        influence_scores = self.contributor_analyzer.compute_developer_influence_scores(df)

        # Community Analysis
        df = self.community_analyzer.analyze_community(df)
        community_summary = self.community_analyzer.get_community_summary(df)
        community_insights = self.community_analyzer.get_community_insights(df)

        # Historical Trends (from snapshots)
        snapshots = self.snapshot_store.get_all_history()
        trends = self.time_series_analyzer.analyze_snapshot_trends(snapshots)

        # Score summary and leaders
        score_summary = self.scorer.get_score_summary(df)
        dimension_leaders = self.scorer.get_dimension_leaders(df)

        # Activity heatmap data
        heatmap_data = self.time_series_analyzer.get_activity_heatmap_data(df)
        
        results = {
            "df": df,
            "score_summary": score_summary,
            "dimension_leaders": dimension_leaders,
            "commit_timeline": commit_timeline,
            "top_contributors": top_contributors,
            "top_committers": top_committers,
            "cross_repo_contributors": cross_repo,
            "contributor_dominance": dominance,
            "developer_influence": influence_scores,
            "community_summary": community_summary,
            "community_insights": community_insights,
            "historical_trends": trends,
            "heatmap_data": heatmap_data,
        }
        self.logger.info("Analysis pipeline complete")
        return results
    
    def run_full_pipeline(self, repos: Optional[List[str]] = None) -> Dict[str, Any]:
        #Execute the complete pipeline end-to-end: collection, storage, and analysis
        self.logger.info("=== Starting Full Pipeline ===")
        # Collect and Store
        dataset = self.run_collection(repos)
        if dataset:
            self.run_storage(dataset)
        # Analyze
        results = self.run_analysis()
        self.logger.info("=== Full Pipeline Complete ===")
        return results

    def run_analysis_only(self) -> Dict[str, Any]:
        #Run only the analysis stages
        return self.run_analysis()