# backend/src/handlers/s3_to_postgres/app.py
import os
import json
import uuid
from urllib.parse import unquote_plus

import boto3
import psycopg   # psycopg v3

s3 = boto3.client("s3")
secrets = boto3.client("secretsmanager")

_CONN = None


def _get_db_params():
    """
    Obtiene parámetros de conexión:
    - Host/Port/DB desde variables de entorno
    - Usuario/Password desde Secrets Manager (ARN en DB_SECRET_ARN)
    """
    host = os.environ["DB_HOST"]
    port = int(os.environ.get("DB_PORT", "5432"))
    dbname = os.environ["DB_NAME"]

    secret_arn = os.environ.get("DB_SECRET_ARN")
    if not secret_arn:
        # Modo alterno: variables directas
        user = os.environ["DB_USER"]
        password = os.environ["DB_PASSWORD"]
    else:
        sec = secrets.get_secret_value(SecretId=secret_arn)
        data = json.loads(sec["SecretString"])
        user = data["username"]
        password = data["password"]

    return dict(host=host, port=port, dbname=dbname, user=user, password=password)


def _get_conn():
    """Conexión global reutilizable (fría/caliente)."""
    global _CONN
    if _CONN is None:
        params = _get_db_params()
        _CONN = psycopg.connect(**params, autocommit=True)
        _ensure_schema(_CONN)
    return _CONN


def _ensure_schema(conn):
    """Crea la tabla si no existe (idempotente)."""
    sql = """
    CREATE TABLE IF NOT EXISTS messages (
        message_id TEXT PRIMARY KEY,
        payload    JSONB NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """
    with conn.cursor() as cur:
        cur.execute(sql)


def _download_json(bucket: str, key: str):
    """Descarga un objeto S3 y lo parsea como JSON (devuelve dict)."""
    res = s3.get_object(Bucket=bucket, Key=key)
    body = res["Body"].read()
    return json.loads(body)


def _upsert_message(conn, payload: dict):
    """
    Inserta/actualiza en messages.
    Deriva el id desde el JSON, o genera uno si no existe.
    """
    msg_id = (
        payload.get("MessageId")
        or payload.get("id")
        or payload.get("message_id")
        or str(uuid.uuid4())
    )

    sql = """
    INSERT INTO messages (message_id, payload)
    VALUES (%s, %s)
    ON CONFLICT (message_id) DO UPDATE
    SET payload = EXCLUDED.payload;
    """
    with conn.cursor() as cur:
        cur.execute(sql, (msg_id, json.dumps(payload)))


def lambda_handler(event, context):
    """
    Evento S3 (ObjectCreated:*). Para cada record:
      - lee el JSON del objeto
      - upsert en Postgres
    """
    conn = _get_conn()

    processed = 0
    errors = []

    for record in event.get("Records", []):
        b = record["s3"]["bucket"]["name"]
        k = unquote_plus(record["s3"]["object"]["key"])
        try:
            payload = _download_json(b, k)
            _upsert_message(conn, payload)
            processed += 1
        except Exception as e:
            # no hacemos raise para no reintentar todo el batch
            errors.append({"bucket": b, "key": k, "error": str(e)})

    return {
        "status": "ok" if not errors else "partial",
        "processed": processed,
        "errors": errors,
    }
