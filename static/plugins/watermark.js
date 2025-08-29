export function initWatermarkPlugin(translations, enabled = true) {
    if (!enabled) {
        window.openWatermarkDialog = () => {};
        window.mergeAllWatermarks = async () => {};
        return;
    }

    const watermarks = [];
    let modal;

    function ensureModal() {
        if (modal) return;
        modal = document.createElement('div');
        modal.id = 'watermarkModal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width:300px;padding:10px;text-align:left;">
                <label style="display:block;margin-bottom:4px;">${translations.watermarkText || 'Text'}<br>
                    <input id="wmText" type="text" style="width:100%">
                </label>
                <label style="display:block;margin-bottom:4px;">${translations.watermarkImage || 'Image'}<br>
                    <input id="wmImage" type="file" accept="image/*" style="width:100%">
                </label>
                <label style="display:block;margin-bottom:4px;">${translations.watermarkSize || 'Size'}<br>
                    <input id="wmSize" type="number" value="20" style="width:100%">
                </label>
                <label style="display:block;margin-bottom:4px;">${translations.watermarkAngle || 'Angle'}<br>
                    <input id="wmAngle" type="number" value="0" style="width:100%">
                </label>
                <label style="display:block;margin-bottom:4px;">${translations.watermarkColor || 'Color'}<br>
                    <input id="wmColor" type="color" value="#000000" style="width:100%">
                </label>
                <label style="display:block;margin-bottom:4px;">${translations.watermarkFont || 'Font'}<br>
                    <input id="wmFont" type="text" value="Arial" style="width:100%">
                </label>
                <label style="display:block;margin-bottom:4px;">
                    <input type="checkbox" id="wmAll"> ${translations.applyToAll || 'Apply to all pages'}
                </label>
                <p style="font-size:0.75rem;color:#6b7280;">${translations.legalDisclaimer || ''}</p>
                <div style="text-align:right;margin-top:8px;">
                    <button id="wmCancel" style="margin-right:8px;">${translations.cancel || 'Cancel'}</button>
                    <button id="wmOk">${translations.ok || 'OK'}</button>
                </div>
            </div>`;
        document.body.appendChild(modal);
        modal.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });
    }

    function createOverlay(dataUrl, page, angle) {
        const container = document.querySelector(`.thumbContainer[data-index="${page}"]`);
        if (!container) return;
        container.style.position = 'relative';
        const img = document.createElement('img');
        img.src = dataUrl;
        Object.assign(img.style, {
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: `translate(-50%, -50%) rotate(${angle}deg) scale(1)`,
            cursor: 'move',
            maxWidth: '80%'
        });
        container.appendChild(img);
        const wm = { page, el: img, data: dataUrl, x: 0.5, y: 0.5, scale: 1, angle };
        watermarks.push(wm);

        let dragging = false;
        img.addEventListener('mousedown', (e) => { dragging = true; e.preventDefault(); });
        window.addEventListener('mousemove', (e) => {
            if (!dragging) return;
            const rect = container.getBoundingClientRect();
            wm.x = (e.clientX - rect.left) / rect.width;
            wm.y = (e.clientY - rect.top) / rect.height;
            img.style.left = (wm.x * 100) + '%';
            img.style.top = (wm.y * 100) + '%';
        });
        window.addEventListener('mouseup', () => { dragging = false; });
        img.addEventListener('wheel', (e) => {
            e.preventDefault();
            wm.scale = Math.max(0.1, wm.scale + (e.deltaY < 0 ? 0.1 : -0.1));
            img.style.transform = `translate(-50%, -50%) rotate(${wm.angle}deg) scale(${wm.scale})`;
        });
    }

    function generateTextData(opts) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        ctx.font = `${opts.size}px ${opts.font}`;
        const metrics = ctx.measureText(opts.text);
        const w = metrics.width;
        const h = opts.size * 1.2;
        canvas.width = w;
        canvas.height = h;
        ctx.font = `${opts.size}px ${opts.font}`;
        ctx.fillStyle = opts.color;
        ctx.textBaseline = 'top';
        ctx.fillText(opts.text, 0, 0);
        return canvas.toDataURL('image/png');
    }

    async function fileToDataURL(file) {
        return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.readAsDataURL(file);
        });
    }

    function openWatermarkDialog(index) {
        ensureModal();
        modal.style.display = 'block';
        const txt = document.getElementById('wmText');
        const img = document.getElementById('wmImage');
        const size = document.getElementById('wmSize');
        const angle = document.getElementById('wmAngle');
        const color = document.getElementById('wmColor');
        const font = document.getElementById('wmFont');
        const all = document.getElementById('wmAll');
        document.getElementById('wmCancel').onclick = () => { modal.style.display = 'none'; };
        document.getElementById('wmOk').onclick = async () => {
            modal.style.display = 'none';
            const opts = {
                text: txt.value.trim(),
                file: img.files[0],
                size: parseInt(size.value, 10) || 20,
                angle: parseFloat(angle.value) || 0,
                color: color.value || '#000000',
                font: font.value || 'Arial'
            };
            let dataUrl = '';
            if (opts.file) {
                dataUrl = await fileToDataURL(opts.file);
            } else if (opts.text) {
                dataUrl = generateTextData(opts);
            } else {
                return;
            }
            const imgs = typeof window.getProcessedImages === 'function'
                ? window.getProcessedImages()
                : (window.processedImages || []);
            const targets = all.checked ? imgs.map((_, i) => i) : [index];
            targets.forEach(p => createOverlay(dataUrl, p, opts.angle));
            if (all.checked) {
                await mergeAllWatermarks();
            }
            txt.value = '';
            img.value = '';
            all.checked = false;
        };
    }

    async function mergeAllWatermarks() {
        if (watermarks.length === 0) return;
        const imgs = typeof window.getProcessedImages === 'function'
            ? window.getProcessedImages()
            : (window.processedImages || []);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        async function loadImage(src) {
            return new Promise((resolve) => {
                const im = new Image();
                im.onload = () => resolve(im);
                im.src = src;
            });
        }

        for (const wm of watermarks) {
            const baseSrc = imgs[wm.page];
            if (!baseSrc) continue;
            const base = await loadImage(baseSrc);
            canvas.width = base.width;
            canvas.height = base.height;
            ctx.clearRect(0,0,canvas.width,canvas.height);
            ctx.drawImage(base,0,0);
            const wImg = await loadImage(wm.data);
            const w = wImg.width * wm.scale;
            const h = wImg.height * wm.scale;
            const x = wm.x * canvas.width - w/2;
            const y = wm.y * canvas.height - h/2;
            ctx.save();
            ctx.translate(x + w/2, y + h/2);
            ctx.rotate((wm.angle || 0) * Math.PI / 180);
            ctx.drawImage(wImg, -w/2, -h/2, w, h);
            ctx.restore();
            const url = canvas.toDataURL('image/png');
            if (typeof window.setProcessedImage === 'function') {
                window.setProcessedImage(wm.page, url);
            } else {
                imgs[wm.page] = url;
                if (window.originalImages && window.originalImages[wm.page]) {
                    window.originalImages[wm.page] = url;
                }
            }
            const imgEl = document.querySelector(`.thumbContainer[data-index="${wm.page}"] img`);
            if (imgEl) imgEl.src = url;
            if (wm.el && wm.el.parentNode) wm.el.remove();
        }
        watermarks.length = 0;
    }

    window.openWatermarkDialog = openWatermarkDialog;
    window.mergeAllWatermarks = mergeAllWatermarks;
}

