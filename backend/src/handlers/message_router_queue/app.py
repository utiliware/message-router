import json
import os
import boto3
from aws_xray_sdk.core import xray_recorder, patch_all
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType

patch_all()

# Inicializar Powertools
logger = Logger()
tracer = Tracer()
metrics = Metrics()

# Cliente SQS
sqs = boto3.client("sqs")
QUEUE_URL = os.environ.get("QUEUE_URL")

# Procesador batch de Powertools
processor = BatchProcessor(event_type=EventType.SQS)  # aunque también puedes usarlo manualmente

@tracer.capture_method
def send_batch(messages):
    """
    Envía mensajes a SQS en lotes de hasta 10.
    """
    results = []
    batch = []

    for i, msg in enumerate(messages):
        entry = {
            "Id": str(i),
            "MessageBody": json.dumps({"message": msg})
        }
        batch.append(entry)

        if len(batch) == 10:
            res = sqs.send_message_batch(QueueUrl=QUEUE_URL, Entries=batch)
            logger.info(f"Lote enviado con {len(batch)} mensajes")
            results.append(res)
            batch = []

    if batch:
        res = sqs.send_message_batch(QueueUrl=QUEUE_URL, Entries=batch)
        logger.info(f"Lote enviado con {len(batch)} mensajes")
        results.append(res)

    return results

@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Methods": "OPTIONS,POST"
    }

    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps({"message": "CORS preflight OK"})
        }

    if event.get("httpMethod") == "POST":
        try:
            body = json.loads(event.get("body", "{}"))

            # Caso 1: un solo mensaje
            if "message" in body:
                send_batch([body["message"]])
                return {
                    "statusCode": 200,
                    "headers": cors_headers,
                    "body": json.dumps({"message": "Mensaje recibido y enviado a la cola"})
                }

            # Caso 2: múltiples mensajes
            elif "messages" in body and isinstance(body["messages"], list):
                if not body["messages"]:
                    return {
                        "statusCode": 400,
                        "headers": cors_headers,
                        "body": json.dumps({"message": "La lista 'messages' no puede estar vacía"})
                    }

                send_batch(body["messages"])
                return {
                    "statusCode": 200,
                    "headers": cors_headers,
                    "body": json.dumps({
                        "message": f"{len(body['messages'])} mensajes recibidos y enviados a la cola"
                    })
                }

            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps({"message": "Debes enviar 'message' o 'messages' (lista)"})
            }

        except Exception as e:
            logger.exception("Error al procesar POST")
            return {
                "statusCode": 500,
                "headers": cors_headers,
                "body": json.dumps({"message": f"Error interno: {str(e)}"})
            }

    return {
        "statusCode": 405,
        "headers": cors_headers,
        "body": json.dumps({"message": "Method Not Allowed"})
    }
