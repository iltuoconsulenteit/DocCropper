import main

def test_dev_license_key_enables_plugins():
    cfg = {
        'license_level': 'free',
        'license_key': 'AAA-DEV',
        'enable_pageselect': True,
        'pageselect_dev_only': True,
    }
    active = main.compute_active_plugins(cfg)
    assert 'pageselect' in active
