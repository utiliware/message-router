import os
import json

def lambda_handler(event, context):
    web_socket_url = os.environ.get("WEBSOCKET_URL", "")
    body = json.dumps({"webSocketUrl": web_socket_url})
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": body,
    }
