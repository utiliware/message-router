import json
import os
import uuid
import boto3
from aws_xray_sdk.core import patch_all, xray_recorder
patch_all()

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']  
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    print("Evento recibido desde SNS:", json.dumps(event))

    for record in event['Records']:
        sns_message = record['Sns']['Message']
        try:
            data = json.loads(sns_message)
            message = data.get("detail", {}).get("message", "Mensaje sin contenido")
        except Exception as e:
            print("Error al procesar mensaje SNS:", str(e))
            message = sns_message

        table.put_item(
            Item={
                'MessageId': str(uuid.uuid4()),
                'Message': message
            }
        )

    return {
        "statusCode": 200,
        "body": json.dumps({"status": "Mensaje almacenado en DynamoDB"})
    }
