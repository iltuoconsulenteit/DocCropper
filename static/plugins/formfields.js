export function initFormFieldsPlugin(translations, enabled = true) {
    if (!enabled) {
        window.openFormFieldsDialog = () => {};
        window.mergeAllFormFields = async () => {};
        return;
    }

    const fields = {};
    let modal, overlay, currentPage, currentType = null;

    function ensureModal() {
        if (modal) return;
        modal = document.createElement('div');
        modal.id = 'formFieldsModal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width:90%;max-height:90%;display:flex;">
                <div id="ffImageWrap" style="position:relative;flex:1;display:flex;justify-content:center;align-items:center;">
                    <img id="ffImage" style="max-width:100%;max-height:100%;" />
                    <div id="ffOverlay" style="position:absolute;left:0;top:0;right:0;bottom:0;"></div>
                </div>
                <div style="width:150px;padding:10px;background:#fff;display:flex;flex-direction:column;gap:4px;">
                    <button id="ffText">${translations.addTextField || 'Text box'}</button>
                    <button id="ffCheck">${translations.addCheckbox || 'Checkbox'}</button>
                    <button id="ffSelect">${translations.addDropdown || 'Dropdown'}</button>
                    <button id="ffSign">${translations.addSignatureField || 'Signature'}</button>
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
        document.getElementById('ffSign').onclick = () => { currentType = 'sign'; };
        document.getElementById('ffCancel').onclick = () => { modal.style.display = 'none'; };
        document.getElementById('ffOk').onclick = saveAndClose;
        overlay = document.getElementById('ffOverlay');
        overlay.addEventListener('mousedown', startDraw);
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
            createFieldElement(overlay, { type: currentType, x, y, w, h });
            currentType = null;
        }

        overlay.addEventListener('mousemove', move);
        window.addEventListener('mouseup', end);
    }

    function createFieldElement(parent, f) {
        let el;
        if (f.type === 'checkbox') {
            el = document.createElement('input');
            el.type = 'checkbox';
        } else if (f.type === 'select') {
            el = document.createElement('select');
            el.innerHTML = '<option></option>';
        } else if (f.type === 'sign') {
            el = document.createElement('div');
            const canvas = document.createElement('canvas');
            canvas.style.width = '100%';
            canvas.style.height = '100%';
            el.appendChild(canvas);
            const ctx = canvas.getContext('2d');
            ctx.lineWidth = 2;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            function resize() {
                canvas.width = el.clientWidth;
                canvas.height = el.clientHeight;
                if (f.value) {
                    const img = new Image();
                    img.onload = () => ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                    img.src = f.value;
                }
            }
            let drawing = false;
            function pos(ev) {
                const rect = canvas.getBoundingClientRect();
                const clientX = ev.touches ? ev.touches[0].clientX : ev.clientX;
                const clientY = ev.touches ? ev.touches[0].clientY : ev.clientY;
                return {
                    x: (clientX - rect.left) * canvas.width / rect.width,
                    y: (clientY - rect.top) * canvas.height / rect.height
                };
            }
            function start(ev) {
                drawing = true;
                const p = pos(ev);
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ev.preventDefault();
            }
            function move(ev) {
                if (!drawing) return;
                const p = pos(ev);
                ctx.lineTo(p.x, p.y);
                ctx.stroke();
                ev.preventDefault();
            }
            function end() {
                if (drawing) {
                    drawing = false;
                    f.value = canvas.toDataURL('image/png');
                }
            }
            canvas.addEventListener('mousedown', start);
            canvas.addEventListener('mousemove', move);
            window.addEventListener('mouseup', end);
            canvas.addEventListener('touchstart', start, { passive: false });
            canvas.addEventListener('touchmove', move, { passive: false });
            window.addEventListener('touchend', end);
            const file = document.createElement('input');
            file.type = 'file';
            file.accept = 'image/*';
            file.title = translations.importImage || 'Import image';
            Object.assign(file.style, {
                position: 'absolute',
                bottom: '2px',
                right: '2px',
                opacity: 0.7
            });
            file.addEventListener('change', (e) => {
                const fobj = e.target.files[0];
                if (!fobj) return;
                const reader = new FileReader();
                reader.onload = (ev) => {
                    const img = new Image();
                    img.onload = () => {
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                        f.value = canvas.toDataURL('image/png');
                    };
                    img.src = ev.target.result;
                };
                reader.readAsDataURL(fobj);
            });
            el.appendChild(file);
            window.addEventListener('resize', resize);
        } else {
            el = document.createElement('textarea');
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
            height: (f.h * 100) + '%'
        });
        const handle = document.createElement('div');
        Object.assign(handle.style, {
            position: 'absolute',
            left: '-4px',
            top: '-4px',
            width: '12px',
            height: '12px',
            background: 'rgba(37,99,235,0.8)',
            cursor: 'move'
        });
        el.appendChild(handle);
        handle.addEventListener('mousedown', (e) => {
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
        });
        parent.appendChild(el);
        if (f.type === 'sign') {
            requestAnimationFrame(resize);
        }
        f.el = el;
        return el;
    }

    function openFormFieldsDialog(page) {
        ensureModal();
        currentPage = page;
        const img = document.getElementById('ffImage');
        const imgs = typeof window.getProcessedImages === 'function' ? window.getProcessedImages() : (window.processedImages || []);
        img.src = imgs[page];
        overlay.innerHTML = '';
        (fields[page] || []).forEach(f => createFieldElement(overlay, f));
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
                f.value = el.checked;
            } else if (type === 'sign') {
                const canv = el.querySelector('canvas');
                f.value = canv ? canv.toDataURL('image/png') : null;
            } else {
                f.value = el.value;
            }
            return f;
        });
        fields[currentPage] = pageFields;
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
        const baseSrc = imgs[page];
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
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 1;
            ctx.strokeRect(x,y,w,h);
            if (f.type === 'text') {
                ctx.fillStyle = '#000';
                ctx.font = `${Math.max(10, h*0.8)}px sans-serif`;
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
                ctx.fillStyle = '#000';
                ctx.font = `${Math.max(10, h*0.8)}px sans-serif`;
                ctx.textBaseline = 'top';
                ctx.fillText(f.value || '', x+2, y+2, w-4);
            } else if (f.type === 'sign' && f.value) {
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
        delete fields[page];
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

