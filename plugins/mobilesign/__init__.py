from fastapi import Request, Body
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import uuid, qrcode, io, base64, os, json, hashlib, logging
from datetime import datetime
import fitz

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
        name = data.get('name', '')
        email = data.get('email', '')
        phone = data.get('phone', '')
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
            'name': name,
            'email': email,
            'phone': phone,
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
        email = info.get('email', '')
        phone = info.get('phone', '')
        name = info.get('name', '')
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
        <label style='display:block;margin-top:5px;'><input type='checkbox' id='consentFlag'> Consento il trattamento dei dati</label>
        <input id='nameInput' type='text' placeholder='Nome' value='{name}' style='width:90%;max-width:300px;margin-top:5px;'>
        <input id='emailInput' type='email' placeholder='Email' value='{email}' style='width:90%;max-width:300px;margin-top:5px;'>
        <input id='phoneInput' type='tel' placeholder='Cellulare' value='{phone}' style='width:90%;max-width:300px;margin-top:5px;'>
        <p id='finishMsg' style='display:none;color:green;font-weight:bold'></p>
        <a id='pdfLink' style='display:none;margin-top:5px;' download='signed.pdf'>Download PDF</a>
        <button id='waPdfBtn' style='display:none;margin-left:10px;'>WhatsApp</button>
        <button id='emailPdfBtn' style='display:none;margin-left:10px;'>Email</button>
        <p>Tap the document then draw your signature</p>
        <label for='pageSelect' style='display:block;margin-top:10px;'>Page:</label>
        <select id='pageSelect' style='margin-top:4px'></select>
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
        const nameInput=document.getElementById('nameInput');
        const emailInput=document.getElementById('emailInput');
        const phoneInput=document.getElementById('phoneInput');
        const consentFlag=document.getElementById('consentFlag');
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
        const pdfLink=document.getElementById('pdfLink');
        const waPdfBtn=document.getElementById('waPdfBtn');
        const emailPdfBtn=document.getElementById('emailPdfBtn');
        async function pollPdf(){
            try{
                const r=await fetch('/signed-pdf/{token}',{cache:'no-store'});
                if(r.status===200){
                    const d=await r.json();
                    if(d.url){
                        pdfLink.href=d.url;
                        pdfLink.textContent='Download PDF';
                        pdfLink.style.display='block';
                        finishMsg.textContent='Signatures sent. Download your PDF:';
                        if(waPdfBtn){
                            waPdfBtn.onclick=()=>{
                                const p=(d.phone||'').replace(/[^0-9]/g,'');
                                const u=p?`https://wa.me/${p}?text=${encodeURIComponent(d.url)}`:`https://wa.me/?text=${encodeURIComponent(d.url)}`;
                                window.open(u,'_blank');
                            };
                            waPdfBtn.style.display='inline';
                        }
                        if(emailPdfBtn){
                            emailPdfBtn.onclick=()=>{
                                const m=d.email?encodeURIComponent(d.email):'';
                                const mailto=`mailto:${m}?body=${encodeURIComponent(d.url)}`;
                                window.open(mailto,'_blank');
                            };
                            emailPdfBtn.style.display='inline';
                        }
                        return;
                    }
                }
            }catch{}
            setTimeout(pollPdf,3000);
        }
        finishBtn.onclick=async()=>{
            if(finished) return;
            if(!pad.isEmpty()) await submitCurrent();
            finishMsg.textContent='Sending signatures...';
            finishMsg.style.display='block';
            await fetch('/finish-signing/{token}',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:nameInput.value||'',email:emailInput.value||'',phone:phoneInput.value||'',consent:consentFlag.checked})});
            finishMsg.textContent='Signatures sent. Waiting for PDF...';
            finished=true;
            finishBtn.disabled=true;
            submitBtn.disabled=true;
            clearBtn.disabled=true;
            docImg.onclick=null;
            pollPdf();
        };
        </script>
        </body></html>
        """.replace('{token}', token).replace('{img}', img_b64).replace('{images_json}', json.dumps(images)).replace('{spots_json}', json.dumps(points)).replace('{page}', str(page_index)).replace('{email}', email).replace('{phone}', phone).replace('{name}', name)
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
    async def finish_signing(token: str, data: dict = Body(default_factory=dict)):
        info_path = os.path.join(signatures_dir, f'{token}.json')
        if not os.path.exists(info_path):
            return JSONResponse(status_code=404, content={'message': 'Not found'})
        with open(info_path, 'r') as fh:
            info = json.load(fh)
        info['signed'] = True
        info['name'] = data.get('name','')
        info['email'] = data.get('email','')
        info['phone'] = data.get('phone','')
        info['consent'] = bool(data.get('consent', False))
        info['timestamp'] = datetime.utcnow().isoformat()
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
        result = {'signatures': pages}
        for key in ('name', 'email', 'phone', 'timestamp', 'consent'):
            if key in info:
                result[key] = info[key]
        return result

    def send_mail(to_addr: str, subject: str, body: str, attachment: str | None = None):
        settings = load_settings()
        server = os.getenv('SMTP_SERVER') or settings.get('smtp_server')
        user = os.getenv('SMTP_USER') or settings.get('smtp_user')
        password = os.getenv('SMTP_PASS') or settings.get('smtp_pass')
        port = int(os.getenv('SMTP_PORT') or settings.get('smtp_port', 587))
        sender = os.getenv('SMTP_FROM') or settings.get('smtp_from', user)
        if not (server and user and password and to_addr):
            return
        import smtplib
        from email.message import EmailMessage
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to_addr
        msg.set_content(body)
        if attachment:
            with open(attachment, 'rb') as fh:
                data = fh.read()
            msg.add_attachment(data, maintype='application', subtype='pdf', filename=os.path.basename(attachment))
        try:
            with smtplib.SMTP(server, port) as s:
                s.starttls()
                s.login(user, password)
                s.send_message(msg)
        except Exception:
            logging.exception('Email send failed')

    @app.post('/store-signed-pdf/{token}')
    async def store_signed_pdf(request: Request, token: str, data: dict = Body(...)):
        pdf_b64 = data.get('pdf')
        if not pdf_b64:
            return JSONResponse(status_code=400, content={'message': 'No PDF'})
        if pdf_b64.startswith('data:'):
            pdf_b64 = pdf_b64.split(',', 1)[1]
        try:
            pdf_bytes = base64.b64decode(pdf_b64)
        except Exception:
            return JSONResponse(status_code=400, content={'message': 'Invalid PDF'})
        info_path = os.path.join(signatures_dir, f'{token}.json')
        if not os.path.exists(info_path):
            return JSONResponse(status_code=404, content={'message': 'Not found'})
        with open(info_path, 'r') as fh:
            info = json.load(fh)
        hash_hex = hashlib.sha256(pdf_bytes).hexdigest()
        ts = info.get('timestamp') or datetime.utcnow().isoformat()
        name = info.get('name', '')
        ip = request.client.host or ''
        email = info.get('email', '')
        legal = f"Firmato elettronicamente in data {ts} da {name} con firma elettronica semplice ai sensi del Regolamento eIDAS (UE 910/2014). IP: {ip} | Email: {email} | SHA256: {hash_hex}"
        try:
            doc = fitz.open(stream=pdf_bytes, filetype='pdf')
            page = doc[-1]
            rect = fitz.Rect(50, page.rect.height - 40, page.rect.width - 50, page.rect.height - 10)
            page.insert_textbox(rect, legal, fontsize=8, align=1)
            pdf_bytes = doc.tobytes()
            doc.close()
        except Exception:
            logging.exception('Failed to append legal text')
        pdf_path = os.path.join(signatures_dir, f'signed_{token}.pdf')
        with open(pdf_path, 'wb') as fh:
            fh.write(pdf_bytes)
        url = request.url_for('download_signed_pdf', token=token)
        info['pdf_file'] = pdf_path
        info['pdf_url'] = str(url)
        info['pdf_hash'] = hash_hex
        with open(info_path, 'w') as fh:
            json.dump(info, fh)
        log_entry = {
            'token': token,
            'pdf_file': os.path.basename(pdf_path),
            'hash': hash_hex,
            'timestamp': ts,
            'ip': ip,
            'user_agent': request.headers.get('user-agent', ''),
            'email': email,
            'name': name,
            'consent': info.get('consent', False)
        }
        os.makedirs('log_firme', exist_ok=True)
        with open(os.path.join('log_firme', f'firma_{token}.json'), 'w') as fh:
            json.dump(log_entry, fh, indent=2)
        if email:
            send_mail(email, 'Documento firmato', f'SHA256: {hash_hex}', pdf_path)
        return {'status': 'ok', 'url': str(url)}

    @app.get('/signed-pdf/{token}')
    async def signed_pdf(request: Request, token: str):
        info_path = os.path.join(signatures_dir, f'{token}.json')
        if not os.path.exists(info_path):
            return JSONResponse(status_code=404, content={'message': 'Not found'})
        with open(info_path, 'r') as fh:
            info = json.load(fh)
        pdf_url = info.get('pdf_url')
        result = {}
        if pdf_url:
            result['url'] = pdf_url
        else:
            pdf_path = info.get('pdf_file')
            if not pdf_path or not os.path.exists(pdf_path):
                return JSONResponse(status_code=202, content={'message': 'Pending'})
            url = request.url_for('download_signed_pdf', token=token)
            result['url'] = str(url)
        for key in ('name', 'email', 'phone'):
            if key in info:
                result[key] = info[key]
        return result

    @app.get('/download-signed/{token}.pdf', name='download_signed_pdf')
    async def download_signed_pdf(token: str):
        pdf_path = os.path.join(signatures_dir, f'signed_{token}.pdf')
        if not os.path.exists(pdf_path):
            return JSONResponse(status_code=404, content={'message': 'Not found'})
        return FileResponse(pdf_path, media_type='application/pdf', filename=f'signed_{token}.pdf', headers={"Cache-Control": "no-cache"})
