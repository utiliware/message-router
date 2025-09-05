import os
import json
import uuid
import time
import boto3

dynamodb = boto3.resource("dynamodb")
TABLE = dynamodb.Table(os.getenv("TABLE_NAME", "MessagesTable"))

def lambda_handler(event, context):
    # Evento de SNS (records)
    for rec in event.get("Records", []):
        sns_msg = rec.get("Sns", {}).get("Message", "{}")
        try:
            payload = json.loads(sns_msg)
        except Exception:
            payload = {"message": sns_msg}

        item = {
            "MessageId": str(uuid.uuid4()),
            "ReceivedAt": int(time.time()),
            "Payload": payload
        }
        TABLE.put_item(Item=item)

    return {"status": "ok"}
