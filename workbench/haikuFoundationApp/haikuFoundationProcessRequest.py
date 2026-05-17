import json


# ----------------------------
# Controllers
# ----------------------------

class HomeController:
    def get(self, event):
        return {"module": "HOME", "action": "GET"}

    def post(self, event):
        return {"module": "HOME", "action": "POST"}


class ExploreController:
    def get(self, event):
        return {"module": "EXPLORE", "action": "GET"}


class MessagesController:
    def get(self, event):
        return {"module": "MESSAGES", "action": "GET"}


class LogoutController:
    def get(self, event):
        return {"module": "LOGOUT", "action": "GET"}


class LoginController:
    def get(self, event):
        return {"module": "LOGIN", "action": "GET"}


class LoginController:
    def post(self, event):
        return {"module": "LOGIN", "action": "POST"}


class NotFoundController:
    def handle(self, event):
        return {"error": "Route not found"}


# ----------------------------
# Controller registry
# ----------------------------

CONTROLLERS = {
    "/home": HomeController(),
    "/explore": ExploreController(),
    "/login": LoginController(),
}

FALLBACK = NotFoundController()


# ----------------------------
# Helpers
# ----------------------------

def parse_body(event):
    body = event.get("body")
    if not body:
        return {}

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {}


def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body)
    }


# ----------------------------
# Lambda handler
# ----------------------------

def lambda_handler(event, context):
    print("event:", event)

    http_method = (event.get("httpMethod") or "").upper()

    body = parse_body(event)

    # THIS is your real router key
    request_method = body.get("requestMethod")

    if not request_method:
        return response(400, {"error": "Missing requestMethod in body"})

    controller = CONTROLLERS.get(request_method, FALLBACK)

    # map HTTP method → function
    handler = getattr(controller, http_method.lower(), None)

    if not handler:
        return response(405, {
            "error": f"HTTP method {http_method} not supported for {request_method}"
        })

    result = handler({
        "httpMethod": http_method,
        "route": request_method,
        "body": body,
        "headers": event.get("headers", {}),
        "user": event.get("requestContext", {}).get("authorizer")
    })

    return response(200, result)


if __name__ == "__main__":
    test_event = {
        "httpMethod": "POST",
        "body": json.dumps({
            "requestMethod": "/home"
        })
    }
    print(lambda_handler(test_event, None))