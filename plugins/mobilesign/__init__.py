from fastapi import Request, Body
from fastapi.responses import HTMLResponse, JSONResponse
import uuid, qrcode, io, base64, os, json

__all__ = ['register']

def register(app, utils):
    load_settings = utils['load_settings']
    get_session_dir = utils['get_session_dir']
    signatures_dir = utils['SIGNATURES_DIR']

    @app.post('/start-sign/')
    async def start_sign(request: Request, data: dict = Body(...)):
        """Begin a mobile signing session for a specific page."""
        settings = load_settings()
        if settings.get('license_level', 'free') == 'free':
            return JSONResponse(status_code=403, content={'message': 'Pro required'})
        img = data.get('image')
        page = int(data.get('page', 0))
        images = data.get('images') if isinstance(data.get('images'), list) else None
        points = data.get('points') if isinstance(data.get('points'), dict) else {}
        if images:
            if len(images) == 0:
                return JSONResponse(status_code=400, content={'message': 'No image supplied'})
        elif not img:
            return JSONResponse(status_code=400, content={'message': 'No image supplied'})
        else:
            images = [img]
        token = uuid.uuid4().hex
        info = {
            'session': request.cookies.get('session_id'),
            'page': page,
            'image': img,
            'images': images,
            'points': points,
            'signed': False,
            'signatures': [],
        }
        os.makedirs(signatures_dir, exist_ok=True)
        with open(os.path.join(signatures_dir, f'{token}.json'), 'w') as fh:
            json.dump(info, fh)
        settings_data = load_settings()
        settings_public = settings_data.get('public_url')
        base = os.getenv('DOCROPPER_PUBLIC_URL') or settings_public
        if not base and settings_data.get('demo_full_mode'):
            base = 'https://doccropper.iltuoconsulenteit.it'
        if not base:
            host = request.headers.get('x-forwarded-host') or request.headers.get('host')
            scheme = request.headers.get('x-forwarded-proto') or request.url.scheme
            visitor = request.headers.get('cf-visitor')
            if visitor:
                try:
                    scheme = json.loads(visitor).get('scheme', scheme)
                except Exception:
                    pass
            if host:
                base = f'{scheme}://{host}'
            else:
                base = str(request.base_url).rstrip('/')
        url = f'{base}/sign/{token}'
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
        images = info.get('images') or [img_b64]
        points = info.get('points') or {}
        page_index = int(info.get('page', 0))
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
        <p style='font-size:small;color:#a00;margin-top:5px;font-weight:bold'>DocCropper e i suoi autori declinano ogni responsabilità per un uso non conforme alla legge.<br>DocCropper and its authors accept no liability for illegal use.</p>
        <p id='finishMsg' style='display:none;color:green;font-weight:bold'></p>
        <p>Tap the document then draw your signature</p>
        <select id='pageSelect' style='margin-top:10px'></select>
        <div id='container'>
            <img id='docImg' src='{img}' alt='doc'>
            <canvas id='overlay'></canvas>
        </div><br>
        <canvas id='pad'></canvas><br>
        <div id='controls' style='display:none;'>
            <button id='clear'>Clear</button>
            <button id='submit'>Add</button>
            <label style='margin-left:10px;'>Scale:
                <input type='range' id='scaleRange' min='0.5' max='2' step='0.1' value='1'>
            </label>
            <button id='finish'>Finish</button>
        </div>
        <div style='margin-top:20px;'><img src='/static/logos/footer_logo.png' style='max-width:120px' alt='IlTuoConsulenteIT'></div>
        <script>
        const padEl=document.getElementById('pad');
        const overlay=document.getElementById('overlay');
        const controls=document.getElementById('controls');
        const docImg=document.getElementById('docImg');
        const pageSelect=document.getElementById('pageSelect');
        const submitBtn=document.getElementById('submit');
        const clearBtn=document.getElementById('clear');
        const finishBtn=document.getElementById('finish');
        const scaleInput=document.getElementById('scaleRange');
        let scale=1;
        if(scaleInput){
            scaleInput.oninput=()=>{ scale=parseFloat(scaleInput.value); };
        }
        const images={images_json};
        const spots={spots_json};
        async function loadPages(){
            try{
                const resp=await fetch('/sign-pages/{token}');
                if(resp.ok){
                    const data=await resp.json();
                    if(Array.isArray(data.images)){
                        images.splice(0,images.length,...data.images);
                    }
                }
            }catch{}
            images.forEach((img,idx)=>{const opt=document.createElement('option');opt.value=idx;opt.textContent=(idx+1);pageSelect.appendChild(opt);});
            pageSelect.value={page};
            docImg.src=images[pageSelect.value];
            drawSpots();
        }
        loadPages();
        let pos=null;
        let finished=false;
        function resize(){
            padEl.width=window.innerWidth*0.9; padEl.height=200;
            overlay.width=docImg.clientWidth; overlay.height=docImg.clientHeight;
        }
        resize(); window.addEventListener('resize',resize);
        const pad=new SignaturePad(padEl);
        function drawSpots(){
            const ctx=overlay.getContext('2d');
            ctx.clearRect(0,0,overlay.width,overlay.height);
            const list=spots[pageSelect.value]||[];
            ctx.strokeStyle='#f00';
            ctx.lineWidth=2;
            list.forEach(pt=>{const x=pt.x*overlay.width;const y=pt.y*overlay.height;ctx.beginPath();ctx.moveTo(x-10,y);ctx.lineTo(x+10,y);ctx.moveTo(x,y-10);ctx.lineTo(x,y+10);ctx.stroke();});
        }
        pageSelect.onchange=()=>{ docImg.src=images[pageSelect.value]; drawSpots(); pos=null; };
        docImg.onclick=e=>{ if(finished) return; const r=e.target.getBoundingClientRect(); pos={x:(e.clientX-r.left)/r.width,y:(e.clientY-r.top)/r.height}; padEl.style.display='block'; controls.style.display='block'; };
        clearBtn.onclick=()=>pad.clear();
        async function submitCurrent(){
            if(!pos||pad.isEmpty())return false;
            const img=pad.toDataURL('image/png');
            await fetch('/submit-signature/{token}',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image:img,x:pos.x,y:pos.y,page:parseInt(pageSelect.value),scale})});
            const ctx=overlay.getContext('2d');
            const tmp=new Image();
            tmp.onload=()=>{
                const w=tmp.width*(overlay.height/10)*scale/tmp.height;
                const h=overlay.height/10*scale;
                const x=pos.x*overlay.width - w/2;
                const y=pos.y*overlay.height - h/2;
                ctx.drawImage(tmp,x,y,w,h);
            };
            tmp.src=img;
            pad.clear();
            padEl.style.display='none';
            drawSpots();
            return true;
        }
        submitBtn.onclick=submitCurrent;
        const finishMsg=document.getElementById('finishMsg');
        finishBtn.onclick=async()=>{
            if(finished) return;
            if(!pad.isEmpty()) await submitCurrent();
            finishMsg.textContent='Sending signatures...';
            finishMsg.style.display='block';
            await fetch('/finish-signing/{token}',{method:'POST'});
            finishMsg.textContent='Signatures sent. You may close this page.';
            finished=true;
            finishBtn.disabled=true;
            submitBtn.disabled=true;
            clearBtn.disabled=true;
            docImg.onclick=null;
        };
        </script>
        </body></html>
        """.replace('{token}', token).replace('{img}', img_b64).replace('{images_json}', json.dumps(images)).replace('{spots_json}', json.dumps(points)).replace('{page}', str(page_index))
        return HTMLResponse(content=html)

    @app.get('/sign-pages/{token}')
    async def get_sign_pages(token: str):
        info_path = os.path.join(signatures_dir, f'{token}.json')
        if not os.path.exists(info_path):
            return JSONResponse(status_code=404, content={'message': 'Not found'})
        with open(info_path, 'r') as fh:
            info = json.load(fh)
        images = info.get('images') or [info.get('image', '')]
        return {'images': images}

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
            'y': float(data.get('y', 0.5)),
            'page': int(data.get('page', info.get('page', 0))),
            'scale': float(data.get('scale', 1.0))
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
        pages = {}
        for sig in info.get('signatures', []):
            with open(sig['image_path'], 'rb') as fh:
                b64 = base64.b64encode(fh.read()).decode()
            page = sig.get('page', info.get('page', 0))
            pages.setdefault(page, []).append({'image': 'data:image/png;base64,' + b64, 'x': sig['x'], 'y': sig['y'], 'scale': sig.get('scale', 1.0)})
        return {'signatures': pages}
