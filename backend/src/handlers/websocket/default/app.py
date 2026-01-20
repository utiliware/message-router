import json

def lambda_handler(event, context):
    print("Message Received by WebSocket:", json.dumps(event))
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Mensaje recibido"})
    }