import os, json, boto3, uuid, logging
from datetime import datetime

from aws_xray_sdk.core import xray_recorder, patch_all
patch_all()

sfn = boto3.client("stepfunctions")
STATE_MACHINE_ARN = os.environ.get("STATE_MACHINE_ARN", "").strip()


log = logging.getLogger()
log.setLevel(logging.INFO)


def _safe_start_execution(payload):
    resp = sfn.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        name=str(uuid.uuid4()),
        input=json.dumps(payload, ensure_ascii=False),
    )
    # Convert the boto3 response to a JSON-serializable dict
    safe = {
        "executionArn": resp.get("executionArn"),
        # startDate puede ser datetime -> convertir a ISO string si existe
        "startDate": resp.get("startDate").isoformat() if resp.get("startDate") else None,
        "ResponseMetadata": {
            "HTTPStatusCode": resp.get("ResponseMetadata", {}).get("HTTPStatusCode")
        }
    }
    return safe


def lambda_handler(event, context):
    records = event.get("Records", [])
    if not records:
        log.info("No Records (trigger vacío); nada que hacer")
        return {"ok": True, "count": 0}

    messages = []
    for r in records:
        try:
            body = json.loads(r["body"])
        except Exception:
            body = {"message": r["body"]}  # por si llega texto plano
        messages.append({"messageId": r["messageId"], "body": body})

    log.info("Arrancando SFN con %d mensajes", len(messages))

    if not STATE_MACHINE_ARN or STATE_MACHINE_ARN == "*" or STATE_MACHINE_ARN.lower().startswith("invalid"):
        log.warning("STATE_MACHINE_ARN no configurado o inválido (%s). Saltando start_execution.", STATE_MACHINE_ARN)
        return {"ok": False, "count": len(messages), "error": "missing_state_machine_arn"}

    try:
        payload = {"messages": messages}
        resp_safe = _safe_start_execution(payload)
        log.info("StartExecution safe response: %s", resp_safe)
        # Devuelve sólo campos serializables
        return {"ok": True, "count": len(messages), "startExecution": resp_safe}
    except Exception as e:
        log.exception("Error arrancando StepFunction: %s", e)
        # No lanzar excepción; devolver error serializable (si quieres forzar retry, lanza la excepción en vez de devolver)
        return {"ok": False, "count": len(messages), "error": str(e)}

