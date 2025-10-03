import boto3
import json

# Clientes AWS
s3_client = boto3.client('s3')
bedrock_client = boto3.client('bedrock-runtime')

def lambda_handler(event, context):
    # --- Extraer el mensaje de SNS ---
    sns_message = event['Records'][0]['Sns']['Message']
    s3_event = json.loads(sns_message)  # Convertir string JSON a dict

    # --- Obtener bucket y key del evento S3 ---
    record = s3_event['Records'][0]['s3']
    bucket_name = record['bucket']['name']
    object_key = record['object']['key']

    # --- Leer contenido del objeto S3 ---
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    content = response['Body'].read().decode('utf-8')
    
    # --- Parsear JSON del objeto ---
    obj = json.loads(content)
    message_text = obj.get("item", {}).get("Message", "")
    
    # --- Construir prompt para Bedrock solo con el "Message" ---
    prompt = f"What's the meaning of '{message_text}'?"

    # --- Llamar a Bedrock ---
    bedrock_response = bedrock_client.invoke_model(
        modelId="amazon.titan-text-express-v1",
        body=json.dumps({"inputText": prompt}),
        contentType="application/json"
    )

    # --- Leer la respuesta ---
    result = json.loads(bedrock_response['body'].read())

    # --- Imprimir resultado en CloudWatch Logs ---
    print("Bedrock result:", result)

    # --- Retornar únicamente la respuesta generada ---
    return {
        "statusCode": 200,
        "body": json.dumps({
            "prompt": prompt,
            "response": result.get("content")
        })
    }
