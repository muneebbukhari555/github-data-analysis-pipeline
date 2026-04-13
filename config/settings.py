import os
import logging
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    # GitHub API
    github_token: str = field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))
    api_base_url: str = "https://api.github.com"
    max_api_pages: int = field(
        default_factory=lambda: int(os.getenv("MAX_API_PAGES", "5"))
    )
    api_timeout: int = field(
        default_factory=lambda: int(os.getenv("API_TIMEOUT", "10"))
    )
    per_page: int = 100
    rate_limit_sleep: int = 60
    # MongoDB
    mongo_uri: str = field(
        default_factory=lambda: os.getenv("MONGO_URI", "mongodb://localhost:27017")
    )
    mongo_db: str = field(
        default_factory=lambda: os.getenv("MONGO_DB", "github_pipeline_analysis")
    )
    # Target Repositories
    target_repos: List[str] = field(default_factory=lambda: [
        "kubernetes/kubernetes",
        "pytorch/pytorch",
        "ansible/ansible",
        "scikit-learn/scikit-learn",
        "tensorflow/tensorflow",
        "apache/spark",
        "docker/compose",
        "prometheus/prometheus",
    ])
    # Logging
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )
    @property
    def headers(self) -> dict:
        h = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            h["Authorization"] = f"Bearer {self.github_token}"
        return h

    def get_logger(self, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, self.log_level.upper(), logging.INFO))
        return logger
