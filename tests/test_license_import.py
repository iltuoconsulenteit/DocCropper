import asyncio
import json
import os
import shutil
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

def _default_settings_block() -> str:
    lines = Path('services/api/app.py').read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith('DEFAULT_SETTINGS = {'))
    brace_depth = 0
    collected = []
    for line in lines[start:]:
        collected.append(line)
        brace_depth += line.count('{') - line.count('}')
        if brace_depth == 0:
            break
    return '\n'.join(collected)


def _build_upload(tmp_path):
    lines = Path('services/api/app.py').read_text().splitlines()
    decorator_idx = next(i for i, line in enumerate(lines) if line.strip() == '@app.post("/license/upload")')
    func_idx = decorator_idx + 1
    while func_idx < len(lines) and not lines[func_idx].startswith('async def upload_license'):
        func_idx += 1
    body = [lines[func_idx]]
    for line in lines[func_idx + 1:]:
        if line.startswith('    ') or line.strip() == '':
            body.append(line)
        else:
            break
    func_src = '\n'.join(body)

    saved_updates = []

    class DummyHTTPException(Exception):
        def __init__(self, status_code, detail=''):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class DummyJSONResponse(dict):
        def __init__(self, content, headers=None):
            super().__init__(content)
            self.headers = headers or {}

    class DummyJWTError(Exception):
        pass

    class DummyJWT:
        @staticmethod
        def decode(token, secret, algorithms):
            raise DummyJWTError('not a token')

    class DummyUpload:
        def __init__(self, payload: bytes):
            self._payload = payload

        async def read(self):
            return self._payload

    namespace = {
        'Any': Any,
        'HTTPException': DummyHTTPException,
        'JSONResponse': DummyJSONResponse,
        'UploadFile': DummyUpload,
        'Request': object,
        'File': lambda *args, **kwargs: None,
        'jwt': DummyJWT,
        'JWTError': DummyJWTError,
        'json': json,
        'os': os,
        'time': time,
        'Path': Path,
        'shutil': shutil,
        'load_env_files': lambda override=False: None,
        'save_settings': lambda update: (saved_updates.append(update), update)[1],
        'get_machine_fingerprint': lambda: 'fp-123',
        'BASE_DIR': str(tmp_path),
        'ENV_DIR': str(tmp_path / 'env'),
        'LICENSE_SECRET': 'secret',
    }

    exec(func_src, namespace)
    upload = namespace['upload_license']
    return upload, saved_updates, DummyUpload, DummyHTTPException


def test_default_settings_ship_demo_full():
    block = _default_settings_block()
    assert '"license_key": "DEMO-FULL-DC"' in block
    assert '"license_level": "full"' in block
    assert '"enable_sponsor_features": False' in block


def test_license_upload_accepts_json_file(tmp_path):
    upload, saved_updates, DummyUpload, DummyHTTPException = _build_upload(tmp_path)
    payload = {
        'license_key': 'MANUAL-123',
        'license_name': 'Manual',
        'license_type': 'manual',
        'enable_sponsor_features': True,
        'settings': {'extra_option': 'value'},
    }
    request = SimpleNamespace(client=SimpleNamespace(host='localhost'))
    result = asyncio.run(upload(request, DummyUpload(json.dumps(payload).encode('utf-8'))))
    assert result['status'] == 'saved'
    assert result['license_type'] == 'manual'
    assert saved_updates, 'save_settings should be invoked'
    update = saved_updates[-1]
    assert update['license_key'] == 'MANUAL-123'
    assert update['license_name'] == 'Manual'
    assert update['license_type'] == 'manual'
    assert update['enable_sponsor_features'] is True
    assert update['license_check'] is False
    assert update['extra_option'] == 'value'
    env_file = Path(tmp_path, 'env', 'license.env')
    assert env_file.exists()
    env_text = env_file.read_text()
    assert 'DOCROPPER_LICENSE_KEY=MANUAL-123' in env_text
    assert 'DOCROPPER_LICENSE_NAME=Manual' in env_text
