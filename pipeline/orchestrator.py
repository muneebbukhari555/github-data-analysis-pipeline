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

        # Score summary and leaders
        score_summary = self.scorer.get_score_summary(df)
        
        results = {
            "df": df,
            "score_summary": score_summary,
            "dimension_leaders": dimension_leaders,
            "commit_timeline": commit_timeline,
            "top_contributors": top_contributors,
            "top_committers": top_committers,
        }
        self.logger.info("Analysis pipeline complete")
        return results