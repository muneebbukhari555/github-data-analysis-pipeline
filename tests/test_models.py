#Unit tests for data models. Tests nested JSON processing and data validation.

import unittest
from models.repository import RepositoryModel
from models.contributor import ContributorModel
from models.commit import CommitModel

class TestRepositoryModel(unittest.TestCase):
    #Tests for RepositoryModel

    def test_from_api_response(self):
        """Test construction from raw GitHub API response."""
        raw = {
            "stargazers_count": 1000,
            "forks_count": 200,
            "open_issues_count": 50,
            "language": "Python",
            "created_at": "2020-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "description": "Test repo",
            "size": 5000,
            "watchers_count": 800,
            "has_wiki": True,
            "has_pages": False,
            "default_branch": "main",
            "license": {"spdx_id": "MIT"},
            "topics": ["python", "ml"],
        }
        model = RepositoryModel.from_api_response("test/repo", raw)

        self.assertEqual(model.name, "test/repo")
        self.assertEqual(model.stars, 1000)
        self.assertEqual(model.forks, 200)
        self.assertEqual(model.language, "Python")
        self.assertEqual(model.license_name, "MIT")
        self.assertEqual(model.topics, ["python", "ml"])

    def test_stars_per_day(self):
        #Test derived metric computation.
        model = RepositoryModel(
            name="test/repo",
            stars=365,
            created_at="2023-01-01T00:00:00Z",
        )
        # Should be approximately 1 star per day (depending on current date)
        self.assertGreater(model.stars_per_day, 0)

    def test_to_dict(self):
        #Test serialization to dictionary.
        model = RepositoryModel(name="test/repo", stars=100)
        d = model.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["name"], "test/repo")


class TestContributorModel(unittest.TestCase):
    #Tests for ContributorModel.

    def test_from_api_response(self):
        #Test construction from raw contributor JSON.
        raw = {
            "login": "testuser",
            "contributions": 150,
            "avatar_url": "https://example.com/avatar.png",
            "html_url": "https://github.com/testuser",
            "type": "User",
            "site_admin": False,
        }
        model = ContributorModel.from_api_response(raw)
        self.assertEqual(model.login, "testuser")
        self.assertEqual(model.contributions, 150)

    def test_compute_dominance(self):
        #Test contribution dominance calculation.
        contributors = [
            ContributorModel(login="a", contributions=80),
            ContributorModel(login="b", contributions=20),
        ]
        dominance = ContributorModel.compute_dominance(contributors)
        self.assertAlmostEqual(dominance, 0.8)

    def test_extract_contributor_list(self):
        #Test bulk extraction from raw dicts.
        raw = [
            {"login": "user1", "contributions": 100},
            {"login": "user2", "contributions": 50},
            {"invalid": "data"},
        ]
        result = ContributorModel.extract_contributor_list(raw)
        self.assertEqual(len(result), 2)


class TestCommitModel(unittest.TestCase):
    #Tests for CommitModel.

    def test_from_api_response(self):
        #Test construction from deeply nested commit JSON.
        raw = {
            "sha": "abc123def456",
            "commit": {
                "author": {
                    "name": "Test User",
                    "email": "test@example.com",
                    "date": "2024-01-15T10:30:00Z",
                },
                "message": "Fix bug in feature X",
                "committer": {"name": "Test Committer"},
            },
            "author": {"login": "testuser"},
        }
        model = CommitModel.from_api_response(raw)

        self.assertEqual(model.sha, "abc123def456")
        self.assertEqual(model.author_name, "Test User")
        self.assertEqual(model.author_login, "testuser")
        self.assertIn("Fix bug", model.message)

    def test_parsed_date(self):
        #Test date parsing from commit.
        model = CommitModel(sha="abc", date="2024-01-15T10:30:00Z")
        parsed = model.parsed_date
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.year, 2024)

    def test_extract_unique_authors(self):
        #Test unique author extraction.
        commits = [
            CommitModel(sha="1", author_login="alice"),
            CommitModel(sha="2", author_login="bob"),
            CommitModel(sha="3", author_login="alice"),
        ]
        authors = CommitModel.extract_unique_authors(commits)
        self.assertEqual(len(authors), 2)
        self.assertIn("alice", authors)

if __name__ == "__main__":
    unittest.main()
