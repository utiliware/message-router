import os
import json
import boto3
import logging
from datetime import datetime
from uuid import uuid4
from decimal import Decimal
from boto3.dynamodb.types import TypeDeserializer

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

s3 = boto3.client('s3')
deserializer = TypeDeserializer()
BUCKET = os.environ.get('S3_BUCKET')


def _convert_decimals(obj):
    if isinstance(obj, dict):
        return {k: _convert_decimals(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_decimals(v) for v in obj]
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    return obj


def _deserialize_map(dynamo_map):
    """Converts a DynamoDB map (NewImage o Keys) to a dict python"""
    return {k: deserializer.deserialize(v) for k, v in dynamo_map.items()}


def _make_id_from_keys(keys_map):
    """Builds an id readable fro the Keys structure of the event"""
    if not keys_map:
        return None
    parts = []
    for k, v in keys_map.items():
        val = deserializer.deserialize(v)
        val = _convert_decimals(val)
        parts.append(f"{k}-{val}")
    return "_".join(parts)


def lambda_handler(event, context):
    LOGGER.info("Received event with %d records", len(event.get('Records', [])))
    for record in event.get('Records', []):
        try:
            LOGGER.info("Record: %s", json.dumps(record, default=str))
            ev_type = record.get('eventName')
            ddb = record.get('dynamodb', {})

            # Prefer NewImage (INSERT / MODIFY). If no NewImage, try with Keys.
            item = {}
            if 'NewImage' in ddb and ddb['NewImage'] is not None:
                item = _deserialize_map(ddb['NewImage'])
                item = _convert_decimals(item)
            else:
                # Could be REMOVE (no NewImage) -> obtains the Keys
                keys = ddb.get('Keys')
                if keys:
                    item = {k: deserializer.deserialize(v) for k, v in keys.items()}
                    item = _convert_decimals(item)

            # Common ways to extract an id:
            item_id = None
            if isinstance(item, dict):
                item_id = item.get('id') or item.get('Id') or item.get('messageId') or item.get('MessageId')

            # If there is no id, create it from the existing Keys:
            if not item_id:
                item_id = _make_id_from_keys(ddb.get('Keys', {}))

            # Last resource: uuid
            if not item_id:
                item_id = str(uuid4())

            # Builds a content to save: if it is REMOVE, mark eliminated
            obj = {
                'eventType': ev_type,
                'item': item
            }

            ts = datetime.utcnow().isoformat().replace(":", "_")
            key = f"{item_id}_{ts}.json"

            s3.put_object(
                Bucket=BUCKET,
                Key=key,
                Body=json.dumps(obj, default=str).encode('utf-8'),
                ContentType='application/json'
            )
            LOGGER.info("Saved to s3://%s/%s", BUCKET, key)

        except Exception as e:
            LOGGER.exception("Error processing record")
            raise
    
    # Retorno con CORS para API Gateway (aunque normalmente no se usa)
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps({"status": "ok"})
    }
