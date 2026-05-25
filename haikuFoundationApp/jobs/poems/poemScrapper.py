from __future__ import annotations
from typing import Any
import requests
from boto3 import client

from haikuFoundationApp.utils.content_id_generator import generate_content_id
from haikuFoundationApp.dbmodels.poemsHandler import get_poem_values, create_poem
BASE_URL = "https://poetrydb.org"

class PoetryDBClient:

    def __init__(
            self,
            timeout: int = 10,
    ) -> None:
        self.timeout = timeout
        self.session = requests.Session()

    def _get(self, endpoint: str) -> list[dict[str, Any]]:
        url = f"{BASE_URL}/{endpoint}"

        response = self.session.get(
            url,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict) and "reason" in data:
            raise ValueError(data["reason"])

        return data

    def get_authors(self) -> list[str]:
        """
        Get all authors
        """
        url = f"{BASE_URL}/author"
        response = self.session.get(
            url,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()

        return data.get("authors", [])

    def get_poems_by_author(
            self,
            author: str,
    ) -> list[dict[str, Any]]:
        """
        Example:
        get_poems_by_author("Emily Dickinson")
        """
        author = author.replace(" ", "%20")

        return self._get(f"author/{author}")

    def get_poem_by_title(
            self,
            title: str,
    ) -> list[dict[str, Any]]:
        """
        Example:
        get_poem_by_title("Ozymandias")
        """
        title = title.replace(" ", "%20")

        return self._get(f"title/{title}")

    def search_by_line(
            self,
            line: str,
    ) -> list[dict[str, Any]]:
        """
        Search poems containing text
        """
        line = line.replace(" ", "%20")

        return self._get(f"lines/{line}")

    @staticmethod
    def _format_content(lines: list[str]) -> str:
        """Format every poem line into newline-separated content."""
        return "\n".join(line.strip() for line in lines if line.strip())

    @classmethod
    def _normalize_poem(cls, poem: dict[str, Any]) -> dict[str, str]:
        """Return only the fields needed by the app."""
        return {
            "title": poem.get("title", ""),
            "body": cls._format_content(poem.get("lines", [])),
            "author": poem.get("author", ""),
        }

    def random_poems(
            self,
            count: int = 1,
    ) -> list[dict[str, str]]:
        """
        Get random poems with title, formatted content, and author.
        """
        return [self._normalize_poem(poem) for poem in self._get(f"random/{count}")]

    @staticmethod
    def format_poem(
            poem: dict[str, Any],
    ) -> str:
        """
        Convert poem JSON to readable text
        """
        title = poem.get("title", "")
        author = poem.get("author", "")
        content = poem.get("content") or PoetryDBClient._format_content(poem.get("lines", []))

        return f"{title}\nby {author}\n\n{content}"


    def bootstrap_poems(self, user_id= 'sughanrichardson'):
        client = PoetryDBClient()
        poem = client.random_poems(count=1)
        title = poem[0]['title']
        body = poem[0]['body']
        author = poem[0]['author']
        status = 'live'
        tags = ["haiku", "random"]
        content_id = generate_content_id(title, body, author)
        try:
            out = create_poem(content_id=content_id, user_id=user_id,
                              title=title, body=body, author=author,
                              tags=tags, status=status)
            return f"Created: {out.keys()}"
        except Exception as error:
            raise error


if __name__ == "__main__":
    client = PoetryDBClient()
    for count in range(0,10):
        print(client.bootstrap_poems(user_id='sughanrichardson'))


