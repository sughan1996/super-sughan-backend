import json

import requests

from haikuFoundationApp.processRequestHandler import lambda_handler

url = "https://cognito-idp.us-east-1.amazonaws.com/"
payload = "{\n  \"AuthFlow\": \"USER_PASSWORD_AUTH\",\n  \"ClientId\": \"3q34c48o6fvaqbdmssvuovu86k\",\n  \"AuthParameters\": {\n    \"USERNAME\": \"samsonbabuji\",\n    \"PASSWORD\": \"Samsonbabuji@1967!\"\n  }\n}"
headers = {
    'Content-Type': 'application/x-amz-json-1.1',
    'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth'
}

response = requests.request("POST", url, headers=headers, data=payload).json()

access_token = response['AuthenticationResult']['AccessToken']
event_0 = {
    "httpMethod": "POST",
    "body": json.dumps({"requestMethod": "/home", "userId": "samsonbabuji"}),
    "headers": {
        "Authorization": 'Bearer ' + access_token}}
event_1 = {
    "httpMethod": "POST",
    "body": json.dumps({"requestMethod": "/topics", "userId": "samsonbabuji"}),
    "headers": {
        "Authorization": 'Bearer ' + access_token}}

event_2 = {
    "httpMethod": "POST",
    "body": json.dumps({"requestMethod": "/explore", "userId": "samsonbabuji"}),
    "headers": {
        "Authorization": 'Bearer ' + access_token}}

if __name__ == "__main__":
    print(lambda_handler(event_0, None))
    # print(lambda_handler(event_1, None))
    # print(lambda_handler(event_2, None))

