import time
import requests
from typing import Optional, List, Dict, Any
from config.settings import Settings

class BaseCollector:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.logger = self.settings.get_logger(self.__class__.__name__)
        self.session = requests.Session()
        self.session.headers.update(self.settings.headers)

    def _make_request(self, url: str) -> Optional[requests.Response]:
        try:
            response = self.session.get(url, timeout=self.settings.api_timeout)
            if response.status_code == 403:
                self.logger.warning("Rate limit hit. Sleeping %ds...", self.settings.rate_limit_sleep)
                time.sleep(self.settings.rate_limit_sleep)
                response = self.session.get(url, timeout=self.settings.api_timeout)

            if response.status_code != 200:
                self.logger.error("HTTP %d for %s", response.status_code, url)
                return None
            return response
        except requests.exceptions.Timeout:
            self.logger.error("Request timeout: %s", url)
            return None
        except requests.exceptions.ConnectionError:
            self.logger.error("Connection error: %s", url)
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error("Request failed: %s - %s", url, str(e))
            return None

    def _paginated_fetch(self, url_template: str, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        max_pages = max_pages or self.settings.max_api_pages
        all_items = []
        page = 1
        while page <= max_pages:
            url = url_template.format(
                per_page=self.settings.per_page,
                page=page
            )
            self.logger.debug("Fetching page %d: %s", page, url)
            response = self._make_request(url)
            if response is None:
                break
            data = response.json()

            # GitHub returns dict for errors, list for valid data
            if not data or isinstance(data, dict):
                break
            all_items.extend(data)
            self.logger.info("Page %d: fetched %d items (total: %d)", page, len(data), len(all_items))
            if len(data) < self.settings.per_page:
                break
            page += 1
        return all_items

    def _single_fetch(self, url: str) -> Dict[str, Any]:
        response = self._make_request(url)
        if response is None:
            return {}
        return response.json()

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
