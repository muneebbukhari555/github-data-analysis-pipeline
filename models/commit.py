from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class CommitModel:
    #Represents a single Git commit with extracted metadata.
    sha: str
    message: str = ""
    author_name: Optional[str] = None
    author_login: Optional[str] = None
    author_email: Optional[str] = None
    date: Optional[str] = None
    committer_name: Optional[str] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "CommitModel":
        commit_data = data.get("commit", {})
        author_data = commit_data.get("author", {})
        top_author = data.get("author") or {}
        return cls(
            sha=data.get("sha", ""),
            message=commit_data.get("message", ""),
            author_name=author_data.get("name"),
            author_login=top_author.get("login"),
            author_email=author_data.get("email"),
            date=author_data.get("date"),
            committer_name=commit_data.get("committer", {}).get("name"),
        )
    @property
    def parsed_date(self) -> Optional[datetime]:
        #Parse the commit date string into a datetime object.
        if not self.date:
            return None
        try:
            return datetime.fromisoformat(self.date.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None

    def to_dict(self) -> Dict[str, Any]:
        #Convert to dictionary for storage.
        return asdict(self)

    @staticmethod
    def extract_commit_list(raw_commits: List[Dict]) -> List["CommitModel"]:
        #Bulk extraction: convert raw API commit dicts into CommitModel instances.
        commits = []
        for c in raw_commits:
            if isinstance(c, dict) and c.get("sha"):
                commits.append(CommitModel.from_api_response(c))
        return commits

    @staticmethod
    def extract_dates(commits: List["CommitModel"]) -> List[datetime]:
        #Extract parsed dates from a list of commits (filtering None values)
        return [c.parsed_date for c in commits if c.parsed_date is not None]

    @staticmethod
    def extract_unique_authors(commits: List["CommitModel"]) -> List[str]:
        #Get distinct author logins from a list of commits.
        authors = set()
        for c in commits:
            if c.author_login:
                authors.add(c.author_login)
        return sorted(authors)

    def __repr__(self) -> str:
        short_msg = self.message[:50] + "..." if len(self.message) > 50 else self.message
        return f"CommitModel(sha='{self.sha[:7]}', author='{self.author_login}', msg='{short_msg}')"
