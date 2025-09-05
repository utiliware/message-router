import os
import json
import uuid
import boto3
from boto3.dynamodb.types import TypeDeserializer

s3 = boto3.client("s3")
BUCKET = os.getenv("S3_BUCKET")
deser = TypeDeserializer()

def _from_ddb_image(img):
    return {k: deser.deserialize(v) for k, v in img.items()}

def lambda_handler(event, context):
    for record in event.get("Records", []):
        if record.get("eventName") not in ("INSERT", "MODIFY"):
            continue
        new_image = record.get("dynamodb", {}).get("NewImage", {})
        doc = _from_ddb_image(new_image) if new_image else {}

        key = f"ddb-events/{doc.get('MessageId', str(uuid.uuid4()))}.json"
        s3.put_object(Bucket=BUCKET, Key=key, Body=json.dumps(doc).encode("utf-8"))

    return {"status": "ok"}
