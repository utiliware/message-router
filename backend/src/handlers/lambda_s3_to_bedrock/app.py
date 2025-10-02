import boto3
import os
import json

# Clientes AWS
s3_client = boto3.client('s3')
bedrock_client = boto3.client('bedrock')  # Debes tener permisos: bedrock:InvokeModel

def lambda_handler(event, context):
    # --- Extraer el mensaje de SNS ---
    sns_message = event['Records'][0]['Sns']['Message']
    s3_event = json.loads(sns_message)  # Convertir el string JSON a dict

    # --- Obtener bucket y key del evento S3 ---
    record = s3_event['Records'][0]['s3']
    bucket_name = record['bucket']['name']
    object_key = record['object']['key']
    
    # --- Leer contenido del objeto S3 ---
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    content = response['Body'].read().decode('utf-8')
    
    # --- Construir prompt para Bedrock ---
    prompt = f"What's the meaning of {content}"
    
    # --- Llamar a Bedrock (Titan Text G1 - Express) ---
    bedrock_response = bedrock_client.invoke_model(
        modelId="titan-text-g1",  # Nombre del modelo Titan Text G1 - Express
        body=json.dumps({
            "inputText": prompt,
            "maxTokens": 200
        }),
        contentType="application/json"
    )
    
    # --- Leer la respuesta ---
    result = json.loads(bedrock_response['body'].read())
    
    # --- Retornar resultado ---
    return {
        "statusCode": 200,
        "body": json.dumps({
            "prompt": prompt,
            "response": result.get("outputText")
        })
    }
