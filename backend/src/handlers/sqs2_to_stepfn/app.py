import os, json, boto3, uuid, logging

sfn = boto3.client("stepfunctions")
STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]

log = logging.getLogger()
log.setLevel(logging.INFO)

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
    sfn.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        name=str(uuid.uuid4()),
        input=json.dumps({"messages": messages}, ensure_ascii=False),
    )
    return {"ok": True, "count": len(messages)}
