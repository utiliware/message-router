import os
import json
import boto3
import uuid
import time
import logging

from aws_xray_sdk.core import xray_recorder, patch_all
patch_all()

log = logging.getLogger()
log.setLevel(logging.INFO)

sfn = boto3.client("stepfunctions")
STATE_MACHINE_ARN = os.environ.get("STATE_MACHINE_ARN", "").strip()
# Número de reintentos para start_execution (en caso de fallo transitorio)
SFN_START_RETRIES = int(os.environ.get("SFN_START_RETRIES", "2"))
SFN_START_BACKOFF = float(os.environ.get("SFN_START_BACKOFF", "0.2"))  # segundos

def safe_json_load(s):
    if not isinstance(s, str):
        return s
    s = s.strip()
    if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
        try:
            return json.loads(s)
        except Exception:
            return s
    return s

def start_sfn_for_message(message_payload):
    """Intenta arrancar una ejecución SFN con retries. Lanza excepción si falla."""
    serialized = json.dumps(message_payload, ensure_ascii=False)
    attempt = 0
    while True:
        try:
            resp = sfn.start_execution(
                stateMachineArn=STATE_MACHINE_ARN,
                name=str(uuid.uuid4()),
                input=serialized
            )
            return {
                "executionArn": resp.get("executionArn"),
                "startDate": resp.get("startDate").isoformat() if resp.get("startDate") else None,
                "HTTPStatusCode": resp.get("ResponseMetadata", {}).get("HTTPStatusCode")
            }
        except Exception as e:
            attempt += 1
            log.warning("start_execution fallo (attempt %d/%d): %s", attempt, SFN_START_RETRIES, str(e))
            if attempt > SFN_START_RETRIES:
                raise
            time.sleep(SFN_START_BACKOFF * attempt)

def lambda_handler(event, context):
    records = event.get("Records", [])
    if not records:
        log.info("No Records; nothing to do")
        return {"ok": True, "count": 0}

    parsed = []
    for r in records:
        raw_body = r.get("body", "")
        body = safe_json_load(raw_body)
        # si body es dict, normalizar campos que a su vez sean strings JSON
        if isinstance(body, dict):
            normalized = {}
            for k, v in body.items():
                if isinstance(v, str):
                    normalized[k] = safe_json_load(v)
                else:
                    normalized[k] = v
            body = normalized
        parsed.append({
            "messageId": r.get("messageId"),
            "receiptHandle": r.get("receiptHandle"),
            "body": body
        })

    log.info("Procesando %d mensajes (parsed sample): %s", len(parsed), parsed[:5])

    if not STATE_MACHINE_ARN or STATE_MACHINE_ARN == "*" or STATE_MACHINE_ARN.lower().startswith("invalid"):
        log.error("STATE_MACHINE_ARN inválido (%s). No puedo start_execution.", STATE_MACHINE_ARN)
        # indicar reintento para todos
        return {"batchItemFailures": [{"itemIdentifier": p["messageId"]} for p in parsed]}

    batch_failures = []
    executions = []

    # START ONE EXECUTION PER MESSAGE (no chunking)
    for item in parsed:
        payload = {
            "messageId": item["messageId"],
            "body": item["body"]
        }
        try:
            resp = start_sfn_for_message(payload)
            executions.append(resp)
            log.info("SFN started for message %s -> %s", item["messageId"], resp.get("executionArn"))
        except Exception as e:
            log.exception("No se pudo start_execution para messageId %s: %s", item["messageId"], e)
            batch_failures.append(item["messageId"])

    if batch_failures:
        # informar a SQS cuáles messages deben reintentarse
        log.warning("Mensajes que fallaron y serán reintentados: %s", batch_failures)
        return {"batchItemFailures": [{"itemIdentifier": mid} for mid in batch_failures]}

    return {"ok": True, "count": len(parsed), "executions": executions}
