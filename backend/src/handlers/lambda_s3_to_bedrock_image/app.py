import boto3
import json
import redis
import os
from datetime import datetime

# ---------- Clientes AWS ----------
s3_client = boto3.client("s3")
bedrock_client = boto3.client("bedrock-runtime")

# ---------- Variables de entorno Valkey ----------
VALKEY_HOST = os.environ.get("VALKEY_HOST")
VALKEY_PORT = int(os.environ.get("VALKEY_PORT", 6379))

# ---------- Conexión global Valkey ----------
valkey_client = redis.StrictRedis(
    host=VALKEY_HOST,
    port=VALKEY_PORT,
    decode_responses=True
)

def lambda_handler(event, context):
    try:
        # ---------- Extraer mensaje de SNS ----------
        sns_message = event["Records"][0]["Sns"]["Message"]
        s3_event = json.loads(sns_message)

        # ---------- Obtener bucket y key ----------
        record = s3_event["Records"][0]["s3"]
        bucket_name = record["bucket"]["name"]
        object_key = record["object"]["key"]

        print(f"📥 Processing S3 object: s3://{bucket_name}/{object_key}")

        # ---------- Leer objeto S3 ----------
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        content = response["Body"].read().decode("utf-8")
        obj = json.loads(content)

        message_text = obj.get("item", {}).get("Message", "").strip()
        if not message_text:
            raise ValueError("Message text is empty")

        # ---------- Construir prompt ----------
        prompt = f"What's the meaning of '{message_text}'?"

        # ---------- Cache lookup ----------
        cached_response = valkey_client.get(prompt)
        if cached_response:
            print("⚡ Cache hit")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "prompt": prompt,
                    "response": cached_response,
                    "source": "cache"
                })
            }

        print("🤖 Calling Amazon Bedrock (Nova)")

        # ---------- Llamada a Bedrock ----------
        bedrock_response = bedrock_client.invoke_model(
            modelId="amazon.nova-2-lite-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"text": prompt}
                        ]
                    }
                ]
            })
        )

        # ---------- Parsear respuesta ----------
        result = json.loads(bedrock_response["body"].read())

        response_text = (
            result
            .get("output", {})
            .get("message", {})
            .get("content", [{}])[0]
            .get("text", "No response")
        )

        print("🧠 Bedrock response:", response_text)

        # ---------- Guardar en cache ----------
        valkey_client.set(prompt, response_text)
        valkey_client.set(
            f"prompt:{datetime.utcnow().isoformat()}",
            prompt
        )

        print("💾 Stored prompt in Valkey")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "prompt": prompt,
                "response": response_text,
                "source": "bedrock"
            })
        }

    except Exception as e:
        print("❌ Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }