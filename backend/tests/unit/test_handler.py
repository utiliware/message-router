import json
import os
import importlib
import sys
import types

import pytest

# Fake SQS client para pruebas
class FakeSQS:
    def __init__(self):
        self.sent_messages = []
        self.batches = []

    def send_message(self, QueueUrl, MessageBody):
        self.sent_messages.append((QueueUrl, MessageBody))
        return {"MessageId": "fake-msg-id"}

    def send_message_batch(self, QueueUrl, Entries):
        self.batches.append((QueueUrl, Entries))
        return {"Successful": [{"Id": e["Id"]} for e in Entries]}


@pytest.fixture(autouse=True)
def set_queue_env(monkeypatch):
    monkeypatch.setenv("QUEUE_URL", "https://sqs-fake-url/123/queue")
    yield


def import_app_with_fake_sqs(monkeypatch):
    """
    Inserta un módulo 'boto3' falso en sys.modules antes de importar la app,
    así la importación no fallará y la app asignará app.sqs = FakeSQS() al importar.
    También mockeamos aws_xray_sdk.core.patch_all si no existe.
    """
    # Crear fake boto3 con client() que devuelve FakeSQS
    fake_boto3 = types.ModuleType("boto3")
    def client(service_name, *args, **kwargs):
        if service_name == "sqs":
            return FakeSQS()
        raise RuntimeError(f"Unexpected boto3.client('{service_name}') in test")
    fake_boto3.client = client
    monkeypatch.setitem(sys.modules, "boto3", fake_boto3)

    # Opcional: mockear aws_xray_sdk.core.patch_all si no está instalado
    fake_xray_core = types.ModuleType("aws_xray_sdk.core")
    fake_xray_core.xray_recorder = types.SimpleNamespace()
    fake_xray_core.patch_all = lambda *a, **k: None
    monkeypatch.setitem(sys.modules, "aws_xray_sdk.core", fake_xray_core)

    # Importar la app (usa handlers.message_router_queue.app porque tu PYTHONPATH=backend/src)
    if "handlers.message_router_queue.app" in sys.modules:
        importlib.reload(sys.modules["handlers.message_router_queue.app"])
    app_mod = importlib.import_module("handlers.message_router_queue.app")

    # app_mod.sqs debería ser la instancia FakeSQS creada por fake_boto3.client
    fake = getattr(app_mod, "sqs", None)
    return app_mod, fake


def test_options_preflight(monkeypatch):
    app_mod, fake = import_app_with_fake_sqs(monkeypatch)

    event = {"httpMethod": "OPTIONS"}
    resp = app_mod.lambda_handler(event, None)

    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert body["message"] == "CORS preflight OK"
    assert "Access-Control-Allow-Origin" in resp["headers"]


def test_post_single_message(monkeypatch):
    app_mod, fake = import_app_with_fake_sqs(monkeypatch)

    event = {
        "httpMethod": "POST",
        "body": json.dumps({"message": "hola"})
    }
    resp = app_mod.lambda_handler(event, None)

    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert fake and fake.sent_messages, "Expected send_message to be called"
    queue_url, message_body = fake.sent_messages[0]
    assert queue_url == os.environ["QUEUE_URL"]
    data = json.loads(message_body)
    assert data["message"] == "hola"


def test_post_multiple_messages(monkeypatch):
    app_mod, fake = import_app_with_fake_sqs(monkeypatch)

    messages = ["m1", "m2", "m3"]
    event = {
        "httpMethod": "POST",
        "body": json.dumps({"messages": messages})
    }
    resp = app_mod.lambda_handler(event, None)

    assert resp["statusCode"] == 200
    assert fake and fake.batches, "Expected send_message_batch to be called"
    queue_url, entries = fake.batches[0]
    assert queue_url == os.environ["QUEUE_URL"]
    sent = [json.loads(e["MessageBody"])["message"] for e in entries]
    assert sent == messages


def test_post_empty_messages_returns_400(monkeypatch):
    app_mod, fake = import_app_with_fake_sqs(monkeypatch)

    event = {
        "httpMethod": "POST",
        "body": json.dumps({"messages": []})
    }
    resp = app_mod.lambda_handler(event, None)
    assert resp["statusCode"] == 400
    body = json.loads(resp["body"])
    assert "no puede" in body["message"].lower()
