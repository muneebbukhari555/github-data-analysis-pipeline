from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class RepositoryModel:
    "Represents a GitHub repository with its core metadata."
    name: str
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    language: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    description: Optional[str] = None
    size: int = 0
    watchers: int = 0
    has_wiki: bool = False
    has_pages: bool = False
    default_branch: str = "main"
    license_name: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    contributors: List[Dict[str, Any]] = field(default_factory=list)
    recent_commits: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: Optional[datetime] = None

    @classmethod
    def from_api_response(cls, repo_name: str, data: Dict[str, Any]) -> "RepositoryModel":
        license_info = data.get("license") or {}
        return cls(
            name=repo_name,
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            open_issues=data.get("open_issues_count", 0),
            language=data.get("language"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            description=data.get("description"),
            size=data.get("size", 0),
            watchers=data.get("watchers_count", 0),
            has_wiki=data.get("has_wiki", False),
            has_pages=data.get("has_pages", False),
            default_branch=data.get("default_branch", "main"),
            license_name=license_info.get("spdx_id"),
            topics=data.get("topics", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        "Convert model to dictionary for MongoDB storage."
        result = asdict(self)
        if self.timestamp:
            result["timestamp"] = self.timestamp
        return result

    @property
    def age_days(self) -> int:
        "Calculate repository age in days from creation date."
        if not self.created_at:
            return 0
        try:
            created = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
            delta = datetime.now(created.tzinfo) - created
            return delta.days
        except (ValueError, TypeError):
            return 0

    @property
    def stars_per_day(self) -> float:
        "Derived metric: average stars gained per day since creation."
        age = self.age_days
        return self.stars / age if age > 0 else 0.0

    def __repr__(self) -> str:
        return (
            f"RepositoryModel(name='{self.name}', stars={self.stars}, "
            f"forks={self.forks}, contributors={len(self.contributors)})"
        )
