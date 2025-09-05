import json
import os
import boto3

# Cliente SQS
sqs = boto3.client("sqs")
QUEUE_URL = os.environ.get("QUEUE_URL")

def lambda_handler(event, context):
    # Headers CORS comunes
    cors_headers = {
        "Access-Control-Allow-Origin": "*",  # Permite cualquier origen
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Methods": "OPTIONS,POST"
    }

    # ------------------------
    # Preflight request OPTIONS
    # ------------------------
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps({"message": "CORS preflight OK"})
        }

    # ------------------------
    # POST real
    # ------------------------
    if event.get("httpMethod") == "POST":
        try:
            body = json.loads(event.get("body", "{}"))

            # Caso 1: un solo mensaje
            if "message" in body:
                message = body["message"]
                sqs.send_message(
                    QueueUrl=QUEUE_URL,
                    MessageBody=json.dumps({"message": message})
                )
                return {
                    "statusCode": 200,
                    "headers": cors_headers,
                    "body": json.dumps({
                        "message": "Mensaje recibido y enviado a la cola",
                        "sentMessages": [message]
                    })
                }

            # Caso 2: múltiples mensajes
            elif "messages" in body and isinstance(body["messages"], list):
                messages = body["messages"]
                if not messages:
                    return {
                        "statusCode": 400,
                        "headers": cors_headers,
                        "body": json.dumps({"message": "La lista 'messages' no puede estar vacía"})
                    }

                # SQS solo soporta hasta 10 en send_message_batch
                batch = []
                responses = []
                for i, msg in enumerate(messages):
                    entry = {
                        "Id": str(i),
                        "MessageBody": json.dumps({"message": msg})
                    }
                    batch.append(entry)

                    if len(batch) == 10:  # Enviar en lotes de 10
                        res = sqs.send_message_batch(QueueUrl=QUEUE_URL, Entries=batch)
                        responses.append(res)
                        batch = []

                # Enviar los que faltan (<10)
                if batch:
                    res = sqs.send_message_batch(QueueUrl=QUEUE_URL, Entries=batch)
                    responses.append(res)

                return {
                    "statusCode": 200,
                    "headers": cors_headers,
                    "body": json.dumps({
                        "message": f"{len(messages)} mensajes recibidos y enviados a la cola",
                        "sentMessages": messages
                    })
                }

            # Ningún formato válido
            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps({"message": "Debes enviar 'message' o 'messages' (lista)"})
            }

        except Exception as e:
            return {
                "statusCode": 500,
                "headers": cors_headers,
                "body": json.dumps({"message": f"Error interno: {str(e)}"})
            }

    # ------------------------
    # Método no permitido
    # ------------------------
    return {
        "statusCode": 405,
        "headers": cors_headers,
        "body": json.dumps({"message": "Method Not Allowed"})
    }
