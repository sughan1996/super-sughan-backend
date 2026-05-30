from __future__ import annotations

import random
import requests
from typing import Any, Dict, List


GUARDIAN_API_KEY = "b1ec3d19-17a3-499c-822c-246cf2def0d0"
GUARDIAN_URL = "https://content.guardianapis.com/search"

HEALTH_QUERIES = [
    "health",
    "medicine",
    "public health",
    "mental health",
    "wellness",
    "disease",
]


def fetch_guardian_health_news(
    featured_count: int = 10,
    page_size: int = 50,
) -> Dict[str, Any]:
    """
    Fetch health-related news from The Guardian API.
    """

    params = {
        "api-key": GUARDIAN_API_KEY,
        "q": random.choice(HEALTH_QUERIES),
        "section": "health",  # more relevant than "world" for health topics
        "page-size": page_size,
        "page": random.randint(1, 5),
        "show-fields": "trailText,thumbnail,byline",
        "order-by": "newest",
    }

    response = requests.get(GUARDIAN_URL, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    results = data.get("response", {}).get("results", [])

    random.shuffle(results)

    return {
        "category": "health",
        "count": min(featured_count, len(results)),
        "articles": [_parse_article(a) for a in results[:featured_count]],
    }


def _parse_article(article: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Guardian article format."""
    fields = article.get("fields", {})

    return {
        "id": article.get("id"),
        "title": article.get("webTitle"),
        "url": article.get("webUrl"),
        "published": article.get("webPublicationDate"),
        "section": article.get("sectionName"),
        "description": fields.get("trailText"),
        "thumbnail": fields.get("thumbnail"),
        "author": fields.get("byline"),
    }


class HealthNewsController:
    def get(self, event: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "module": "HEALTH_NEWS",
            "action": "GET",
        }

    def post(self, event: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return fetch_guardian_health_news()


if __name__ == "__main__":
    controller = HealthNewsController()
    result = controller.post()

    print(result)