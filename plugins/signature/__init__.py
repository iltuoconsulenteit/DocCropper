from fastapi import Request, Body
from fastapi.responses import HTMLResponse, JSONResponse
import uuid, qrcode, io, base64, os, subprocess

__all__ = ['register']

def register(app, utils):
    load_settings = utils['load_settings']
    get_session_dir = utils['get_session_dir']
    get_lan_ip = utils['get_lan_ip']
    signatures_dir = utils['SIGNATURES_DIR']

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

    @app.get('/start-sign/')
    async def start_sign(request: Request):
        settings = load_settings()
        if settings.get('license_level', 'free') == 'free':
            return JSONResponse(status_code=403, content={'message': 'Pro required'})
        token = uuid.uuid4().hex
        port = int(settings.get('port', 8765))
        host = get_lan_ip()
        url = f'http://{host}:{port}/sign/{token}'
        qr_img = qrcode.make(url)
        buf = io.BytesIO()
        qr_img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode()
        return {'token': token, 'url': url, 'qr': 'data:image/png;base64,' + b64}

    @app.get('/sign/{token}', response_class=HTMLResponse)
    async def sign_page(token: str):
        html = """
        <html><head>
        <meta name='viewport' content='width=device-width,initial-scale=1.0'>
        <script src='https://cdn.jsdelivr.net/npm/signature_pad@4.1.5/dist/signature_pad.umd.min.js'></script>
        </head><body>
        <canvas id='pad' style='border:1px solid #000;width:100%;height:200px'></canvas>
        <button id='clear'>Clear</button>
        <button id='submit'>Submit</button>
        <script>
        const canvas=document.getElementById('pad');
        function resize(){
            canvas.width=window.innerWidth*0.9;
            canvas.height=200;
        }
        resize();window.addEventListener('resize',resize);
        const pad=new SignaturePad(canvas);
        document.getElementById('clear').onclick=()=>pad.clear();
        document.getElementById('submit').onclick=async()=>{
            if(pad.isEmpty())return;
            const img=pad.toDataURL('image/png');
            await fetch('/submit-signature/{}', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({image:img})});
            document.body.innerHTML='<p>Signature saved. You may close this page.</p>';
        };
        </script>
        </body></html>
        """.format(token)
        return HTMLResponse(content=html)

    @app.post('/submit-signature/{token}')
    async def submit_signature(token: str, data: dict = Body(...)):
        settings = load_settings()
        if settings.get('license_level', 'free') == 'free':
            return JSONResponse(status_code=403, content={'message': 'Pro required'})
        img_b64 = data.get('image')
        if not img_b64:
            return JSONResponse(status_code=400, content={'message': 'No image'})
        if img_b64.startswith('data:'):
            img_b64 = img_b64.split(',',1)[1]
        try:
            img_bytes = base64.b64decode(img_b64)
        except Exception:
            return JSONResponse(status_code=400, content={'message': 'Invalid image'})
        os.makedirs(signatures_dir, exist_ok=True)
        path = os.path.join(signatures_dir, f'signature_{token}.png')
        with open(path, 'wb') as fh:
            fh.write(img_bytes)
        return {'status': 'ok'}
