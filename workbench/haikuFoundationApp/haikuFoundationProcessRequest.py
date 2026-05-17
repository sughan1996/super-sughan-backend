import json


# =========================================================
# Controllers
# =========================================================

class HomeController:

    def get(self, event):
        return {
            "module": "HOME",
            "action": "GET"
        }

    def post(self, event):
        return {
            "module": "HOME",
            "action": "POST"
        }


class ExploreController:

    def get(self, event):
        return {
            "module": "EXPLORE",
            "action": "GET"
        }

    def post(self, event):
        return {
            "module": "EXPLORE",
            "action": "POST"
        }


class MessagesController:

    def get(self, event):
        return {
            "module": "MESSAGES",
            "action": "GET"
        }


class LogoutController:

    def get(self, event):
        return {
            "module": "LOGOUT",
            "action": "GET"
        }


class LoginController:

    def get(self, event):
        return {
            "module": "LOGIN",
            "action": "GET"
        }

    def post(self, event):
        return {
            "module": "LOGIN",
            "action": "POST"
        }


class NotFoundController:

    def handle(self, event):
        return {
            "error": "Route not found"
        }


# =========================================================
# Controller Registry
# =========================================================

CONTROLLERS = {
    "/home": HomeController(),
    "/explore": ExploreController(),
    "/login": LoginController(),
    "/messages": MessagesController(),
    "/logout": LogoutController(),
}

FALLBACK = NotFoundController()


# =========================================================
# Helpers
# =========================================================

def parse_body(event):

    body = event.get("body")

    if not body:
        return {}

    try:
        return json.loads(body)

    except Exception as e:
        print("JSON parse error:", e)
        return {}


def build_response(status, body):

    return {
        "statusCode": status,

        "headers": {

            # ---------------- CORS ----------------
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,PATCH,DELETE",

            # ---------------- CONTENT ----------------
            "Content-Type": "application/json"
        },

        "body": json.dumps(body)
    }


# =========================================================
# Lambda Handler
# =========================================================

def lambda_handler(event, context):
    print("EVENT:", event)
    http_method = (
        event.get("httpMethod", "")
        .upper()
    )

    # =====================================================
    # HANDLE CORS PREFLIGHT
    # =====================================================

    if http_method == "OPTIONS":

        return build_response(
            200,
            {
                "message": "CORS preflight success"
            }
        )

    # =====================================================
    # PARSE BODY
    # =====================================================

    body = parse_body(event)


    # =====================================================
    # ROUTE
    # =====================================================

    request_method = body.get("requestMethod")

    if not request_method:

        return build_response(
            400,
            {
                "error": "Missing requestMethod"
            }
        )

    controller = CONTROLLERS.get(
        request_method,
        FALLBACK
    )

    # =====================================================
    # METHOD RESOLUTION
    # =====================================================

    handler = getattr(
        controller,
        http_method.lower(),
        None
    )

    if not handler:

        return build_response(
            405,
            {
                "error": f"{http_method} not supported for {request_method}"
            }
        )

    # =====================================================
    # EXECUTE CONTROLLER
    # =====================================================

    controller_event = {

        "httpMethod": http_method,

        "route": request_method,

        "body": body,

        "headers": event.get("headers", {}),

        "user": (
            event
            .get("requestContext", {})
            .get("authorizer")
        )
    }

    result = handler(controller_event)

    # =====================================================
    # SUCCESS RESPONSE
    # =====================================================

    return build_response(
        200,
        result
    )


# =========================================================
# Local Test
# =========================================================


if __name__ == "__main__":
    # For local testing
    test_event = {
        "httpMethod": "POST",
        "body": json.dumps({
            "requestMethod": "/home"
        })
    }
    response = lambda_handler(test_event, None)
    print(response)