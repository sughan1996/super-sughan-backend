from __future__ import annotations
import random
import requests

GUARDIAN_API_KEY = "b1ec3d19-17a3-499c-822c-246cf2def0d0"
GUARDIAN_URL = "https://content.guardianapis.com/search"

GEOPOLITICS_QUERIES = [
    "geopolitics",
    "foreign policy",
    "international relations",
    "china",
    "russia",
    "ukraine",
    "middle east",
    "nato",
    "taiwan",
    "european union",
    "south china sea",
    "india china",
    "united nations",
]


def get_geopolitics_news(featured_count: int = 10) -> dict:
    params = {
        "api-key": GUARDIAN_API_KEY,
        "q": random.choice(GEOPOLITICS_QUERIES),
        "section": "world",
        "page-size": 50,
        "page": random.randint(1, 10),
        "show-fields": "trailText,thumbnail,byline",
        "order-by": "newest",
    }

    response = requests.get(
        GUARDIAN_URL,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    articles = data["response"]["results"]

    random.shuffle(articles)

    return {
        "category": "international",
        "count": min(featured_count, len(articles)),
        "articles": [
            {
                "id": article["id"],
                "title": article["webTitle"],
                "url": article["webUrl"],
                "published": article["webPublicationDate"],
                "section": article["sectionName"],
                "description": article.get("fields", {}).get("trailText"),
                "thumbnail": article.get("thumbnail"),
                "author": article.get("fields", {}).get("byline"),
            }
            for article in articles[:featured_count]
        ],
    }


class InternationalController:
    def get(self, event):
        return {
            "module": "FEATURED",
            "action": "GET"
        }

    def post(self, event):
        return get_geopolitics_news()




if __name__ == "__main__":
    news = InternationalController()
    print(news.post({"module": "INTERNATIONAL", "action": "POST"}))