import os
import json
import boto3
from datetime import datetime

s3 = boto3.client('s3')
bucket = os.environ['S3_BUCKET']

def lambda_handler(event, context):
    # For each registration in the Stream
    for record in event.get('Records', []):
        if record['eventName'] == 'INSERT':
            new_img = record['dynamodb']['NewImage']
            # Convert DynamoDB JSON to normal JSON
            item = { k: deserialize(v) for k,v in new_img.items() }

            # Name of the object: id + timestamp
            key = f"{item['id']}_{datetime.utcnow().isoformat()}.json"
            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=json.dumps(item).encode('utf-8'),
                ContentType='application/json'
            )

def deserialize(attribute):
    # DynamoDB JSON → Python value
    if 'S' in attribute:
        return attribute['S']
    if 'N' in attribute:
        return int(attribute['N'])
    return None
