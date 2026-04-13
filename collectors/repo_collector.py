from typing import Dict, Any, Optional
from collectors.base_collector import BaseCollector
from models.repository import RepositoryModel
from config.settings import Settings


class RepoCollector(BaseCollector):
    def __init__(self, settings: Optional[Settings] = None):
        super().__init__(settings)

    def fetch_repo_metadata(self, repo_name: str) -> Dict[str, Any]:
        url = f"{self.settings.api_base_url}/repos/{repo_name}"
        self.logger.info("Fetching metadata for %s", repo_name)
        return self._single_fetch(url)

    def collect(self, repo_name: str) -> RepositoryModel:
        raw_data = self.fetch_repo_metadata(repo_name)
        if not raw_data:
            self.logger.warning("No data returned for %s", repo_name)
            return RepositoryModel(name=repo_name)

        model = RepositoryModel.from_api_response(repo_name, raw_data)
        self.logger.info(
            "Collected %s: stars=%d, forks=%d",
            repo_name, model.stars, model.forks
        )
        return model
