import json
import io
import base64
import main


def test_manual_license_clears_overrides(tmp_path, monkeypatch):
    settings_path = tmp_path / 'settings.json'
    overrides_path = tmp_path / 'license_overrides.json'
    settings_path.write_text(json.dumps({'license_key': 'OLD', 'license_level': 'demo'}))
    overrides_path.write_text(json.dumps({'license_key': 'OLD', 'license_level': 'demo'}))
    monkeypatch.setattr(main, 'SETTINGS_FILE', str(settings_path))
    monkeypatch.setattr(main, 'LICENSE_OVERRIDES_FILE', str(overrides_path))
    res = main.save_settings({'license_key': 'NEW-DEV', 'license_name': 'Developer'})
    assert res['license_level'] == 'developer'
    assert not overrides_path.exists()


def test_developer_level_skips_domain_check(tmp_path, monkeypatch):
    settings_path = tmp_path / 'settings.json'
    settings_path.write_text(json.dumps({'license_key': 'CUSTOM', 'license_level': 'developer', 'license_check': True}))
    monkeypatch.setattr(main, 'SETTINGS_FILE', str(settings_path))

    def fail_verify(key: str) -> bool:
        raise AssertionError('verify_license_server should not be called')

    monkeypatch.setattr(main, 'verify_license_server', fail_verify)

    from fastapi.testclient import TestClient
    from PIL import Image

    img = Image.new('RGB', (1, 1), color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_b64 = base64.b64encode(buf.getvalue()).decode()

    client = TestClient(main.app)
    r = client.post('/create-pdf/', json={'images': [img_b64]})
    assert r.status_code == 200
