import json
import main

def test_user_settings_ignores_stale_license(tmp_path, monkeypatch):
    # Use a temporary users directory
    users_dir = tmp_path / 'users'
    users_dir.mkdir()
    monkeypatch.setattr(main, 'USERS_DIR', str(users_dir))

    # Base settings contain a developer license
    def fake_load_settings():
        return {
            'license_key': 'AAA-DEV',
            'license_level': 'developer',
            'license_name': 'Developer'
        }
    monkeypatch.setattr(main, 'load_settings', fake_load_settings)

    # Create a user file with stale license data
    user_file = users_dir / 'user_at_example_com.json'
    with open(user_file, 'w') as fh:
        json.dump({'license_key': 'OLD', 'license_level': 'demo', 'foo': 1}, fh)

    data = main.load_user_settings('user@example.com')
    assert data['license_level'] == 'developer'
    assert data['license_key'] == 'AAA-DEV'
    assert data['foo'] == 1

    # Saving user settings should not persist license fields
    main.save_user_settings('user@example.com', {'license_key': 'BAD', 'bar': 2})
    with open(user_file) as fh:
        stored = json.load(fh)
    assert 'license_key' not in stored
    assert stored['bar'] == 2
