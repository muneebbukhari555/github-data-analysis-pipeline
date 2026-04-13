from typing import List, Dict, Any, Optional
from collectors.base_collector import BaseCollector
from models.contributor import ContributorModel
from config.settings import Settings

class ContributorCollector(BaseCollector):
    def __init__(self, settings: Optional[Settings] = None):
        super().__init__(settings)

    def fetch_raw_contributors(self, repo_name: str, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        effective_max = max_pages or 3
        url_template = (
            f"{self.settings.api_base_url}/repos/{repo_name}"
            f"/contributors?per_page={{per_page}}&page={{page}}"
        )
        self.logger.info("Fetching contributors for %s", repo_name)
        return self._paginated_fetch(url_template, effective_max)

    def collect(self, repo_name: str, max_pages: Optional[int] = None) -> List[ContributorModel]:
        raw_contributors = self.fetch_raw_contributors(repo_name, max_pages)
        contributors = ContributorModel.extract_contributor_list(raw_contributors)
        self.logger.info(
            "Collected %d contributors for %s", len(contributors), repo_name
        )
        return contributors

    def collect_as_dicts(self, repo_name: str, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        return self.fetch_raw_contributors(repo_name, max_pages)
