import os
import json
import boto3
import uuid
import time
import logging

from aws_xray_sdk.core import xray_recorder, patch_all
patch_all()

# Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client("sqs")
QUEUE_URL = os.environ.get("QUEUE_URL")

# Configuración de reintentos para send_message_batch
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 0.2  # segundos (se multiplica por (attempt))

def send_batch_with_retries(entries):
    """
    Envía un batch (lista de entries) a SQS con reintentos para los fallos parciales.
    Devuelve una tupla (final_response, persistent_failed_entries)
      - final_response: lista de responses acumuladas (successful + failed info)
      - persistent_failed_entries: lista de entries que siguieron fallando tras reintentos
    """
    # Intento inicial
    resp = sqs.send_message_batch(QueueUrl=QUEUE_URL, Entries=entries)
    logger.info("send_message_batch response: %s", json.dumps(resp, ensure_ascii=False))
    failed = resp.get("Failed", [])
    successful = resp.get("Successful", [])

    # Si no hay fallos, devolvemos
    if not failed:
        return [resp], []

    # Reintentar fallos
    persistent_failed = failed
    accumulated_responses = [resp]

    attempt = 1
    while persistent_failed and attempt <= MAX_RETRIES:
        # reconstruir entries para retry usando Id de failed
        retry_entries = []
        failed_ids = {f["Id"] for f in persistent_failed}
        for e in entries:
            if e["Id"] in failed_ids:
                retry_entries.append(e)

        if not retry_entries:
            break

        sleep_time = RETRY_BACKOFF_BASE * attempt
        logger.warning("Retrying %d failed entries (attempt %d) after %.2fs", len(retry_entries), attempt, sleep_time)
        time.sleep(sleep_time)

        resp_retry = sqs.send_message_batch(QueueUrl=QUEUE_URL, Entries=retry_entries)
        logger.info("send_message_batch retry response (attempt %d): %s", attempt, json.dumps(resp_retry, ensure_ascii=False))
        accumulated_responses.append(resp_retry)

        # Calcular los fallos que persisten
        persistent_failed = resp_retry.get("Failed", [])
        attempt += 1

    # Al final, persistent_failed contiene los que no pudieron encolarse
    return accumulated_responses, persistent_failed

def lambda_handler(event, context):
    if not QUEUE_URL:
        logger.error("QUEUE_URL no está configurada en las variables de entorno")
        return {
            "statusCode": 500,
            "body": json.dumps({"ok": False, "error": "QUEUE_URL not configured"})
        }

    try:
        detail = event.get("detail", {})
        # soportar tanto evento con detail.messages como un detail único
        messages = detail.get("messages", [detail])

        if not isinstance(messages, list):
            messages = [messages]

        # Normalizar messages a strings JSON si son dicts/otros
        normalized = []
        for m in messages:
            if isinstance(m, str):
                # dejar tal cual
                normalized.append(m)
            else:
                try:
                    normalized.append(json.dumps(m, ensure_ascii=False))
                except Exception:
                    # si no se puede serializar, usar str()
                    normalized.append(str(m))

        # Crear lotes (batches) de hasta 10
        batches = [normalized[i:i+10] for i in range(0, len(normalized), 10)]

        all_batch_results = []
        persistent_failures = []

        for batch in batches:
            # Construir entries con Id único por batch
            entries = []
            for msg in batch:
                entries.append({
                    "Id": str(uuid.uuid4()),
                    "MessageBody": msg
                })

            logger.info("Enviando batch con %d entries a SQS", len(entries))
            acc_responses, failed_entries = send_batch_with_retries(entries)

            # Registrar resultados de este batch
            batch_summary = {
                "entries_sent": len(entries),
                "responses": acc_responses,
                "failed_count_after_retries": len(failed_entries),
                "failed_entries": failed_entries
            }
            all_batch_results.append(batch_summary)

            if failed_entries:
                # Añadir a la lista persistente para reportar
                persistent_failures.extend(failed_entries)

        if persistent_failures:
            # Si hubo fallos persistentes, devolvemos 500 con detalles para debug/reintento
            logger.error("Algunos mensajes fallaron de forma persistente y no se pudieron encolar: %s", json.dumps(persistent_failures, ensure_ascii=False))
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "ok": False,
                    "message": "Some messages failed to enqueue after retries",
                    "batchesSent": len(all_batch_results),
                    "results": all_batch_results,
                    "persistentFailures": persistent_failures
                }, ensure_ascii=False)
            }

        # Todo enviado con éxito (tras reintentos si los hubo)
        logger.info("Todos los batches enviados correctamente (%d batches)", len(all_batch_results))
        return {
            "statusCode": 200,
            "body": json.dumps({
                "ok": True,
                "batchesSent": len(all_batch_results),
                "results": all_batch_results
            }, ensure_ascii=False)
        }

    except Exception as e:
        logger.exception("Error procesando evento en eb_to_sqs2: %s", e)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "ok": False,
                "error": str(e)
            }, ensure_ascii=False)
        }
