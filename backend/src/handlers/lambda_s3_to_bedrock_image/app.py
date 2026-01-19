import os
import json
import boto3
import base64
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1"))
MODEL_ID = os.environ.get("MODEL_ID", "amazon.nova-canvas-v1:0")
OUTPUT_BUCKET = os.environ.get("OUTPUT_BUCKET")

def _try_parse_json(s):
    try:
        return json.loads(s)
    except Exception:
        return None

def _extract_candidate_from_dict(d):
    if d is None:
        return None

    for k in ("prompt", "text", "message", "Message", "body", "Body"):
        if k in d and isinstance(d[k], (str, int, float)):
            return str(d[k])

    # SNS style: might come wrapped as {"Records": [ { "Sns": {"Message": "..."} } ] }
    if "Records" in d and isinstance(d["Records"], list) and len(d["Records"]) > 0:
        rec0 = d["Records"][0]
        if isinstance(rec0, dict) and "Sns" in rec0 and isinstance(rec0["Sns"], dict):
            sns_msg = rec0["Sns"].get("Message")
            if sns_msg:
                parsed = _try_parse_json(sns_msg)
                if isinstance(parsed, dict):
                    return _extract_candidate_from_dict(parsed) or sns_msg
                return sns_msg
        if isinstance(rec0, dict) and "s3" in rec0 and isinstance(rec0["s3"], dict):
            return None

    for v in d.values():
        if isinstance(v, str) and len(v.strip()) > 0 and len(v) < 2000:
            if not (v.strip().startswith("{") and v.strip().endswith("}")):
                return v

    return None

def build_prompt_from_text(extracted_text):
    return f"Generate a high-resolution, photorealistic image of: {extracted_text}"

def lambda_handler(event, context):
    logger.info("Event received: %s", json.dumps(event))

    try:
        record = event["Records"][0]
        sns_msg_raw = record["Sns"]["Message"]
    except Exception as e:
        logger.exception("Event format unexpected; aborting")
        raise

    parsed_sns_msg = _try_parse_json(sns_msg_raw) or sns_msg_raw

    bucket = None
    key = None
    if isinstance(parsed_sns_msg, dict) and "Records" in parsed_sns_msg and parsed_sns_msg["Records"]:
        rec0 = parsed_sns_msg["Records"][0]
        if "s3" in rec0:
            logger.info("S3 event detected inside SNS message")
            bucket = rec0["s3"]["bucket"]["name"]
            key = rec0["s3"]["object"]["key"]

    if bucket and key:
        logger.info("Incoming S3 event detected")
        logger.info("Detected S3 notification inside SNS. bucket=%s key=%s", bucket, key)
        obj = s3.get_object(Bucket=bucket, Key=key)
        prompt_text_raw = obj["Body"].read().decode("utf-8")
        logger.info("Prompt text read from S3: %s", prompt_text_raw)
    else:
        logger.info("No S3 event detected; using SNS message body directly")
        prompt_text_raw = parsed_sns_msg if isinstance(parsed_sns_msg, str) else json.dumps(parsed_sns_msg)
        logger.info("Using SNS message body as prompt source: %s", prompt_text_raw)


    parsed = _try_parse_json(prompt_text_raw)
    extracted = None
    if isinstance(parsed, dict):
        logger.info("Parsed prompt text as JSON dict; attempting structured extraction")
        extracted = _extract_candidate_from_dict(parsed)

    if not extracted and isinstance(parsed, dict):
        logger.info("No candidate found at top level; searching nested dicts")
        for v in parsed.values():
            if isinstance(v, str):
                maybe = _try_parse_json(v)
                if isinstance(maybe, dict):
                    extracted = _extract_candidate_from_dict(maybe)
                    if extracted:
                        logger.info("Found candidate in nested dict")
                        break

    if not extracted:
        logger.info("No structured prompt text found; falling back to raw text extraction")
        if isinstance(prompt_text_raw, str) and len(prompt_text_raw.strip()) > 0:
            try:
                logger.info("Falling back to regex extraction from raw prompt text")
                import re
                m = re.search(r'"Message"\s*:\s*"([^"]+)"', prompt_text_raw)
                if m:
                    extracted = m.group(1)
                else:
                    logger.info("No regex match for 'Message' field; using full text fallback")
                    extracted = prompt_text_raw.strip()
            except Exception:
                extracted = prompt_text_raw.strip()
        else:
            raise RuntimeError("No usable prompt text found in SNS/S3 payload")

    logger.info("Extracted text for prompt: %s", extracted)

    final_prompt = build_prompt_from_text(extracted)
    logger.info("Final prompt to Bedrock: %s", final_prompt)

    native_request = {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": final_prompt},
        "imageGenerationConfig": {
            "seed": 0,
            "quality": "standard",
            "width": 1024,
            "height": 1024,
            "numberOfImages": 1
        }
    }
    body_bytes = json.dumps(native_request).encode("utf-8")

    try:
        resp = bedrock.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            body=body_bytes
        )
    except Exception:
        logger.exception("InvokeModel failed")
        raise

    resp_body = resp["body"].read()
    logger.info("Raw response bytes length: %d", len(resp_body) if resp_body is not None else 0)

    img_bytes = None
    try:
        parsed_resp = json.loads(resp_body)
        logger.info("Parsed response JSON keys: %s", list(parsed_resp.keys()))
        if parsed_resp.get("images"):
            img_b64 = parsed_resp["images"][0]
        else:
            img_b64 = parsed_resp.get("image_base64") or parsed_resp.get("b64_json") or parsed_resp.get("output")
        if img_b64:
            img_bytes = base64.b64decode(img_b64)
    except Exception:
        try:
            text = resp_body.decode("utf-8")
            maybe = json.loads(text)
            if isinstance(maybe, dict) and maybe.get("images"):
                img_bytes = base64.b64decode(maybe["images"][0])
        except Exception:
            img_bytes = resp_body if isinstance(resp_body, (bytes, bytearray)) else None

    if not img_bytes:
        logger.error("No image found in model response: %s", resp_body[:1000])
        raise RuntimeError("No image found in model response")

    safe_base = "unknown"
    try:
        if bucket and key:
            safe_base = os.path.splitext(key)[0]
        else:
            import uuid
            safe_base = f"msg-{str(uuid.uuid4())[:8]}"
    except Exception:
        safe_base = "output"

    out_key = f"generated-images/{safe_base}-nova-canvas.png"
    s3.put_object(Bucket=OUTPUT_BUCKET, Key=out_key, Body=img_bytes, ContentType="image/png")
    logger.info("Saved generated image to s3://%s/%s", OUTPUT_BUCKET, out_key)

    return {"statusCode": 200, "body": json.dumps({"out_key": out_key})}
