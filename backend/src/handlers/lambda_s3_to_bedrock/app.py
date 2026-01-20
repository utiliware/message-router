import boto3
import json
import redis
import os
from datetime import datetime
from botocore.exceptions import ClientError

# Clientes AWS
s3_client = boto3.client("s3")
bedrock_client = boto3.client("bedrock-runtime")

# Variables de entorno Valkey
VALKEY_HOST = os.environ.get("VALKEY_HOST")
VALKEY_PORT = int(os.environ.get("VALKEY_PORT", 6379))

# Conexión global Valkey (reutilizable)
valkey_client = redis.StrictRedis(
    host=VALKEY_HOST,
    port=VALKEY_PORT,
    decode_responses=True
)

# Modelo Nova (puedes cambiar a nova-lite si quieres)
MODEL_ID = "amazon.nova-micro-v1:0"
# MODEL_ID = "amazon.nova-lite-v1:0"

def lambda_handler(event, context):
    # --- Extraer el mensaje de SNS ---
    sns_message = event["Records"][0]["Sns"]["Message"]
    s3_event = json.loads(sns_message)

    # --- Obtener bucket y key del evento S3 ---
    record = s3_event["Records"][0]["s3"]
    bucket_name = record["bucket"]["name"]
    object_key = record["object"]["key"]

    # --- Leer contenido del objeto S3 ---
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    content = response["Body"].read().decode("utf-8")
    obj = json.loads(content)
    message_text = obj.get("item", {}).get("Message", "")

    # --- Construir prompt ---
    prompt = f"What's the meaning of '{message_text}'?"

    # --- Cache lookup ---
    cached_response = valkey_client.get(prompt)
    if cached_response:
        print("🟢 Cache hit")
        return {
            "statusCode": 200,
            "body": json.dumps({
                "prompt": prompt,
                "response": cached_response,
                "source": "cache"
            })
        }

    # --- Construir conversación para Nova ---
    conversation = [
        {
            "role": "user",
            "content": [
                {"text": prompt}
            ]
        }
    ]

    try:
        # --- Llamada a Amazon Nova ---
        bedrock_response = bedrock_client.converse(
            modelId=MODEL_ID,
            messages=conversation,
            inferenceConfig={
                "maxTokens": 300,
                "temperature": 0.5,
                "topP": 0.9
            }
        )

        # --- Extraer texto generado ---
        response_text = "No response"
        if (
            "output" in bedrock_response
            and "message" in bedrock_response["output"]
            and "content" in bedrock_response["output"]["message"]
        ):
            response_text = bedrock_response["output"]["message"]["content"][0]["text"]

    except ClientError as e:
        print("❌ Bedrock error:", e)
        raise e

    # --- Guardar en cache ---
    valkey_client.set(prompt, response_text)
    valkey_client.set(
        f"prompt:{datetime.utcnow().isoformat()}",
        prompt
    )

    print("💾 Stored prompt:", prompt)
    print("🤖 Nova response:", response_text)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "prompt": prompt,
            "response": response_text,
            "source": "bedrock-nova"
        })
    }
