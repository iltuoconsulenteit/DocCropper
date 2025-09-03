export function initFormFieldsPlugin(translations, enabled = true) {
    if (!enabled) {
        window.openFormFieldsDialog = () => {};
        window.mergeAllFormFields = async () => {};
        return;
    }

    let fields = {};
    const originals = {};
    let modal, overlay, currentPage, currentType = null;
    let currentField = null;
    let colorInput, sizeInput, borderInput;

    const stored = sessionStorage.getItem('formFieldData');
    if (stored) {
        try {
            fields = JSON.parse(atob(stored));
        } catch (e) {
            fields = {};
        }
    }

    let signModal, signCanvas, signCtx, signOk, signCancel, signClear;

    function ensureSignModal() {
        if (signModal) return;
        signModal = document.createElement('div');
        signModal.id = 'ffSignModal';
        signModal.className = 'modal';
        signModal.innerHTML = `
            <div class="modal-content" style="padding:10px;">
                <canvas id="ffSignCanvas" width="400" height="200" style="border:1px solid #000;width:400px;height:200px;"></canvas>
                <div style="text-align:right;margin-top:8px;">
                    <button id="ffSignClear">${translations.clear || 'Clear'}</button>
                    <button id="ffSignCancel">${translations.cancel || 'Cancel'}</button>
                    <button id="ffSignOk">${translations.ok || 'OK'}</button>
                </div>
            </div>`;
        document.body.appendChild(signModal);
        signCanvas = document.getElementById('ffSignCanvas');
        signCtx = signCanvas.getContext('2d');
        signCtx.lineWidth = 2;
        signCtx.lineCap = 'round';
        let drawing = false;
        function pos(ev){
            const r = signCanvas.getBoundingClientRect();
            const cX = ev.touches ? ev.touches[0].clientX : ev.clientX;
            const cY = ev.touches ? ev.touches[0].clientY : ev.clientY;
            return { x: (cX - r.left) * signCanvas.width / r.width, y: (cY - r.top) * signCanvas.height / r.height };
        }
        function start(ev){ drawing = true; const p = pos(ev); signCtx.beginPath(); signCtx.moveTo(p.x,p.y); ev.preventDefault(); }
        function move(ev){ if(!drawing) return; const p = pos(ev); signCtx.lineTo(p.x,p.y); signCtx.stroke(); ev.preventDefault(); }
        function end(){ if(drawing){ drawing=false; } }
        signCanvas.addEventListener('mousedown', start);
        signCanvas.addEventListener('mousemove', move);
        window.addEventListener('mouseup', end);
        signCanvas.addEventListener('touchstart', start, {passive:false});
        signCanvas.addEventListener('touchmove', move, {passive:false});
        window.addEventListener('touchend', end);
        signClear = document.getElementById('ffSignClear');
        signCancel = document.getElementById('ffSignCancel');
        signOk = document.getElementById('ffSignOk');
        signClear.onclick = () => { signCtx.clearRect(0,0,signCanvas.width,signCanvas.height); };
        signCancel.onclick = () => { signModal.style.display = 'none'; };
    }

    function openSignDrawModal(callback){
        ensureSignModal();
        signCtx.clearRect(0,0,signCanvas.width,signCanvas.height);
        signModal.style.display = 'flex';
        signOk.onclick = () => {
            const data = signCanvas.toDataURL('image/png');
            callback(data);
            signModal.style.display = 'none';
        };
    }

    function pickSignImage(callback){
        const inp = document.createElement('input');
        inp.type = 'file';
        inp.accept = 'image/*';
        inp.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = ev => callback(ev.target.result);
            reader.readAsDataURL(file);
        };
        inp.click();
    }

    function ensureModal() {
        if (modal) return;
        modal = document.createElement('div');
        modal.id = 'formFieldsModal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width:90%;max-height:90%;display:flex;">
                <div id="ffImageWrap" style="position:relative;flex:1;display:flex;justify-content:center;align-items:center;">
                    <img id="ffImage" style="max-width:100%;max-height:100%;" />
                    <div id="ffOverlay" style="position:absolute;left:0;top:0;"></div>
                </div>
                <div style="width:170px;padding:10px;background:#fff;display:flex;flex-direction:column;gap:4px;">
                    <button id="ffText">${translations.addTextField || 'Text box'}</button>
                    <button id="ffCheck">${translations.addCheckbox || 'Checkbox'}</button>
                    <button id="ffSelect">${translations.addDropdown || 'Dropdown'}</button>
                    <button id="ffSignDraw">${translations.addSignatureDraw || 'Draw signature'}</button>
                    <button id="ffSignImg">${translations.addSignatureImage || 'Import signature/logo'}</button>
                    <label style="margin-top:8px;">
                        ${translations.ffFontColor || 'Color'}
                        <input id="ffColor" type="color" value="#000000" style="width:100%;">
                    </label>
                    <label>
                        ${translations.ffFontSize || 'Font size'}
                        <input id="ffSize" type="number" value="16" min="8" style="width:100%;">
                    </label>
                    <label>
                        <input id="ffBorder" type="checkbox" checked>
                        ${translations.ffBorder || 'Border'}
                    </label>
                    <div style="flex:1"></div>
                    <div style="text-align:right;">
                        <button id="ffCancel" style="margin-right:8px;">${translations.cancel || 'Cancel'}</button>
                        <button id="ffOk">${translations.ok || 'OK'}</button>
                    </div>
                </div>
            </div>`;
        document.body.appendChild(modal);
        modal.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });
        document.getElementById('ffText').onclick = () => { currentType = 'text'; };
        document.getElementById('ffCheck').onclick = () => { currentType = 'checkbox'; };
        document.getElementById('ffSelect').onclick = () => { currentType = 'select'; };
        document.getElementById('ffSignDraw').onclick = () => { currentType = 'signdraw'; };
        document.getElementById('ffSignImg').onclick = () => { currentType = 'signimg'; };
        document.getElementById('ffCancel').onclick = () => { modal.style.display = 'none'; };
        document.getElementById('ffOk').onclick = saveAndClose;
        overlay = document.getElementById('ffOverlay');
        overlay.addEventListener('mousedown', startDraw);
        colorInput = document.getElementById('ffColor');
        sizeInput = document.getElementById('ffSize');
        borderInput = document.getElementById('ffBorder');
        colorInput.oninput = () => { if (currentField) { currentField.style.color = colorInput.value; currentField.dataset.color = colorInput.value; } };
        sizeInput.oninput = () => { if (currentField) { currentField.style.fontSize = sizeInput.value + 'px'; currentField.dataset.size = (parseFloat(sizeInput.value) / overlay.clientHeight); } };
        borderInput.onchange = () => { if (currentField) { currentField.style.border = borderInput.checked ? '1px solid #000' : 'none'; currentField.dataset.border = borderInput.checked ? 'true' : 'false'; } };
    }

    function startDraw(e) {
        if (!currentType) return;
        e.preventDefault();
        const rect = overlay.getBoundingClientRect();
        const startX = e.clientX - rect.left;
        const startY = e.clientY - rect.top;
        const box = document.createElement('div');
        Object.assign(box.style, {
            position: 'absolute',
            border: '1px dashed #2563eb',
            left: startX + 'px',
            top: startY + 'px'
        });
        overlay.appendChild(box);

        function move(ev) {
            const x = ev.clientX - rect.left;
            const y = ev.clientY - rect.top;
            const w = x - startX;
            const h = y - startY;
            box.style.width = Math.abs(w) + 'px';
            box.style.height = Math.abs(h) + 'px';
            box.style.left = (w < 0 ? x : startX) + 'px';
            box.style.top = (h < 0 ? y : startY) + 'px';
        }

        function end() {
            window.removeEventListener('mouseup', end);
            overlay.removeEventListener('mousemove', move);
            const rect2 = box.getBoundingClientRect();
            const contRect = overlay.getBoundingClientRect();
            const x = (rect2.left - contRect.left) / contRect.width;
            const y = (rect2.top - contRect.top) / contRect.height;
            const w = rect2.width / contRect.width;
            const h = rect2.height / contRect.height;
            box.remove();
            createFieldElement(overlay, {
                type: currentType,
                x,
                y,
                w,
                h,
                color: colorInput ? colorInput.value : '#000000',
                size: sizeInput ? (parseFloat(sizeInput.value) / contRect.height) : (16 / contRect.height),
                border: borderInput ? borderInput.checked : true
            });
            currentType = null;
        }

        overlay.addEventListener('mousemove', move);
        window.addEventListener('mouseup', end);
    }

    function createFieldElement(parent, f) {
        let el;
        if (f.type === 'checkbox') {
            el = document.createElement('div');
            el.dataset.checked = f.value ? 'true' : 'false';
            el.textContent = f.value ? '✓' : '';
            Object.assign(el.style, {
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: '#fff'
            });
            el.addEventListener('click', (ev) => {
                if (ev.target !== el) return;
                el.dataset.checked = el.dataset.checked === 'true' ? 'false' : 'true';
                el.textContent = el.dataset.checked === 'true' ? '✓' : '';
            });
        } else if (f.type === 'select') {
            el = document.createElement('select');
            el.innerHTML = '<option></option>';
            if (f.value) el.value = f.value;
        } else if (f.type === 'signdraw' || f.type === 'signimg') {
            el = document.createElement('div');
            Object.assign(el.style, {
                backgroundSize: 'contain',
                backgroundRepeat: 'no-repeat',
                backgroundPosition: 'center'
            });
            if (f.value) {
                el.style.backgroundImage = `url(${f.value})`;
            } else if (f.type === 'signdraw') {
                openSignDrawModal((data) => { f.value = data; el.style.backgroundImage = `url(${data})`; });
            } else {
                pickSignImage((data) => { f.value = data; el.style.backgroundImage = `url(${data})`; });
            }
        } else {
            el = document.createElement('textarea');
            if (f.value) el.value = f.value;
        }
        el.dataset.type = f.type;
        el.className = 'formField';
        el.title = translations.fieldRemove || 'Double-click to remove';
        el.addEventListener('dblclick', () => el.remove());
        Object.assign(el.style, {
            position: 'absolute',
            left: (f.x * 100) + '%',
            top: (f.y * 100) + '%',
            width: (f.w * 100) + '%',
            height: (f.h * 100) + '%',
            border: f.border === false ? 'none' : '1px solid #000',
            color: f.color || '#000',
            fontSize: f.size ? (f.size * parent.clientHeight) + 'px' : ''
        });
        el.dataset.color = f.color || '#000';
        el.dataset.size = f.size || (16 / parent.clientHeight);
        el.dataset.border = f.border === false ? 'false' : 'true';
        const handle = document.createElement('div');
        Object.assign(handle.style, {
            position: 'absolute',
            left: '-8px',
            top: '-8px',
            width: '16px',
            height: '16px',
            background: 'rgba(37,99,235,0.8)',
            cursor: 'move',
            zIndex: 10
        });
        el.appendChild(handle);
        const dragStart = (e) => {
            e.preventDefault();
            e.stopPropagation();
            const rect = parent.getBoundingClientRect();
            const startX = e.clientX;
            const startY = e.clientY;
            const initLeft = parseFloat(el.style.left);
            const initTop = parseFloat(el.style.top);
            function move(ev) {
                const dx = (ev.clientX - startX) / rect.width * 100;
                const dy = (ev.clientY - startY) / rect.height * 100;
                el.style.left = (initLeft + dx) + '%';
                el.style.top = (initTop + dy) + '%';
            }
            function up() {
                window.removeEventListener('mousemove', move);
                window.removeEventListener('mouseup', up);
            }
            window.addEventListener('mousemove', move);
            window.addEventListener('mouseup', up);
        };
        handle.addEventListener('mousedown', dragStart);
        el.addEventListener('mousedown', (e) => {
            if (e.target === el && e.button === 0 && el.tagName !== 'TEXTAREA') {
                dragStart(e);
            }
        });
        el.addEventListener('click', () => {
            currentType = null;
            currentField = el;
            if (colorInput) colorInput.value = el.dataset.color || '#000000';
            if (sizeInput) sizeInput.value = Math.round((el.dataset.size || (16 / parent.clientHeight)) * parent.clientHeight);
            if (borderInput) borderInput.checked = el.dataset.border !== 'false';
        });
        parent.appendChild(el);
        f.el = el;
        return el;
    }

    function openFormFieldsDialog(page) {
        ensureModal();
        currentPage = page;
        currentField = null;
        const img = document.getElementById('ffImage');
        const wrap = document.getElementById('ffImageWrap');
        const imgs = typeof window.getProcessedImages === 'function' ? window.getProcessedImages() : (window.processedImages || []);
        img.onload = () => {
            const w = img.clientWidth;
            const h = img.clientHeight;
            const offX = (wrap.clientWidth - w) / 2;
            const offY = (wrap.clientHeight - h) / 2;
            overlay.style.left = offX + 'px';
            overlay.style.top = offY + 'px';
            overlay.style.width = w + 'px';
            overlay.style.height = h + 'px';
            overlay.innerHTML = '';
            (fields[page] || []).forEach(f => createFieldElement(overlay, f));
        };
        img.src = imgs[page];
        modal.style.display = 'block';
    }

    async function saveAndClose() {
        const contRect = overlay.getBoundingClientRect();
        const pageFields = Array.from(overlay.querySelectorAll('.formField')).map(el => {
            const rect = el.getBoundingClientRect();
            const type = el.dataset.type || (el.tagName === 'TEXTAREA' ? 'text' : (el.tagName === 'SELECT' ? 'select' : 'checkbox'));
            const f = {
                type,
                x: (rect.left - contRect.left) / contRect.width,
                y: (rect.top - contRect.top) / contRect.height,
                w: rect.width / contRect.width,
                h: rect.height / contRect.height
            };
            if (type === 'checkbox') {
                f.value = el.dataset.checked === 'true';
            } else if (type === 'signdraw' || type === 'signimg') {
                f.value = el.style.backgroundImage ? el.style.backgroundImage.slice(5, -2) : null;
            } else {
                f.value = el.value;
                f.color = el.dataset.color || '#000';
                f.border = el.dataset.border !== 'false';
                f.size = parseFloat(el.dataset.size || '0');
            }
            return f;
        });
        fields[currentPage] = pageFields;
        sessionStorage.setItem('formFieldData', btoa(JSON.stringify(fields)));
        await mergeFieldsToThumbnail(currentPage);
        modal.style.display = 'none';
    }
    async function mergeFieldsToThumbnail(page) {
        const pageFields = fields[page];
        if (!pageFields || pageFields.length === 0) return;
        const imgs = typeof window.getProcessedImages === 'function' ? window.getProcessedImages() : (window.processedImages || []);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        function loadImage(src) {
            return new Promise(res => { const im = new Image(); im.onload = () => res(im); im.src = src; });
        }
        const baseSrc = originals[page] || imgs[page];
        if (!baseSrc) return;
        const base = await loadImage(baseSrc);
        canvas.width = base.width;
        canvas.height = base.height;
        ctx.drawImage(base,0,0);
        for (const f of pageFields) {
            const x = f.x * canvas.width;
            const y = f.y * canvas.height;
            const w = f.w * canvas.width;
            const h = f.h * canvas.height;
            if (f.border !== false) {
                ctx.strokeStyle = '#000';
                ctx.lineWidth = 1;
                ctx.strokeRect(x,y,w,h);
            }
            if (f.type === 'text') {
                ctx.fillStyle = f.color || '#000';
                const fontPx = f.size ? f.size * canvas.height : Math.max(10, h*0.8);
                ctx.font = `${fontPx}px sans-serif`;
                ctx.textBaseline = 'top';
                ctx.fillText(f.value || '', x+2, y+2, w-4);
            } else if (f.type === 'checkbox') {
                if (f.value) {
                    ctx.beginPath();
                    ctx.moveTo(x+2, y+h/2);
                    ctx.lineTo(x+w/3, y+h-2);
                    ctx.lineTo(x+w-2, y+2);
                    ctx.stroke();
                }
            } else if (f.type === 'select') {
                ctx.fillStyle = f.color || '#000';
                const fontPx = f.size ? f.size * canvas.height : Math.max(10, h*0.8);
                ctx.font = `${fontPx}px sans-serif`;
                ctx.textBaseline = 'top';
                ctx.fillText(f.value || '', x+2, y+2, w-4);
            } else if ((f.type === 'signdraw' || f.type === 'signimg') && f.value) {
                const img = await loadImage(f.value);
                ctx.drawImage(img, x, y, w, h);
            }
        }
        const url = canvas.toDataURL('image/png');
        if (typeof window.setProcessedImage === 'function') {
            window.setProcessedImage(page, url);
        } else {
            imgs[page] = url;
        }
        const imgEl = document.querySelector(`.thumbContainer[data-index="${page}"] img`);
        if (imgEl) imgEl.src = url;
        originals[page] = baseSrc;
    }

    async function mergeAllFormFields() {
        const pages = Object.keys(fields);
        for (const p of pages) {
            await mergeFieldsToThumbnail(parseInt(p,10));
        }
    }

    window.openFormFieldsDialog = openFormFieldsDialog;
    window.mergeAllFormFields = mergeAllFormFields;
}

