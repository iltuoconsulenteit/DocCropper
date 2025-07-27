from fastapi import Request
from fastapi.responses import JSONResponse
import os, subprocess, base64, json, urllib.request

__all__ = ['register']

def register(app, utils):
    load_settings = utils['load_settings']
    get_session_dir = utils['get_session_dir']

    @app.post('/remote-sign/')
    async def remote_sign(request: Request):
        session_id = request.cookies.get('session_id')
        session_dir = get_session_dir(session_id)
        pdf_path = os.path.join(session_dir, 'output.pdf')
        if not os.path.exists(pdf_path):
            return JSONResponse(status_code=404, content={'message': 'PDF not found'})
        remote_cmd = os.environ.get('DOCROPPER_REMOTE_SIGN_CMD')
        if not remote_cmd:
            return JSONResponse(status_code=400, content={'message': 'Remote signing not configured'})
        try:
            out_path = pdf_path.replace('.pdf', '_signed.pdf')
            subprocess.run([remote_cmd, pdf_path, out_path], check=True)
            with open(out_path, 'rb') as fh:
                pdf_bytes = fh.read()
            os.replace(out_path, pdf_path)
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            return {'pdf': 'data:application/pdf;base64,' + pdf_base64}
        except Exception:
            return JSONResponse(status_code=500, content={'message': 'Remote signing failed'})

    @app.post('/docuseal-sign/')
    async def docuseal_sign(request: Request):
        session_id = request.cookies.get('session_id')
        session_dir = get_session_dir(session_id)
        pdf_path = os.path.join(session_dir, 'output.pdf')
        if not os.path.exists(pdf_path):
            return JSONResponse(status_code=404, content={'message': 'PDF not found'})
        settings = load_settings()
        api_url = settings.get('docuseal_api_url') or os.getenv('DOCUSEAL_API_URL')
        api_key = settings.get('docuseal_api_key') or os.getenv('DOCUSEAL_API_KEY')
        if not api_url or not api_key:
            return JSONResponse(status_code=400, content={'message': 'Docuseal not configured'})
        try:
            with open(pdf_path, 'rb') as fh:
                data = fh.read()
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
