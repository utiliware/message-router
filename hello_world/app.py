import json
import boto3
import os

sqs = boto3.client('sqs')
QUEUE_URL = os.environ.get('QUEUE_URL')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    message = body.get('message', 'Hello from API')

    response = sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=message
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "messageId": response['MessageId'],
            "status": "Message sent"
        })
    }