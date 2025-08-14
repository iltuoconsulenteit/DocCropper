from fastapi import Request
from fastapi.responses import JSONResponse
import os, subprocess, base64, json, urllib.request

__all__ = ['register']

def register(app, utils):
    load_settings = utils['load_settings']
    get_session_dir = utils['get_session_dir']
    decrypt_file = utils['decrypt_file']
    encrypt_bytes = utils['encrypt_bytes']
    ENC_SUFFIX = utils['ENC_SUFFIX']

    @app.post('/remote-sign/')
    async def remote_sign(request: Request):
        session_id = request.cookies.get('session_id')
        session_dir = get_session_dir(session_id)
        pdf_path = os.path.join(session_dir, 'output.pdf' + ENC_SUFFIX)
        if not os.path.exists(pdf_path):
            return JSONResponse(status_code=404, content={'message': 'PDF not found'})
        remote_cmd = os.environ.get('DOCROPPER_REMOTE_SIGN_CMD')
        if not remote_cmd:
            return JSONResponse(status_code=400, content={'message': 'Remote signing not configured'})
        try:
            tmp_in = pdf_path + '.tmp'
            with open(tmp_in, 'wb') as fh:
                data = decrypt_file(session_id, pdf_path)
                if data is None:
                    return JSONResponse(status_code=500, content={'message': 'Decrypt failed'})
                fh.write(data)
            tmp_out = tmp_in.replace('.tmp', '_signed.tmp')
            subprocess.run([remote_cmd, tmp_in, tmp_out], check=True)
            with open(tmp_out, 'rb') as fh:
                pdf_bytes = fh.read()
            enc = encrypt_bytes(session_id, pdf_bytes)
            with open(pdf_path, 'wb') as fh:
                fh.write(enc)
            os.remove(tmp_in)
            os.remove(tmp_out)
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            return {'pdf': 'data:application/pdf;base64,' + pdf_base64}
        except Exception:
            return JSONResponse(status_code=500, content={'message': 'Remote signing failed'})

    @app.post('/docuseal-sign/')
    async def docuseal_sign(request: Request):
        session_id = request.cookies.get('session_id')
        session_dir = get_session_dir(session_id)
        pdf_path = os.path.join(session_dir, 'output.pdf' + ENC_SUFFIX)
        if not os.path.exists(pdf_path):
            return JSONResponse(status_code=404, content={'message': 'PDF not found'})
        settings = load_settings()
        api_url = settings.get('docuseal_api_url') or os.getenv('DOCUSEAL_API_URL')
        api_key = settings.get('docuseal_api_key') or os.getenv('DOCUSEAL_API_KEY')
        if not api_url or not api_key:
            return JSONResponse(status_code=400, content={'message': 'Docuseal not configured'})
        try:
            data = decrypt_file(session_id, pdf_path)
            if data is None:
                return JSONResponse(status_code=500, content={'message': 'Decrypt failed'})
            req = urllib.request.Request(api_url, data=data, method='POST')
            req.add_header('Authorization', f'Bearer {api_key}')
            req.add_header('Content-Type', 'application/pdf')
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_data = resp.read()
            resp_json = json.loads(resp_data.decode())
            url = resp_json.get('url') or resp_json.get('sign_url')
            if not url:
                raise ValueError('no url')
            return {'url': url}
        except Exception:
            return JSONResponse(status_code=500, content={'message': 'Docuseal request failed'})
