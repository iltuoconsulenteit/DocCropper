import json
import os
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
