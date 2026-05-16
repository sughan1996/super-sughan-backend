import json

from app.utils.AppLogger import logger
from app.utils.AppExceptions import AppBaseException

from app.controllers.AppHome import home_controller
from app.controllers.AppArcade import arcade_controller
from app.controllers.AppEntertainment import entertainment_controller
from app.controllers.AppDoctor import doctor_controller
from app.controllers.AppAssistant import assistant_controller


# =========================================================
# Response Helper
# =========================================================
def response(status_code: int, body: dict):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }


# =========================================================
# Function Map
# Route -> Method -> Controller
# =========================================================
FUNC_MAP = {
    "/home": {
        "GET": home_controller,
        "POST": home_controller,
        "PUT": home_controller,
        "PATCH": home_controller,
        "DELETE": home_controller,
    },

    "/arcade": {
        "GET": arcade_controller,
        "POST": arcade_controller,
        "PUT": arcade_controller,
        "PATCH": arcade_controller,
        "DELETE": arcade_controller,
    },

    "/entertainment": {
        "GET": entertainment_controller,
        "POST": entertainment_controller,
        "PUT": entertainment_controller,
        "PATCH": entertainment_controller,
        "DELETE": entertainment_controller,
    },

    "/doctor": {
        "GET": doctor_controller,
        "POST": doctor_controller,
        "PUT": doctor_controller,
        "PATCH": doctor_controller,
        "DELETE": doctor_controller,
    },

    "/assistant": {
        "GET": assistant_controller,
        "POST": assistant_controller,
        "PUT": assistant_controller,
        "PATCH": assistant_controller,
        "DELETE": assistant_controller,
    }
}


# =========================================================
# Lambda Handler
# =========================================================
def process_request_controller(event, context):
    try:
        logger.info(f"Incoming Event: {json.dumps(event)}")

        # API Gateway v2
        path = event.get("rawPath") or event.get("path")

        method = (
            event.get("requestContext", {})
            .get("http", {})
            .get("method")
        )

        logger.info(f"Path={path}, Method={method}")

        # Validate Route
        route_methods = FUNC_MAP.get(path)

        if not route_methods:
            return response(
                404,
                {"message": f"Invalid route: {path}"}
            )

        # Validate HTTP Method
        controller = route_methods.get(method)

        if not controller:
            return response(
                405,
                {
                    "message": (
                        f"Method {method} not allowed for route {path}"
                    )
                }
            )

        # Execute Controller
        return controller(event)

    except AppBaseException as error:
        logger.exception("Application Exception")

        return response(
            400,
            {
                "message": str(error)
            }
        )

    except Exception as error:
        logger.exception("Unhandled Exception")

        return response(
            500,
            {
                "message": "Internal Server Error",
                "error": str(error)
            }
        )

