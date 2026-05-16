import json
import random

from openai import OpenAI

from config import open_ai_api_key, open_ai_model
from prompts.AppBradPittPrompts import BRAD_PITT_PROMPT, BRAD_PITT_NO_RESPONSE
from utils.AppExceptions import AppBaseException
from utils.AppLogger import logger

OpenAiClient = OpenAI(
    api_key=open_ai_api_key
)


def get_request_body(event: dict) -> dict:
    """
    Extract request body from Lambda event.
    """
    return json.loads(event.get("body", "{}"))


def validate_input(body: dict) -> str:
    """
    Validate incoming text.
    """
    text = body.get("text")
    if len(text) > 150:
        raise AppBaseException("Input text exceeds 150 characters")
    if not text:
        raise AppBaseException("Missing 'text'")
    return text.strip()


def build_messages(user_text: str) -> list:
    """
    Build OpenAI chat messages.
    """
    return [
        {
            "role": "system",
            "content": BRAD_PITT_PROMPT
        },
        {
            "role": "user",
            "content": user_text
        }
    ]


def generate_text(messages: list) -> str:
    """
    Call GPT-5 Mini and generate response text.
    """

    response = OpenAiClient.chat.completions.create(
        model=open_ai_model,
        messages=messages,
        max_completion_tokens=120,
    )

    logger.info(
        "OpenAI response received successfully"
    )

    message = response.choices[0].message
    content = message.content
    if not content:
        logger.error(
            "OpenAI returned empty content"
        )
        return random.choice(BRAD_PITT_NO_RESPONSE)
    return content.strip()


def build_success_response(
        input_text: str,
        output_text: str
) -> dict:
    """
    Build successful API response.
    """
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "input": input_text,
            "output": output_text
        })
    }


def build_error_response(
        status_code: int,
        error_message: str
) -> dict:
    """
    Build error response.
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "error": error_message
        })
    }
