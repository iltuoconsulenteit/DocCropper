import importlib
import os
import sys


sys.path.insert(0, os.getcwd())


def test_dev_license_from_env(monkeypatch):
    monkeypatch.setenv("DOCROPPER_DEV_LICENSE", "AAA")
    import license_utils
    importlib.reload(license_utils)
    assert license_utils.get_dev_license_key() == "AAA"

    monkeypatch.setenv("DOCROPPER_DEV_LICENSE", "BBB")
    assert license_utils.get_dev_license_key() == "BBB"
