from fastapi.testclient import TestClient

from main import app, DEFAULT_SETTINGS_PASSWORD


def test_default_settings_password_allows_login():
    client = TestClient(app)
    resp = client.post("/settings-login/", json={"password": DEFAULT_SETTINGS_PASSWORD})
    assert resp.status_code == 200

