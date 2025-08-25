from fastapi import Request, Body
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import uuid, qrcode, io, base64, os, json, hashlib, logging
from datetime import datetime

__all__ = ['register']

def register(app, utils):
    load_settings = utils['load_settings']
    get_session_dir = utils['get_session_dir']
    signatures_dir = utils['SIGNATURES_DIR']

    import importlib
    fitz_mod = None

    def get_fitz():
        nonlocal fitz_mod
        if fitz_mod is None:
            fitz_mod = importlib.import_module('fitz')
        return fitz_mod

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
        <script src='https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js'></script>
        </head><body>
        <img src='/static/logos/header_logo.png' style='max-width:150px;margin-top:10px' alt='DocCropper'>
        <p style='font-size:small;color:#a00;margin-top:5px;font-weight:bold'>DocCropper e i suoi autori declinano ogni responsabilità per un uso non conforme alla legge.<br>DocCropper and its authors accept no liability for illegal use.</p>
        <label for='pageSelect' style='display:block;margin-top:10px;'>Page:</label>
        <select id='pageSelect' style='margin-top:4px'></select>
        <label style='display:block;margin-top:5px;'><input type='checkbox' id='consentFlag'> Consento il trattamento dei dati</label>
        <input id='nameInput' type='text' placeholder='Nome' value='{name}' style='width:90%;max-width:300px;margin-top:5px;'>
        <input id='emailInput' type='email' placeholder='Email' value='{email}' style='width:90%;max-width:300px;margin-top:5px;'>
        <input id='phoneInput' type='tel' placeholder='Cellulare' value='{phone}' style='width:90%;max-width:300px;margin-top:5px;'>
        <p id='finishMsg' style='display:none;color:green;font-weight:bold'></p>
        <a id='pdfLink' style='display:none;margin-top:5px;' download='signed.pdf'>Download PDF</a>
        <button id='waPdfBtn' style='display:none;margin-left:10px;'>WhatsApp</button>
        <button id='emailPdfBtn' style='display:none;margin-left:10px;'>Email</button>
        <p>Tap the document then draw your signature</p>
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
        <div style='margin-top:20px;text-align:center;'>
            <a href='https://www.iltuoconsulenteit.it/site/index.php/applicazioni/doccropper' target='_blank' style='display:inline-flex;flex-direction:column;align-items:center;text-decoration:none;color:inherit;'>
                <span style='font-size:12px;margin-bottom:4px;'>By IlTuoConsulenteIT</span>
                <img src='/static/logos/footer_logo.png' style='max-height:30px' alt='IlTuoConsulenteIT'>
            </a>
        </div>
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
        const container=document.getElementById('container');
        let scale=1;
        let activeSign=null;
        if(scaleInput){
            scaleInput.oninput=()=>{
                scale=parseFloat(scaleInput.value);
                if(activeSign){
                    activeSign.scale=scale;
                    positionAllSigns();
                }
            };
        }
        const images={images_json};
        const spots={spots_json};
        const signs=[];
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
            docImg.onload=()=>{resize(); drawSpots(); positionAllSigns();};
            docImg.src=images[pageSelect.value];
        }
        loadPages();
        let pos=null;
        let finished=false;
        function resize(){
            padEl.width=window.innerWidth*0.9; padEl.height=200;
            overlay.width=docImg.clientWidth; overlay.height=docImg.clientHeight;
            positionAllSigns();
        }
        window.addEventListener('resize',resize);
        const pad=new SignaturePad(padEl);
        function drawSpots(){
            const ctx=overlay.getContext('2d');
            ctx.clearRect(0,0,overlay.width,overlay.height);
            const list=spots[pageSelect.value]||[];
            ctx.strokeStyle='#f00';
            ctx.lineWidth=2;
            list.forEach(pt=>{const x=pt.x*overlay.width;const y=pt.y*overlay.height;ctx.beginPath();ctx.moveTo(x-10,y);ctx.lineTo(x+10,y);ctx.moveTo(x,y-10);ctx.lineTo(x,y+10);ctx.stroke();});
        }
        function positionAllSigns(){
            const rect=docImg.getBoundingClientRect();
            signs.forEach(s=>{
                const h=rect.height/10*s.scale;
                const w=h*(s.ratio||1);
                const x=s.x*rect.width - w/2;
                const y=s.y*rect.height - h/2;
                s.element.style.width=w+'px';
                s.element.style.height=h+'px';
                s.element.style.left=x+'px';
                s.element.style.top=y+'px';
                s.element.style.display = (s.page==parseInt(pageSelect.value)) ? 'block':'none';
            });
        }
        function makeDraggable(el,s){
            let sx=0, sy=0, dragging=false;
            el.addEventListener('pointerdown',e=>{
                dragging=true; sx=e.clientX; sy=e.clientY; el.setPointerCapture(e.pointerId);
                activeSign=s;
                if(scaleInput){ scaleInput.value=s.scale; }
                scale=s.scale;
            });
            el.addEventListener('pointermove',e=>{
                if(!dragging) return; const dx=e.clientX-sx; const dy=e.clientY-sy; const left=parseFloat(el.style.left)+dx; const top=parseFloat(el.style.top)+dy; el.style.left=left+'px'; el.style.top=top+'px'; const rect=docImg.getBoundingClientRect(); s.x=(left+el.offsetWidth/2)/rect.width; s.y=(top+el.offsetHeight/2)/rect.height; sx=e.clientX; sy=e.clientY;
            });
            el.addEventListener('pointerup',e=>{ dragging=false; el.releasePointerCapture(e.pointerId); });
        }
        pageSelect.onchange=()=>{ docImg.onload=()=>{resize(); drawSpots(); positionAllSigns();}; docImg.src=images[pageSelect.value]; pos=null; };
        docImg.onclick=e=>{ if(finished) return; const r=e.target.getBoundingClientRect(); pos={x:(e.clientX-r.left)/r.width,y:(e.clientY-r.top)/r.height}; padEl.style.display='block'; controls.style.display='block'; };
        clearBtn.onclick=()=>pad.clear();
        function placeCurrent(){
            if(!pos||pad.isEmpty())return false;
            const img=pad.toDataURL('image/png');
            const sign={img,x:pos.x,y:pos.y,scale:scale,page:parseInt(pageSelect.value)};
            const el=new Image();
            el.src=img; el.style.position='absolute'; el.style.touchAction='none';
            sign.element=el;
            el.onload=()=>{ sign.ratio=el.width/el.height; positionAllSigns(); };
            makeDraggable(el,sign);
            container.appendChild(el);
            signs.push(sign);
            pad.clear();
            padEl.style.display='none';
            drawSpots();
            activeSign=sign;
            if(scaleInput){ scaleInput.value=sign.scale; }
            return true;
        }
        submitBtn.onclick=placeCurrent;
        const finishMsg=document.getElementById('finishMsg');
        const pdfLink=document.getElementById('pdfLink');
        const waPdfBtn=document.getElementById('waPdfBtn');
        const emailPdfBtn=document.getElementById('emailPdfBtn');

        function loadImage(src){
            return new Promise((res,rej)=>{const i=new Image();i.onload=()=>res(i);i.onerror=rej;i.src=src;});
        }

        async function generatePdf(){
            try{
                const { jsPDF } = window.jspdf || {};
                if(!jsPDF) throw new Error('jsPDF missing');
                const imgs=[];
                for(const src of images){ imgs.push(await loadImage(src)); }
                const pdf=new jsPDF({orientation:'p',unit:'px',format:[imgs[0].width,imgs[0].height]});
                imgs.forEach((img,idx)=>{
                    if(idx>0) pdf.addPage([img.width,img.height]);
                    const c=document.createElement('canvas');
                    c.width=img.width; c.height=img.height;
                    c.getContext('2d').drawImage(img,0,0);
                    const jpg=c.toDataURL('image/jpeg',0.85);
                    pdf.addImage(jpg,'JPEG',0,0,img.width,img.height,'','FAST');
                    signs.filter(s=>s.page===idx).forEach(s=>{
                        const h=img.height/10*s.scale;
                        const w=h*(s.ratio||1);
                        const x=s.x*img.width - w/2;
                        const y=s.y*img.height - h/2;
                        pdf.addImage(s.img,'PNG',x,y,w,h);
                    });
                });
                const data=pdf.output('datauristring');
                const r=await fetch('/store-signed-pdf/{token}',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pdf:data})});
                if(r.ok){
                    const d=await r.json();
                    if(d.url&&d.hash){
                        try{
                            const fr=await fetch(d.url);
                            const buf=await fr.arrayBuffer();
                            const digest=await crypto.subtle.digest('SHA-256',buf);
                            const hash=Array.from(new Uint8Array(digest)).map(b=>b.toString(16).padStart(2,'0')).join('');
                            if(hash!==d.hash){
                                finishMsg.textContent='Hash mismatch';
                                return;
                            }
                        }catch{}
                        pdfLink.href=d.url;
                        pdfLink.textContent='Download PDF';
                        pdfLink.style.display='block';
                        finishMsg.textContent='Signatures sent. SHA256: '+d.hash;
                        if(waPdfBtn){
                            waPdfBtn.onclick=()=>{
                                const p=(phoneInput.value||'').replace(/[^0-9]/g,'');
                                const params=new URLSearchParams({text:d.url});
                                if(p) params.set('phone',p);
                                const u=`https://web.whatsapp.com/send?${params.toString()}`;
                                window.open(u,'_blank');
                            };
                            waPdfBtn.style.display='inline';
                        }
                        if(emailPdfBtn){
                            emailPdfBtn.onclick=()=>{
                                const m=emailInput.value?encodeURIComponent(emailInput.value):'';
                                const mailto=`mailto:${m}?body=${encodeURIComponent(d.url)}`;
                                window.open(mailto,'_blank');
                            };
                            emailPdfBtn.style.display='inline';
                        }
                        return;
                    }
                }
                finishMsg.textContent='PDF generation failed';
            }catch(err){
                finishMsg.textContent='PDF generation failed';
            }
        }
        finishBtn.onclick=async()=>{
            if(finished) return;
            if(!pad.isEmpty()) placeCurrent();
            finishMsg.textContent='Sending signatures...';
            finishMsg.style.display='block';
            for(const s of signs){
                await fetch('/submit-signature/{token}',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image:s.img,x:s.x,y:s.y,page:s.page,scale:s.scale})});
            }
            await fetch('/finish-signing/{token}',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:nameInput.value||'',email:emailInput.value||'',phone:phoneInput.value||'',consent:consentFlag.checked})});
            finishMsg.textContent='Generating PDF...';
            finished=true;
            finishBtn.disabled=true;
            submitBtn.disabled=true;
            clearBtn.disabled=true;
            docImg.onclick=null;
            await generatePdf();
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
        ts = info.get('timestamp') or datetime.utcnow().isoformat()
        name = info.get('name', '')
        ip = request.client.host or ''
        email = info.get('email', '')
        phone = info.get('phone', '')
        consent = info.get('consent', False)
        try:
            fitz = get_fitz()
            doc = fitz.open(stream=pdf_bytes, filetype='pdf')
            # Reapply recorded signatures to guarantee the server copy is signed
            for sig in info.get('signatures', []) or []:
                try:
                    page_num = sig.get('page', info.get('page', 0))
                    page = doc[page_num]
                    img_path = sig.get('image_path')
                    if not img_path or not os.path.exists(img_path):
                        continue
                    x = float(sig.get('x', 0.5))
                    y = float(sig.get('y', 0.5))
                    scale = float(sig.get('scale', 1.0))
                    pix = fitz.Pixmap(img_path)
                    h = page.rect.height / 10 * scale
                    w = h * pix.width / pix.height
                    x0 = x * page.rect.width - w / 2
                    y0 = y * page.rect.height - h / 2
                    page.insert_image(fitz.Rect(x0, y0, x0 + w, y0 + h), filename=img_path)
                except Exception:
                    continue
            doc_bytes = doc.tobytes(
                clean=True,
                garbage=4,
                deflate=True,
                deflate_images=True,
                deflate_fonts=True,
            )
            doc.close()
        except Exception:
            logging.exception('Failed to reapply signatures')
            doc_bytes = pdf_bytes
        content_hash = hashlib.sha256(doc_bytes).hexdigest()
        legal = f"Firmato elettronicamente in data {ts} da {name} con firma elettronica semplice ai sensi del Regolamento eIDAS(UE 910/2014). IP: {ip} | Email: {email} | SHA256: {content_hash}"
        try:
            fitz = get_fitz()
            doc = fitz.open(stream=doc_bytes, filetype='pdf')
            try:
                page = doc[-1]
                rect = fitz.Rect(50, page.rect.height - 40, page.rect.width - 50, page.rect.height - 10)
                page.insert_textbox(rect, legal, fontsize=8, align=1)
            except Exception:
                pass
            try:
                info_page = doc.new_page()
                text = f"Nome: {name}\nEmail: {email}\nTelefono: {phone}\nData: {ts}\nSHA256: {content_hash}\nConsenso: {consent}"
                info_rect = fitz.Rect(50,50, info_page.rect.width-50, info_page.rect.height-50)
                info_page.insert_textbox(info_rect, text, fontsize=12, align=0)
            except Exception:
                pass
            pdf_bytes = doc.tobytes(
                clean=True,
                garbage=4,
                deflate=True,
                deflate_images=True,
                deflate_fonts=True,
            )
            doc.close()
        except Exception:
            logging.exception('Failed to append legal text')
            pdf_bytes = doc_bytes
        hash_hex = hashlib.sha256(pdf_bytes).hexdigest()
        pdf_path = os.path.join(signatures_dir, f'signed_{token}.pdf')
        with open(pdf_path, 'wb') as fh:
            fh.write(pdf_bytes)
        url = request.url_for('download_signed_pdf', token=token)
        info['pdf_file'] = pdf_path
        info['pdf_url'] = str(url)
        info['pdf_hash'] = hash_hex
        info['content_hash'] = content_hash
        with open(info_path, 'w') as fh:
            json.dump(info, fh)
        log_entry = {
            'token': token,
            'pdf_file': os.path.basename(pdf_path),
            'hash': hash_hex,
            'content_hash': content_hash,
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
            send_mail(email, 'Documento firmato', f'SHA256: {content_hash}', pdf_path)
        return {'status': 'ok', 'url': str(url), 'hash': hash_hex, 'email': email, 'phone': phone}

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
        for key in ('name', 'email', 'phone', 'pdf_hash'):
            if key in info:
                result[key if key != 'pdf_hash' else 'hash'] = info[key]
        return result

    @app.get('/download-signed/{token}.pdf', name='download_signed_pdf')
    async def download_signed_pdf(token: str):
        pdf_path = os.path.join(signatures_dir, f'signed_{token}.pdf')
        if not os.path.exists(pdf_path):
            return JSONResponse(status_code=404, content={'message': 'Not found'})
        return FileResponse(pdf_path, media_type='application/pdf', filename=f'signed_{token}.pdf', headers={"Cache-Control": "no-cache"})
