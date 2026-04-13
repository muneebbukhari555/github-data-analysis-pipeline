from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

@dataclass
class ContributorModel:
    #Represents a GitHub contributor with their activity metadata.
    login: str
    contributions: int = 0
    avatar_url: Optional[str] = None
    profile_url: Optional[str] = None
    contributor_type: str = "User"
    site_admin: bool = False

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "ContributorModel":
        return cls(
            login=data.get("login", "unknown"),
            contributions=data.get("contributions", 0),
            avatar_url=data.get("avatar_url"),
            profile_url=data.get("html_url"),
            contributor_type=data.get("type", "User"),
            site_admin=data.get("site_admin", False),
        )

    def to_dict(self) -> Dict[str, Any]:
        #Convert to dictionary for storage.
        return asdict(self)

    @staticmethod
    def extract_contributor_list(raw_contributors: List[Dict]) -> List["ContributorModel"]:
        contributors = []
        for c in raw_contributors:
            if isinstance(c, dict) and c.get("login"):
                contributors.append(ContributorModel.from_api_response(c))
        return contributors

    @staticmethod
    def compute_dominance(contributors: List["ContributorModel"]) -> float:
        if not contributors:
            return 0.0
        total = sum(c.contributions for c in contributors)
        if total == 0:
            return 0.0
        top = max(c.contributions for c in contributors)
        return top / total

    def __repr__(self) -> str:
        return f"ContributorModel(login='{self.login}', contributions={self.contributions})"
