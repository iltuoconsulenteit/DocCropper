import asyncio
from pathlib import Path
import pytest

# Extract settings_login function source without importing heavy dependencies
source = Path('services/api/app.py').read_text().splitlines()
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
# Compile the function in isolated namespace
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
        return hashed == 'hash-' + pwd

bcrypt = DummyBcrypt()
DEFAULT_SETTINGS_PASSWORD = '12345678'

def load_settings():
    return {'settings_password_hash': bcrypt.hash(DEFAULT_SETTINGS_PASSWORD)}

ns = {
    'bcrypt': bcrypt,
    'DEFAULT_SETTINGS_PASSWORD': DEFAULT_SETTINGS_PASSWORD,
    'load_settings': load_settings,
    'HTTPException': HTTPException,
}
exec(func_src, ns)
settings_login = ns['settings_login']


def test_settings_login_accepts_default_password():
    result = asyncio.run(settings_login({'password': '12345678'}))
    assert result['status'] == 'ok'


def test_settings_login_rejects_wrong_password():
    with pytest.raises(HTTPException) as exc:
        asyncio.run(settings_login({'password': 'wrong'}))
    assert exc.value.status_code == 403
