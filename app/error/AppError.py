from app.utils.AppExceptions import AppBaseException
from app.utils.AppLogger import logger


def error_controller(event):
    """
    AWS Lambda entrypoint for cooking-related requests.
    """
    try:
        path = event.get("path", None)
        return {
            "statusCode": 200,
            "path": path,
            "body": "Login Error"
        }
    except Exception as error:
        raise AppBaseException(f"Error processing cooking request: {error}")
