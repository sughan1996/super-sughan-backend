from app.utils.AppExceptions import AppBaseException
from app.utils.AppLogger import logger


def home_controller(event):
    """
    AWS Lambda entrypoint for cooking-related requests.
    """
    try:
        return {
            "statusCode": 200,
            "body": "Home controller is under construction"
        }
    except Exception as error:
        raise AppBaseException(f"Error processing cooking request: {error}")
