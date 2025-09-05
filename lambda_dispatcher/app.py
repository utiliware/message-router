import os
import json
import boto3

events = boto3.client("events")
BUS_NAME = os.getenv("EVENT_BUS_NAME", "default")

def lambda_handler(event, context):
    entries = []

    for record in event.get("Records", []):
        body = record.get("body", "")
        try:
            parsed = json.loads(body)  # si ya viene JSON
        except Exception:
            parsed = {"message": body}

        detail = {
            **(parsed if isinstance(parsed, dict) else {"message": str(parsed)}),
            "sqsMessageId": record.get("messageId"),
            "timestamp": record.get("attributes", {}).get("SentTimestamp")
        }

        entries.append({
            "Source": "MyApp",
            "DetailType": "PlainText",
            "Detail": json.dumps(detail),
            "EventBusName": BUS_NAME
        })

    if not entries:
        return {"status": "no-records"}

    resp = events.put_events(Entries=entries)
    return {"status": "ok", "failed": resp.get("FailedEntryCount", 0), "resp": resp}
