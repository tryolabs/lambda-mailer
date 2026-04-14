import boto3
import pytest
from httpx import ASGITransport, AsyncClient
from moto import mock_aws

from api import app


@pytest.fixture
def ses_client(aws_credentials):
    """Create a mocked SES client and verify the sender email."""
    with mock_aws():
        client = boto3.client("ses", region_name="us-east-1")
        client.verify_email_identity(EmailAddress="test-from@example.com")
        yield client


@pytest.fixture
def patched_app(ses_client, monkeypatch):
    """Patch the app's SES client to use the mocked one."""
    import api

    monkeypatch.setattr(api, "ses", ses_client)
    return app


@pytest.fixture
async def client(patched_app):
    transport = ASGITransport(app=patched_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


SECRET_HEADER = {"X-Form-Secret": "test-secret"}

VALID_PAYLOAD = {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "message": "Hello, this is a test message.",
}


# --- Shared secret tests ---


@pytest.mark.anyio
async def test_missing_secret_returns_403(client):
    resp = await client.post("/", json=VALID_PAYLOAD)
    assert resp.status_code == 403


@pytest.mark.anyio
async def test_wrong_secret_returns_403(client):
    resp = await client.post("/", json=VALID_PAYLOAD, headers={"X-Form-Secret": "wrong"})
    assert resp.status_code == 403


# --- Validation tests ---


@pytest.mark.anyio
async def test_valid_request(client):
    resp = await client.post("/", json=VALID_PAYLOAD, headers=SECRET_HEADER)
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_missing_name(client):
    payload = {"email": "a@b.com", "message": "hi"}
    resp = await client.post("/", json=payload, headers=SECRET_HEADER)
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_missing_email(client):
    payload = {"name": "Jane", "message": "hi"}
    resp = await client.post("/", json=payload, headers=SECRET_HEADER)
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_missing_message(client):
    payload = {"name": "Jane", "email": "a@b.com"}
    resp = await client.post("/", json=payload, headers=SECRET_HEADER)
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_empty_name(client):
    payload = {"name": "   ", "email": "a@b.com", "message": "hi"}
    resp = await client.post("/", json=payload, headers=SECRET_HEADER)
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_empty_email(client):
    payload = {"name": "Jane", "email": "   ", "message": "hi"}
    resp = await client.post("/", json=payload, headers=SECRET_HEADER)
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_empty_message(client):
    payload = {"name": "Jane", "email": "a@b.com", "message": "   "}
    resp = await client.post("/", json=payload, headers=SECRET_HEADER)
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_invalid_email_format(client):
    payload = {"name": "Jane", "email": "not-an-email", "message": "hi"}
    resp = await client.post("/", json=payload, headers=SECRET_HEADER)
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_empty_body(client):
    resp = await client.post(
        "/", content=b"", headers={"content-type": "application/json", **SECRET_HEADER}
    )
    assert resp.status_code == 422


# --- Honeypot tests ---


@pytest.mark.anyio
async def test_honeypot_field_returns_ok_without_sending(client):
    payload = {**VALID_PAYLOAD, "_important": "gotcha"}
    resp = await client.post("/", json=payload, headers=SECRET_HEADER)
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# --- Extra fields tests ---


@pytest.mark.anyio
async def test_extra_fields_accepted(client):
    payload = {**VALID_PAYLOAD, "budget": "75-100k", "company": "Acme"}
    resp = await client.post("/", json=payload, headers=SECRET_HEADER)
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# --- CORS tests ---


@pytest.mark.anyio
async def test_cors_preflight(client):
    resp = await client.options(
        "/",
        headers={
            "Origin": "https://tryolabs.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert resp.status_code == 200
    assert "access-control-allow-origin" in resp.headers


@pytest.mark.anyio
async def test_cors_header_on_post(client):
    resp = await client.post(
        "/", json=VALID_PAYLOAD, headers={"Origin": "https://tryolabs.com", **SECRET_HEADER}
    )
    assert resp.headers.get("access-control-allow-origin") == "*"


# --- Method tests ---


@pytest.mark.anyio
async def test_get_not_allowed(client):
    resp = await client.get("/")
    assert resp.status_code == 405
