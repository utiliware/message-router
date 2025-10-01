import json
import os
import uuid
import boto3
import logging

from aws_xray_sdk.core import xray_recorder, patch_all
patch_all()

# --- Configuración DynamoDB ---
dynamodb = boto3.resource("dynamodb")
table_name = os.environ["TABLE_NAME"]
table = dynamodb.Table(table_name)

# --- Logging ---
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def safe_json_loads(s):
    """Intentar json.loads y si falla devolver el valor original."""
    if not isinstance(s, str):
        return s
    try:
        return json.loads(s)
    except Exception:
        return s


def extract_messages_from_event_dict(data):
    """
    Recibe un dict ya parseado del mensaje SNS y devuelve una lista de mensajes
    en formato canonizado: [{'messageId':..., 'body': ...}, ...]
    """
    msgs = []

    # Caso típico: evento de StepFunctions (EventBridge) con detail.output (string JSON)
    detail = data.get("detail")
    if isinstance(detail, dict):
        out = detail.get("output")
        if out is not None:
            out_parsed = safe_json_loads(out)
            if isinstance(out_parsed, dict):
                if "messages" in out_parsed and isinstance(out_parsed["messages"], list):
                    for m in out_parsed["messages"]:
                        msgs.append(m)
                    return msgs
                if "message" in out_parsed:
                    msgs.append({"messageId": out_parsed.get("messageId"), "body": out_parsed.get("message")})
                    return msgs
                # si no tiene keys esperadas, guardar el objeto completo
                msgs.append(out_parsed)
                return msgs

    # Caso: el propio body tiene "messages" en la raíz
    if "messages" in data and isinstance(data["messages"], list):
        return data["messages"]

    # Caso: single message with "message" property
    if "message" in data:
        return [{"messageId": data.get("messageId"), "body": data.get("message")}]

    # Si es un objeto genérico, intentar meterlo tal cual
    return [data]


def canonize_message_obj(m):
    """
    Canoniza un mensaje en la forma {'messageId': <id>, 'body': <json-serializable>}
    """
    if not isinstance(m, dict):
        return {"messageId": str(uuid.uuid4()), "body": m}
    mid = m.get("messageId") or m.get("id") or str(uuid.uuid4())
    if "body" in m:
        body = m["body"]
    elif "message" in m:
        body = m["message"]
    else:
        body = m
    body = safe_json_loads(body)
    return {"messageId": mid, "body": body}


def extract_text_from_body(body):
    """
    Intentar extraer un texto legible del 'body' con heurísticas:
    - si body es string -> devolverlo
    - si body es dict y tiene 'message' y es primitivo -> devolver body['message']
    - si body es dict y tiene 'body' interno -> recursivamente intentar extraer
    - si body es lista con 1 elemento primitivo -> devolver ese elemento
    - devuelve None si no puede extraer texto simple
    """
    # strings y primitivos
    if isinstance(body, str):
        return body
    if isinstance(body, (int, float, bool)):
        return str(body)

    # dicts
    if isinstance(body, dict):
        # caso directo: {"message": "Hola"}
        if "message" in body and isinstance(body["message"], (str, int, float, bool)):
            return str(body["message"])
        # nested: {"body": {"message": "Hola"}}
        if "body" in body:
            return extract_text_from_body(body["body"])
        # otras claves: buscar heurísticamente por keys comunes
        for key in ("text", "msg", "payload"):
            if key in body and isinstance(body[key], (str, int, float, bool)):
                return str(body[key])
        # no encontramos un texto simple
        return None

    # listas
    if isinstance(body, list) and len(body) == 1:
        return extract_text_from_body(body[0])

    return None


def lambda_handler(event, context):
    logger.info("Evento recibido desde SNS: %s", json.dumps(event))

    for record in event.get("Records", []):
        sns_message = record.get("Sns", {}).get("Message", "")

        parsed = safe_json_loads(sns_message)
        logger.info("SNS Message parsed (type=%s): %s", type(parsed).__name__, str(parsed)[:1000])

        extracted = []
        if isinstance(parsed, dict):
            extracted = extract_messages_from_event_dict(parsed)
        elif isinstance(parsed, list):
            extracted = parsed
        else:
            # string plano u otro tipo -> guardar como single message
            extracted = [{"message": parsed}]

        # Canonizar cada message y guardarlo (uno por item en Dynamo)
        for raw in extracted:
            msg = canonize_message_obj(raw)

            # Intentar extraer el texto real (p.ej. body={"message":"Hola"} -> "Hola")
            text = extract_text_from_body(msg["body"])

            if text is not None:
                body_to_store = text
            else:
                # Fallback: almacenar estructura JSON legible
                try:
                    body_to_store = msg["body"] if isinstance(msg["body"], str) else json.dumps(msg["body"], ensure_ascii=False)
                except Exception:
                    body_to_store = str(msg["body"])

            item = {
                "MessageId": msg["messageId"],
                "Message": body_to_store,
            }
            logger.info("Guardando item en DynamoDB: %s", json.dumps(item, ensure_ascii=False))
            try:
                table.put_item(Item=item)
            except Exception as e:
                logger.exception("Error guardando item en DynamoDB: %s", e)

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps({"status": "Mensajes almacenados en DynamoDB"}),
    }
