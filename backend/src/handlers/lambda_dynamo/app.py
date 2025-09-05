import json
import os
import uuid
import boto3

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

    # Retorno con CORS
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps({"status": "Mensaje almacenado en DynamoDB"})
    }