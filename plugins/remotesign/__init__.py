from fastapi import Request
from fastapi.responses import JSONResponse
import os, subprocess, base64

__all__ = ['register']

def register(app, utils):
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

