import json
import os

from openai import OpenAI

from app.utils.AppExceptions import AppBaseException
from app.utils.AppLogger import logger
from app.config import open_ai_api_key

OpenAiClient = OpenAI(
    api_key=open_ai_api_key
)

SYSTEM_PROMPT = """
You are a writing assistant.

Rewrite the user input in a cinematic, confident, calm, conversational tone inspired by classic Brad Pitt-style dialogue delivery.

Rules:
- Output must be between short and not exceed 100 words
- Return plain text only
- No markdown
- No bullet points
- No explanations
- Keep it natural and human
"""


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
            "content": SYSTEM_PROMPT
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
        model="gpt-5-mini",
        messages=messages,
        max_completion_tokens=120
    )

    return response.choices[0].message.content.strip()


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


def assistant_controller(event):
    """
    AWS Lambda entrypoint.
    """
    try:
        body = get_request_body(event)
        input_text = validate_input(body)
        messages = build_messages(input_text)
        output_text = generate_text(messages)
        return build_success_response(
            input_text=input_text,
            output_text=output_text
        )
    except Exception as error:
        raise AppBaseException(f"Error processing request: {error}")


if __name__ == "__main__":
    # For local testing
    test_event = {
        "body": json.dumps({
            "text": "Hey"
        })
    }
    response = assistant_controller(test_event)
    logger.info(response)