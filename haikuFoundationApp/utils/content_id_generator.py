import hashlib
import re


def normalize(value: str) -> str:
    """
    Normalize text before hashing.
    """
    value = value.strip().lower()

    # collapse whitespace
    value = re.sub(r"\s+", " ", value)

    return value


def generate_content_id(
    title: str,
    body: str,
    author: str,
) -> str:
    payload = "|".join([
        normalize(title),
        normalize(author),
        normalize(body),
    ])

    digest = hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()

    return f"CONTENT#{digest[:20]}"
