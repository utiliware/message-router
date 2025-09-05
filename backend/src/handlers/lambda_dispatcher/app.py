import os
import json
import boto3

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
            'Source': 'MyApp',            # Debe coincidir exactamente con EventPattern
            'DetailType': 'PlainText',          # Puedes cambiar el tipo si quieres
            'Detail': json.dumps(data),              # El contenido del evento
            'EventBusName': 'default'                # Bus default
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
