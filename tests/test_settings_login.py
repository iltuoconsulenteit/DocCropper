import asyncio
import logging
import secrets
from pathlib import Path

import pytest

# Extract settings_login function source without importing heavy dependencies
source = Path('services/api/app.py').read_text().splitlines()
helper_start = next(i for i, line in enumerate(source) if line.startswith('def _verify_settings_password'))
helper_lines = [source[helper_start]]
for line in source[helper_start + 1:]:
    if line.startswith('    ') or line.strip() == '':
        helper_lines.append(line)
    else:
        break
helper_src = '\n'.join(helper_lines)

start = source.index('@app.post("/settings-login/")') + 2
body_lines = []
for line in source[start:]:
    if line.startswith('    '):
        body_lines.append(line)
    elif line.strip() == '':
        body_lines.append(line)
    else:
        break
func_src = "async def settings_login(data: dict = None):\n" + "\n".join(body_lines)

class HTTPException(Exception):
    def __init__(self, status_code, detail=""):
        self.status_code = status_code
        self.detail = detail

class DummyBcrypt:
    @staticmethod
    def hash(pwd: str) -> str:
        return 'hash-' + pwd

    @staticmethod
    def verify(pwd: str, hashed: str) -> bool:
        if not DummyBcrypt.identify(hashed):
            raise ValueError('invalid hash')
        return hashed == 'hash-' + pwd

    @staticmethod
    def identify(value) -> bool:
        return isinstance(value, str) and value.startswith('hash-')

bcrypt = DummyBcrypt()
DEFAULT_SETTINGS_PASSWORD = '12345678'


def build_func(load_settings):
    ns = {
        'bcrypt': bcrypt,
        'DEFAULT_SETTINGS_PASSWORD': DEFAULT_SETTINGS_PASSWORD,
        'load_settings': load_settings,
        'HTTPException': HTTPException,
        'logging': logging,
        'secrets': secrets,
    }
    exec(helper_src, ns)
    exec(func_src, ns)
    return ns['settings_login']


def test_settings_login_accepts_plain_password():
    func = build_func(lambda: {'settings_password': 'custom'})
    result = asyncio.run(func({'password': 'custom'}))
    assert result['status'] == 'ok'


def test_settings_login_accepts_default_when_unset():
    func = build_func(lambda: {})
    result = asyncio.run(func({'password': '12345678'}))
    assert result['status'] == 'ok'


def test_settings_login_rejects_wrong_password():
    func = build_func(lambda: {})
    with pytest.raises(HTTPException) as exc:
        asyncio.run(func({'password': 'wrong'}))
    assert exc.value.status_code == 403


def test_settings_login_accepts_default_when_hash_corrupted():
    func = build_func(lambda: {'settings_password_hash': 'broken'})
    result = asyncio.run(func({'password': '12345678'}))
    assert result['status'] == 'ok'


def test_settings_login_accepts_hash_only_configuration():
    func = build_func(lambda: {'settings_password_hash': bcrypt.hash('custom')})
    result = asyncio.run(func({'password': 'custom'}))
    assert result['status'] == 'ok'


def test_settings_login_rejects_default_when_custom_password_present():
    func = build_func(lambda: {'settings_password': 'custom'})
    with pytest.raises(HTTPException) as exc:
        asyncio.run(func({'password': '12345678'}))
    assert exc.value.status_code == 403
