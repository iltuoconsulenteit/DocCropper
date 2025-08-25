import os
import importlib

import main


def test_env_developer_enables_plugins(monkeypatch):
    monkeypatch.setenv('DOCROPPER_DEV_LICENSE', 'AAA')
    cfg = {
        'license_level': 'free',
        'license_key': '',
        'enable_pageselect': True,
        'pageselect_dev_only': True,
    }
    # reload main to ensure environment variable considered if needed
    importlib.reload(main)
    active = main.compute_active_plugins(cfg)
    assert 'pageselect' in active
