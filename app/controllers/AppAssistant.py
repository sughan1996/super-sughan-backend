import json

from app.utils.AppExceptions import AppBaseException
from external.AppOpenAi import (get_request_body, validate_input,
                                build_messages, generate_text, build_success_response)
from utils.AppLogger import logger


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
            "text": "Hey Brad, what's the best way to handle a tough situation?"
        })
    }
    response = assistant_controller(test_event)
    logger.info(response)