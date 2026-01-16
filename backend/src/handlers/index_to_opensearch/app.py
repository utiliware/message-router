# backend/src/handlers/index_to_opensearch/app.py
import os
import json
import time
import logging
import uuid
import urllib.parse
import datetime
import boto3
import requests
from requests.auth import HTTPBasicAuth
from botocore.exceptions import ClientError

from aws_xray_sdk.core import patch_all
patch_all()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
secrets = boto3.client("secretsmanager")

OPENSEARCH_ENDPOINT = os.environ.get("OPENSEARCH_ENDPOINT")
OPENSEARCH_INDEX = os.environ.get("OPENSEARCH_INDEX", "messages")
MASTER_SECRET_ARN = os.environ.get("OPENSEARCH_MASTER_SECRET_ARN")

# Cabeceras compatibles: kbn-xsrf (Kibana style) y osd-xsrf (OpenSearch Dashboards)
XSFR_HEADERS = {
    "kbn-xsrf": "true",
    "osd-xsrf": "true",
    "Content-Type": "application/json"
}

# ---------------- helpers ----------------
def get_master_credentials():
    if not MASTER_SECRET_ARN:
        raise RuntimeError("OPENSEARCH_MASTER_SECRET_ARN no definido")
    try:
        resp = secrets.get_secret_value(SecretId=MASTER_SECRET_ARN)
        secret_string = resp.get("SecretString")
        if not secret_string:
            raise RuntimeError("SecretString vacío en Secrets Manager")
        data = json.loads(secret_string)
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            raise RuntimeError("Secret missing username/password")
        logger.info("Master credentials fetched (username=%s)", username)
        return username, password
    except ClientError:
        logger.exception("Error leyendo secret")
        raise

def index_document_basic(index_name, doc, doc_id=None, username=None, password=None):
    auth = None
    if username and password:
        auth = HTTPBasicAuth(username, password)
    if doc_id:
        url = f"https://{OPENSEARCH_ENDPOINT}/{index_name}/_doc/{doc_id}"
        logger.info("Indexing (idempotent) to %s", url)
        r = requests.put(url, auth=auth, json=doc, timeout=15, verify=True)
    else:
        url = f"https://{OPENSEARCH_ENDPOINT}/{index_name}/_doc"
        logger.info("Indexing (auto-id) to %s", url)
        r = requests.post(url, auth=auth, json=doc, timeout=15, verify=True)
    r.raise_for_status()
    return r.json()

def mapping_field_exists(session, auth, index, field):
    """
    Comprueba si un campo existe en el mapping del índice.
    """
    try:
        url = f"https://{OPENSEARCH_ENDPOINT}/{index}/_mapping/field/{field}"
        r = session.get(url, headers=XSFR_HEADERS, auth=auth, timeout=10, verify=True)
        logger.info("field check %s status=%s", field, r.status_code)
        if r.status_code == 200:
            body = r.json()
            return field in json.dumps(body)
    except Exception as e:
        logger.warning("mapping_field_exists exception: %s", e)
    return False

def create_index_pattern_post(session, auth, title, time_field=None, attempts=6):
    url = f"https://{OPENSEARCH_ENDPOINT}/_dashboards/api/saved_objects/index-pattern"
    payload = {"attributes": {"title": title}}
    if time_field:
        payload["attributes"]["timeFieldName"] = time_field
    for attempt in range(attempts):
        try:
            logger.info("Attempt %d: creating index-pattern '%s'", attempt+1, title)
            r = session.post(url, headers=XSFR_HEADERS, auth=auth, json=payload, timeout=15, verify=True)
            logger.info("create_index_pattern status=%s body=%s", r.status_code, r.text[:1000])
            if r.status_code in (200, 201):
                return r.json().get("id")
            elif r.status_code == 409:
                found = find_index_pattern(session, auth, title)
                if found:
                    return found
        except Exception as e:
            logger.warning("create_index_pattern attempt exception: %s", e)
        time.sleep(2 ** attempt)
    return None

def find_index_pattern(session, auth, title):
    url = f"https://{OPENSEARCH_ENDPOINT}/_dashboards/api/saved_objects/_find"
    params = {"type": "index-pattern", "search": title, "search_fields": "title", "per_page": 100}
    try:
        r = session.get(url, headers=XSFR_HEADERS, auth=auth, params=params, timeout=15, verify=True)
        r.raise_for_status()
        for so in r.json().get("saved_objects", []):
            if so.get("attributes", {}).get("title") == title:
                return so.get("id")
    except Exception:
        pass
    return None

def create_visualization_histogram(session, auth, title, index_pattern_id, time_field='@timestamp'):
    url = f"https://{OPENSEARCH_ENDPOINT}/_dashboards/api/saved_objects/visualization"
    vis_state = {
        "title": title,
        "type": "histogram",
        "params": {},
        "aggs": [
            {"id": "1", "enabled": True, "type": "count", "schema": "metric", "params": {}},
            {"id": "2", "enabled": True, "type": "date_histogram", "schema": "segment", "params": {"field": time_field, "interval": "auto", "min_doc_count": 0}}
        ]
    }
    payload = {
        "attributes": {
            "title": title,
            "visState": json.dumps(vis_state),
            "uiStateJSON": "{}",
            "description": "",
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": index_pattern_id,
                    "query": {"query": "", "language": "kuery"},
                    "filter": []
                })
            }
        }
    }
    r = session.post(url, headers=XSFR_HEADERS, auth=auth, json=payload, timeout=15, verify=True)
    logger.info("create_visualization_histogram status=%s body=%s", r.status_code, r.text[:800])
    if r.status_code in (200, 201):
        return r.json().get("id")
    elif r.status_code == 409:
        return find_visualization(session, auth, title)
    return None

def create_visualization_terms(session, auth, title, index_pattern_id, field):
    url = f"https://{OPENSEARCH_ENDPOINT}/_dashboards/api/saved_objects/visualization"
    vis_state = {
        "title": title,
        "type": "pie",
        "params": {},
        "aggs": [
            {"id": "1", "enabled": True, "type": "count", "schema": "metric", "params": {}},
            {"id": "2", "enabled": True, "type": "terms", "schema": "segment", "params": {"field": field, "size": 5}}
        ]
    }
    payload = {
        "attributes": {
            "title": title,
            "visState": json.dumps(vis_state),
            "uiStateJSON": "{}",
            "description": "",
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": index_pattern_id,
                    "query": {"query": "", "language": "kuery"},
                    "filter": []
                })
            }
        }
    }
    r = session.post(url, headers=XSFR_HEADERS, auth=auth, json=payload, timeout=15, verify=True)
    logger.info("create_visualization_terms status=%s body=%s", r.status_code, r.text[:800])
    if r.status_code in (200, 201):
        return r.json().get("id")
    elif r.status_code == 409:
        return find_visualization(session, auth, title)
    return None

def find_visualization(session, auth, title):
    url = f"https://{OPENSEARCH_ENDPOINT}/_dashboards/api/saved_objects/_find"
    params = {"type": "visualization", "search": title, "search_fields": "title", "per_page": 100}
    try:
        r = session.get(url, headers=XSFR_HEADERS, auth=auth, params=params, timeout=15, verify=True)
        r.raise_for_status()
        for so in r.json().get("saved_objects", []):
            if so.get("attributes", {}).get("title") == title:
                return so.get("id")
    except Exception:
        pass
    return None

def create_saved_search(session, auth, title, index_pattern_id):
    url = f"https://{OPENSEARCH_ENDPOINT}/_dashboards/api/saved_objects/search"
    payload = {
        "attributes": {
            "title": title,
            "searchSourceJSON": json.dumps({
                "index": index_pattern_id,
                "query": {"query": "", "language": "kuery"},
                "filter": []
            })
        }
    }
    r = session.post(url, headers=XSFR_HEADERS, auth=auth, json=payload, timeout=15, verify=True)
    logger.info("create_saved_search status=%s body=%s", r.status_code, r.text[:800])
    if r.status_code in (200, 201):
        return r.json().get("id")
    elif r.status_code == 409:
        return find_saved_search(session, auth, title)
    return None

def find_saved_search(session, auth, title):
    url = f"https://{OPENSEARCH_ENDPOINT}/_dashboards/api/saved_objects/_find"
    params = {"type": "search", "search": title, "search_fields": "title", "per_page": 100}
    try:
        r = session.get(url, headers=XSFR_HEADERS, auth=auth, params=params, timeout=15, verify=True)
        r.raise_for_status()
        for so in r.json().get("saved_objects", []):
            if so.get("attributes", {}).get("title") == title:
                return so.get("id")
    except Exception:
        pass
    return None

def create_dashboard_with_panels(session, auth, title, panels, index_pattern_id=None):
    url = f"https://{OPENSEARCH_ENDPOINT}/_dashboards/api/saved_objects/dashboard"
    panels_json = []
    for p in panels:
        panels_json.append({
            "panelIndex": p.get("panelIndex", str(uuid.uuid4())[:6]),
            "gridData": p.get("gridData", {"x": 0, "y": 0, "w": 24, "h": 6}),
            "version": "1.0.0",
            "type": p.get("type", "visualization"),
            "id": p["id"]
        })
    payload = {
        "attributes": {
            "title": title,
            "panelsJSON": json.dumps(panels_json),
            "optionsJSON": "{}"
        },
        "references": []
    }
    if index_pattern_id:
        payload["references"].append({
            "id": index_pattern_id,
            "name": "indexPattern_0",
            "type": "index-pattern"
        })
    r = session.post(url, headers=XSFR_HEADERS, auth=auth, json=payload, timeout=15, verify=True)
    logger.info("create_dashboard_with_panels status=%s body=%s", r.status_code, r.text[:1200])
    if r.status_code in (200, 201):
        return r.json().get("id")
    elif r.status_code == 409:
        return find_dashboard(session, auth, title)
    return None

def find_dashboard(session, auth, title):
    url = f"https://{OPENSEARCH_ENDPOINT}/_dashboards/api/saved_objects/_find"
    params = {"type": "dashboard", "search": title, "search_fields": "title", "per_page": 100}
    try:
        r = session.get(url, headers=XSFR_HEADERS, auth=auth, params=params, timeout=15, verify=True)
        r.raise_for_status()
        for so in r.json().get("saved_objects", []):
            if so.get("attributes", {}).get("title") == title:
                return so.get("id")
    except Exception:
        pass
    return None

# ---------------- handler ----------------
def lambda_handler(event, context):
    logger.info("Event received: %s", json.dumps(event))

    # parse bucket/key
    bucket = event.get("bucket") or event.get("detail", {}).get("bucket", {}).get("name")
    key = event.get("key") or event.get("detail", {}).get("object", {}).get("key")
    logger.info("Parsed bucket=%s key=%s", bucket, key)

    body_text = None
    if bucket and key:
        try:
            resp = s3.get_object(Bucket=bucket, Key=key)
            body_text = resp["Body"].read().decode("utf-8", errors="ignore")
            logger.info("Read S3 object s3://%s/%s len=%d", bucket, key, len(body_text))
        except Exception as e:
            logger.exception("Error reading S3 object")
            return {"status": "error_read_s3", "error": str(e)}

    # get master creds
    try:
        username, password = get_master_credentials()
    except Exception as e:
        logger.exception("Cannot fetch master credentials")
        return {"status": "error_secret", "error": str(e)}

    auth = HTTPBasicAuth(username, password)
    session = requests.Session()

    # ensure index-pattern
    index_pattern_title = OPENSEARCH_INDEX if OPENSEARCH_INDEX.endswith("*") else f"{OPENSEARCH_INDEX}*"
    idx_id = find_index_pattern(session, auth, index_pattern_title)
    if not idx_id:
        idx_id = create_index_pattern_post(session, auth, index_pattern_title, time_field='@timestamp')
    logger.info("Index-pattern id=%s", idx_id)

    # create visualizations/dashboard but only if fields exist
    try:
        hist_id = find_visualization(session, auth, "Messages over time") or create_visualization_histogram(session, auth, "Messages over time", idx_id, time_field='@timestamp')
        # Check if 'sender' field exists in mapping. If not, skip terms viz.
        sender_field = "sender"
        sender_exists = mapping_field_exists(session, auth, OPENSEARCH_INDEX, sender_field)
        if not sender_exists:
            logger.info("Field '%s' not present in mapping; will skip Terms visualization", sender_field)
            terms_id = None
        else:
            terms_id = find_visualization(session, auth, "Top senders (sample)") or create_visualization_terms(session, auth, "Top senders (sample)", idx_id, field=sender_field)

        # ensure saved_search
        search_id = find_saved_search(session, auth, "Recent messages") or create_saved_search(session, auth, "Recent messages", idx_id)

        panels = []
        if hist_id:
            panels.append({"id": hist_id, "type": "visualization", "panelIndex": "1", "gridData": {"x":0,"y":0,"w":24,"h":8}})
        if terms_id:
            panels.append({"id": terms_id, "type": "visualization", "panelIndex": "2", "gridData": {"x":0,"y":8,"w":12,"h":8}})
        if search_id:
            panels.append({"id": search_id, "type": "search", "panelIndex": "3", "gridData": {"x":12,"y":8,"w":12,"h":8}})

        dashboard_title = f"{OPENSEARCH_INDEX} dashboard"
        dash_id = find_dashboard(session, auth, dashboard_title)
        if not dash_id:
            dash_id = create_dashboard_with_panels(session, auth, dashboard_title, panels, index_pattern_id=idx_id)
        logger.info("Dashboard id=%s", dash_id)
    except Exception:
        logger.exception("Error creating saved objects")

    # index document: try to derive sender if missing, ensure @timestamp
    if body_text:
        try:
            try:
                doc = json.loads(body_text)
            except Exception:
                doc = {"message": body_text}
            # fill sender from common keys if missing
            if "sender" not in doc:
                for k in ("sender", "from", "senderId", "source", "user"):
                    if k in doc:
                        doc["sender"] = doc[k]
                        break
            # ensure @timestamp
            if "@timestamp" not in doc:
                doc["@timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
            # idempotent id: s3 key
            doc_id = urllib.parse.quote_plus(key)
            resp = index_document_basic(OPENSEARCH_INDEX, doc, doc_id=doc_id, username=username, password=password)
            logger.info("Indexed document response: %s", resp)
        except Exception:
            logger.exception("Error indexing document")
            return {"status":"error_indexing", "error": "see logs"}

    return {"status":"ok", "index_pattern_id": idx_id, "dashboard_id": dash_id if 'dash_id' in locals() else None}
