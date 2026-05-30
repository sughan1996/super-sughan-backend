from haikuFoundationApp.requester.postController import post_home_controller


class PoemsController:

    def get(self, event):
        return {
            "module": "HOME",
            "action": "GET"
        }

    def post(self, event):
        return post_home_controller(event)
