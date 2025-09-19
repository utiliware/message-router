import os
import json
import boto3

from aws_xray_sdk.core import xray_recorder, patch_all
patch_all() 

# Cliente de EventBridge
eventbridge = boto3.client('events')

def lambda_handler(event, context):
    print("=== LambdaDispatcher recibido ===")
    print(json.dumps(event, indent=2))

    entries = []

    for record in event.get('Records', []):
        raw_body = record["body"]
        print("Raw body de SQS:", raw_body)

        # Convertir a JSON si es posible, si no enviar como texto plano
        try:
            data = json.loads(raw_body) #Convertido a dict
        except json.JSONDecodeError:
            print("No es JSON, enviando como texto plano")
            data = {"message": raw_body}

        # Crear el evento para EventBridge
        entries.append({
            'Source': 'my.app.messages',           # debe coincidir con EventPattern.source
            'DetailType': 'MessageReceived',       # debe coincidir con EventPattern.detail-type
            'Detail': json.dumps(data, ensure_ascii=False),  # string con JSON
            'EventBusName': os.environ.get('EVENT_BUS_NAME', 'default')
        })


    if entries:
        response = eventbridge.put_events(Entries=entries)
        print("EventBridge put_events response:", json.dumps(response, indent=2))

        # Revisar si hubo errores
        if response.get('FailedEntryCount', 0) > 0:
            print("Algunos eventos fallaron al publicarse:", response.get('Entries', []))

    # Retorno con CORS
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps({"status": "done"})
    }
