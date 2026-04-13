from typing import List, Dict, Any, Optional
from collectors.base_collector import BaseCollector
from models.commit import CommitModel
from config.settings import Settings

class CommitCollector(BaseCollector):
    def __init__(self, settings: Optional[Settings] = None):
        super().__init__(settings)

    def fetch_raw_commits(self, repo_name: str, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        url_template = (
            f"{self.settings.api_base_url}/repos/{repo_name}"
            f"/commits?per_page={{per_page}}&page={{page}}"
        )
        self.logger.info("Fetching commits for %s", repo_name)
        return self._paginated_fetch(url_template, max_pages)

    def collect(self, repo_name: str, max_pages: Optional[int] = None) -> List[CommitModel]:
        raw_commits = self.fetch_raw_commits(repo_name, max_pages)
        commits = CommitModel.extract_commit_list(raw_commits)
        self.logger.info("Collected %d commits for %s", len(commits), repo_name)
        return commits

    def collect_as_dicts(self, repo_name: str, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        return self.fetch_raw_commits(repo_name, max_pages)
