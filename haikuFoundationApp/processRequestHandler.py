import json

from haikuFoundationApp.controllers.explorer.explore_controller import ExploreController
from haikuFoundationApp.controllers.international.international_controller import InternationalController
from haikuFoundationApp.controllers.home.home_controller import HomeController
from haikuFoundationApp.controllers.logout.logout_controller import LogoutController
from haikuFoundationApp.controllers.messages.messages_controller import MessagesController
from haikuFoundationApp.controllers.notifications.notifications_controller import NotificationsController
from haikuFoundationApp.controllers.profile.profile_controller import ProfileController
from haikuFoundationApp.controllers.saved.saved_controller import SavedController
from haikuFoundationApp.controllers.settings.settings_controller import SettingsController
from haikuFoundationApp.controllers.topics.topics_controller import TopicController
from haikuFoundationApp.controllers.trending.trending_controller import TrendingController
from haikuFoundationApp.controllers.write.write_controller import WriteController
from haikuFoundationApp.utils.authorizer import validate_jwt_token
from haikuFoundationApp.utils.lazy_loader import LazyLoadingRegister


class NotFoundController:

    def handle(self, event):
        return {
            "error": "Route not found"
        }


CONTROLLERS = LazyLoadingRegister({
    "/poems": HomeController,
    "/explore": ExploreController,
    "/topics": TopicController,
    "/saved": SavedController,
    "/international": InternationalController,
    "/write": WriteController,
    "/profile": ProfileController,
    "/trending": TrendingController,
    "/messages": MessagesController,
    "/settings": SettingsController,
    "/notifications": NotificationsController,
    "/logout": LogoutController,
})

FALLBACK = NotFoundController()


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
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,PATCH,DELETE",
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    print("EVENT:", event)
    http_method = (
        event.get("httpMethod", "")
        .upper()
    )
    if http_method == "OPTIONS":
      return build_response(200, {"message": "CORS preflight success"})
    body = parse_body(event)
    request_method = body.get("requestMethod")
    if not request_method:
      return build_response(400, {"error": "Missing requestMethod"})
    controller = CONTROLLERS.get(request_method, FALLBACK)
    handler = getattr(
        controller,
        http_method.lower(),
        None
    )
    if not handler:
      return build_response(405, {"error": f"{http_method} not supported for {request_method}"})
    user_claims = None
    if http_method in ("GET", "POST"):
      headers = event.get('headers', {}) or {}
      auth_header = headers.get('Authorization') or headers.get('authorization')
      try:
        user_claims = validate_jwt_token(auth_header)
      except Exception as e:
        return build_response(401, {"error": str(e)})
    controller_event = {
        "httpMethod": http_method,
        "route": request_method,
        "body": body,
        "headers": event.get("headers", {}),
      "user": user_claims or (
            event
            .get("requestContext", {})
            .get("authorizer")
        )
    }
    result = handler(controller_event)
    return build_response(200, result)
