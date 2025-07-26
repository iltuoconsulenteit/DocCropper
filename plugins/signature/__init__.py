from fastapi import Request, Body
from fastapi.responses import HTMLResponse, JSONResponse
import uuid, qrcode, io, base64, os, subprocess, json, urllib.request

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

    @app.post('/start-sign/')
    async def start_sign(request: Request, data: dict = Body(...)):
        """Begin a mobile signing session for a specific page."""
        settings = load_settings()
        if settings.get('license_level', 'free') == 'free':
            return JSONResponse(status_code=403, content={'message': 'Pro required'})
        img = data.get('image')
        page = int(data.get('page', 0))
        if not img:
            return JSONResponse(status_code=400, content={'message': 'No image supplied'})
        token = uuid.uuid4().hex
        info = {
            'session': request.cookies.get('session_id'),
            'page': page,
            'image': img,
            'signed': False,
            'signatures': [],
        }
        os.makedirs(signatures_dir, exist_ok=True)
        with open(os.path.join(signatures_dir, f'{token}.json'), 'w') as fh:
            json.dump(info, fh)
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
        info_path = os.path.join(signatures_dir, f'{token}.json')
        if not os.path.exists(info_path):
            return HTMLResponse('<p>Invalid token</p>', status_code=404)
        with open(info_path, 'r') as fh:
            info = json.load(fh)
        img_b64 = info.get('image', '')
        html = """
        <html><head>
        <meta name='viewport' content='width=device-width,initial-scale=1.0'>
        <style>
        body{ text-align:center;font-family:sans-serif; }
        #container{ position:relative; display:inline-block; }
        #docImg{ max-width:100%; height:auto; display:block; }
        #overlay{ position:absolute; left:0; top:0; pointer-events:none; }
        #pad{ border:1px solid #000; display:none; margin-top:10px; width:100%; height:200px }
        </style>
        <script src='https://cdn.jsdelivr.net/npm/signature_pad@4.1.5/dist/signature_pad.umd.min.js'></script>
        </head><body>
        <img src='/static/logos/header_logo.png' style='max-width:150px;margin-top:10px' alt='DocCropper'>
        <p>Tap the document then draw your signature</p>
        <div id='container'>
            <img id='docImg' src='{img}' alt='doc'>
            <canvas id='overlay'></canvas>
        </div><br>
        <canvas id='pad'></canvas><br>
        <div id='controls' style='display:none;'>
            <button id='clear'>Clear</button>
            <button id='submit'>Add</button>
            <button id='finish'>Finish</button>
        </div>
        <div style='margin-top:20px;'><img src='/static/logos/footer_logo.png' style='max-width:120px' alt='IlTuoConsulenteIT'></div>
        <script>
        const padEl=document.getElementById('pad');
        const overlay=document.getElementById('overlay');
        const controls=document.getElementById('controls');
        const docImg=document.getElementById('docImg');
        let pos=null;
        function resize(){
            padEl.width=window.innerWidth*0.9; padEl.height=200;
            overlay.width=docImg.clientWidth; overlay.height=docImg.clientHeight;
        }
        resize(); window.addEventListener('resize',resize);
        const pad=new SignaturePad(padEl);
        docImg.onclick=e=>{ const r=e.target.getBoundingClientRect(); pos={x:(e.clientX-r.left)/r.width,y:(e.clientY-r.top)/r.height}; padEl.style.display='block'; controls.style.display='block'; };
        document.getElementById('clear').onclick=()=>pad.clear();
        document.getElementById('submit').onclick=async()=>{
            if(!pos||pad.isEmpty())return;
            const img=pad.toDataURL('image/png');
            await fetch('/submit-signature/{token}',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image:img,x:pos.x,y:pos.y})});
            const ctx=overlay.getContext('2d');
            const tmp=new Image();
            tmp.onload=()=>{
                const w=tmp.width*(overlay.height/10)/tmp.height;
                const h=overlay.height/10;
                const x=pos.x*overlay.width - w/2;
                const y=pos.y*overlay.height - h/2;
                ctx.drawImage(tmp,x,y,w,h);
            };
            tmp.src=img;
            pad.clear();
            padEl.style.display='none';
        };
        document.getElementById('finish').onclick=async()=>{
            await fetch('/finish-signing/{token}',{method:'POST'});
            document.body.innerHTML='<p>Signature saved. You may close this page.</p>';
        };
        </script>
        </body></html>
        """.replace('{token}', token).replace('{img}', img_b64)
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
        info_path = os.path.join(signatures_dir, f'{token}.json')
        if os.path.exists(info_path):
            with open(info_path, 'r') as fh:
                info = json.load(fh)
        else:
            info = {}
        sig_idx = len(info.get('signatures', []))
        img_path = os.path.join(signatures_dir, f'signature_{token}_{sig_idx}.png')
        with open(img_path, 'wb') as fh:
            fh.write(img_bytes)
        sig_entry = {
            'image_path': img_path,
            'x': float(data.get('x', 0.5)),
            'y': float(data.get('y', 0.5))
        }
        info.setdefault('signatures', []).append(sig_entry)
        info['signed'] = False
        with open(info_path, 'w') as fh:
            json.dump(info, fh)
        return {'status': 'ok'}

    @app.post('/finish-signing/{token}')
    async def finish_signing(token: str):
        info_path = os.path.join(signatures_dir, f'{token}.json')
        if not os.path.exists(info_path):
            return JSONResponse(status_code=404, content={'message': 'Not found'})
        with open(info_path, 'r') as fh:
            info = json.load(fh)
        info['signed'] = True
        with open(info_path, 'w') as fh:
            json.dump(info, fh)
        return {'status': 'ok'}

    @app.get('/signature-result/{token}')
    async def signature_result(token: str):
        info_path = os.path.join(signatures_dir, f'{token}.json')
        if not os.path.exists(info_path):
            return JSONResponse(status_code=404, content={'message': 'Not found'})
        with open(info_path, 'r') as fh:
            info = json.load(fh)
        if not info.get('signed'):
            return JSONResponse(status_code=202, content={'message': 'Pending'})
        sigs = []
        for sig in info.get('signatures', []):
            with open(sig['image_path'], 'rb') as fh:
                b64 = base64.b64encode(fh.read()).decode()
            sigs.append({'image': 'data:image/png;base64,' + b64, 'x': sig['x'], 'y': sig['y']})
        return {'page': info.get('page', 0), 'signatures': sigs}
