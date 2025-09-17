import os, json, boto3
sqs = boto3.client("sqs")
QUEUE_URL = os.environ["QUEUE_URL"]

def lambda_handler(event, context):
    try:
        detail = event.get("detail", {})
        body = detail.get("message", detail)
        if not isinstance(body, str):
            body = json.dumps(body, ensure_ascii=False)
        resp = sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=body)
        return {"statusCode": 200, "body": json.dumps({"ok": True, "messageId": resp["MessageId"]})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"ok": False, "error": str(e)})}
