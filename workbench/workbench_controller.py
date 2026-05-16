import json
from app.controllers.AppProcessRequest import process_request_controller
from app.utils.AppLogger import logger

def check_assistant(text=None):
    assistant = {
        "rawPath": "/assistant",
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
        "body": json.dumps({
            "text": text
        })
    }
    response = process_request_controller(assistant, None)
    return response

def check_home():
    home = {
        "rawPath": "/home",
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }
    response = process_request_controller(home, None)
    return response

def check_error():
    error = {
        "rawPath": "/error",
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }
    response = process_request_controller(error, None)
    return response

def check_doctor():
    doctor = {
        "rawPath": "/doctor",
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }
    response = process_request_controller(doctor, None)
    return response


if __name__ == "__main__":
    logger.info(check_assistant("suck my dick"))

