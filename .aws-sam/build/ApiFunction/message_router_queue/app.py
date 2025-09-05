# message_router_queue/app.py
import os
import json
import boto3

sqs = boto3.client("sqs")
QUEUE_URL = os.getenv("QUEUE_URL")

def lambda_handler(event, context):
    # Cuerpo recibido por API Gateway (proxy)
    try:
        body = json.loads(event.get("body") or "{}")
    except Exception:
        body = {"message": str(event.get("body"))}

    resp = sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(body))

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"ok": True, "sqsMessageId": resp.get("MessageId")})
    }
