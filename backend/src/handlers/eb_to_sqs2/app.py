import os
import json
import boto3
import uuid

from aws_xray_sdk.core import xray_recorder, patch_all
patch_all() 

sqs = boto3.client("sqs")
QUEUE_URL = os.environ["QUEUE_URL"]  # Inyeccion desde sam a queue 2


def lambda_handler(event, context):
    try:
        detail = event.get("detail", {})
        messages = detail.get("messages", [detail])  # soporte para enviar lista o uno solo

        if not isinstance(messages, list):
            messages = [messages]

        # Preparar los entries para send_message_batch (máx 10 por batch)
        batches = [
            messages[i:i+10] for i in range(0, len(messages), 10)
        ]

        all_responses = []
        for batch in batches:
            entries = []
            for idx, msg in enumerate(batch):
                if not isinstance(msg, str):
                    msg = json.dumps(msg, ensure_ascii=False)

                entries.append({
                    "Id": str(uuid.uuid4()),   # cada mensaje necesita un Id único en el batch
                    "MessageBody": msg
                })

            resp = sqs.send_message_batch(
                QueueUrl=QUEUE_URL,
                Entries=entries
            )
            all_responses.append(resp)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "ok": True,
                "batchesSent": len(all_responses),
                "results": all_responses
            }, ensure_ascii=False)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "ok": False,
                "error": str(e)
            }, ensure_ascii=False)
        }
