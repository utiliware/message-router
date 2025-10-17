import boto3
import json
import redis
import os
from datetime import datetime

# Clientes AWS
s3_client = boto3.client('s3')
bedrock_client = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')

# Variables de entorno Valkey
VALKEY_HOST = os.environ.get("VALKEY_HOST")
VALKEY_PORT = int(os.environ.get("VALKEY_PORT", 6379))

# WebSocket config
WEBSOCKET_ENDPOINT = os.environ.get("WEBSOCKET_ENDPOINT")
CONNECTIONS_TABLE = os.environ.get("CONNECTIONS_TABLE")

table = dynamodb.Table(CONNECTIONS_TABLE)


# Conexión global (para que se reutilice entre invocaciones)
valkey_client = redis.StrictRedis(
    host=VALKEY_HOST,
    port=VALKEY_PORT,
    decode_responses=True
)

def lambda_handler(event, context):
    # --- Extraer el mensaje de SNS ---
    sns_message = event['Records'][0]['Sns']['Message']
    s3_event = json.loads(sns_message)

    # --- Obtener bucket y key del evento S3 ---
    record = s3_event['Records'][0]['s3']
    bucket_name = record['bucket']['name']
    object_key = record['object']['key']

    # --- Leer contenido del objeto S3 ---
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    content = response['Body'].read().decode('utf-8')
    obj = json.loads(content)
    message_text = obj.get("item", {}).get("Message", "")

    # --- Construir prompt ---
    prompt = f"What's the meaning of '{message_text}'?"

    # --- Verificar si ya existe en cache ---
    cached_response = valkey_client.get(prompt)
    if cached_response:
        print("Cache hit:", cached_response)
        _broadcast_websocket(prompt, cached_response, "cache")
        return {
            "statusCode": 200,
            "body": json.dumps({
                "prompt": prompt,
                "response": cached_response,
                "source": "cache"
            })
        }

    # --- Llamar a Bedrock ---
    bedrock_response = bedrock_client.invoke_model(
        modelId="amazon.titan-text-express-v1",
        body=json.dumps({"inputText": prompt}),
        contentType="application/json"
    )

    result = json.loads(bedrock_response['body'].read())

    # Extrae correctamente el texto del resultado
    response_text = "No response"
    if "results" in result and len(result["results"]) > 0:
        response_text = result["results"][0].get("outputText", "No response")

    # --- Guardar en cache ---
    valkey_client.set(prompt, response_text)
    valkey_client.set(f"prompt:{datetime.utcnow().isoformat()}", prompt)

    print("Stored prompt:", prompt)
    print("Bedrock result:", response_text)

    # --- Presentar en Frontend con WebSocket ---
    _broadcast_websocket(prompt, response_text, "bedrock")


    return {
        "statusCode": 200,
        "body": json.dumps({
            "prompt": prompt,
            "response": response_text,
            "source": "bedrock"
        })
    }

def _broadcast_websocket(prompt, response, source):
    """Envía el resultado a todas las conexiones activas del WebSocket."""
    print("Debug entra a _broadcast_websocket")
    ws_client = boto3.client("apigatewaymanagementapi", endpoint_url=WEBSOCKET_ENDPOINT)

    payload = json.dumps({
        "prompt": prompt,
        "response": response,
        "source": source,
        "timestamp": datetime.utcnow().isoformat()
    })

    # Leer todas las conexiones de la tabla DynamoDB
    try:
        connections = table.scan().get('Items', [])
    except Exception as e:
        print(f"Error al leer ConnectionsTable: {e}")
        return

    print(f"🔌 Enviando mensaje a {len(connections)} conexiones")

    for conn in connections:
        connection_id = conn.get('connectionId')
        try:
            ws_client.post_to_connection(
                ConnectionId=connection_id,
                Data=payload.encode('utf-8')
            )
        except ws_client.exceptions.GoneException:
            print(f"Conexión caducada: {connection_id}")
            _remove_stale_connection(connection_id)
        except Exception as e:
            print(f"Error enviando a {connection_id}: {e}")


def _remove_stale_connection(connection_id):
    """Elimina conexiones caducadas de DynamoDB."""
    try:
        table.delete_item(Key={"connectionId": connection_id})
        print(f"Eliminada conexión caducada: {connection_id}")
    except Exception as e:
        print(f"Error al eliminar conexión {connection_id}: {e}")