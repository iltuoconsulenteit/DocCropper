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
        } else {
            el = document.createElement('textarea');
        }
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
        parent.appendChild(el);
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

    function saveAndClose() {
        const contRect = overlay.getBoundingClientRect();
        const pageFields = Array.from(overlay.querySelectorAll('.formField')).map(el => {
            const rect = el.getBoundingClientRect();
            const f = {
                type: el.tagName === 'TEXTAREA' ? 'text' : (el.tagName === 'SELECT' ? 'select' : 'checkbox'),
                x: (rect.left - contRect.left) / contRect.width,
                y: (rect.top - contRect.top) / contRect.height,
                w: rect.width / contRect.width,
                h: rect.height / contRect.height,
                value: el.tagName === 'TEXTAREA' ? el.value : (el.tagName === 'SELECT' ? el.value : el.checked)
            };
            return f;
        });
        fields[currentPage] = pageFields;
        renderFieldsToThumbnail(currentPage);
        modal.style.display = 'none';
    }

    function renderFieldsToThumbnail(page) {
        const container = document.querySelector(`.thumbContainer[data-index="${page}"]`);
        if (!container) return;
        container.style.position = 'relative';
        container.querySelectorAll('.formField').forEach(el => el.remove());
        (fields[page] || []).forEach(f => {
            const el = createFieldElement(container, f);
            el.value = typeof f.value === 'boolean' ? undefined : f.value;
            if (f.type === 'checkbox') el.checked = !!f.value;
            el.addEventListener('input', () => { f.value = el.tagName === 'TEXTAREA' ? el.value : el.value; });
            el.addEventListener('change', () => { f.value = el.tagName === 'INPUT' ? el.checked : el.value; });
        });
    }

    async function mergeAllFormFields() {
        const pages = Object.keys(fields);
        if (pages.length === 0) return;
        const imgs = typeof window.getProcessedImages === 'function' ? window.getProcessedImages() : (window.processedImages || []);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        function loadImage(src) {
            return new Promise(res => { const im = new Image(); im.onload = () => res(im); im.src = src; });
        }

        for (const p of pages) {
            const page = parseInt(p, 10);
            const baseSrc = imgs[page];
            if (!baseSrc) continue;
            const base = await loadImage(baseSrc);
            canvas.width = base.width;
            canvas.height = base.height;
            ctx.drawImage(base,0,0);
            for (const f of fields[page]) {
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
        }

        // remove drawn fields after merge
        Object.keys(fields).forEach(p => {
            const container = document.querySelector(`.thumbContainer[data-index="${p}"]`);
            if (container) container.querySelectorAll('.formField').forEach(el => el.remove());
        });
        for (const k in fields) delete fields[k];
    }

    window.openFormFieldsDialog = openFormFieldsDialog;
    window.mergeAllFormFields = mergeAllFormFields;
}

