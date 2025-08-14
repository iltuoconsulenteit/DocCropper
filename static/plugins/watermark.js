export function initWatermarkPlugin(translations, enabled = true) {
    if (!enabled) {
        window.openWatermarkDialog = () => {};
        return;
    }
    let modal;
    function ensureModal() {
        if (modal) return;
        modal = document.createElement('div');
        modal.id = 'watermarkModal';
        Object.assign(modal.style, {
            position: 'fixed', top: '0', left: '0', right: '0', bottom: '0',
            background: 'rgba(0,0,0,0.6)', display: 'none', alignItems: 'center', justifyContent: 'center',
            zIndex: '1000'
        });
        const box = document.createElement('div');
        Object.assign(box.style, {
            background: '#fff', padding: '10px', borderRadius: '4px', width: '260px'
        });
        box.innerHTML = `
            <label>${translations.watermarkText || 'Text'}<input id="wmText" type="text" style="width:100%"></label>
            <label>${translations.watermarkImage || 'Image'}<input id="wmImage" type="file" accept="image/*" style="width:100%"></label>
            <label>${translations.watermarkSize || 'Size'}<input id="wmSize" type="number" value="20" style="width:100%"></label>
            <label>${translations.watermarkAngle || 'Angle'}<input id="wmAngle" type="number" value="0" style="width:100%"></label>
            <label>${translations.watermarkColor || 'Color'}<input id="wmColor" type="color" value="#000000" style="width:100%"></label>
            <label>${translations.watermarkFont || 'Font'}<input id="wmFont" type="text" value="arial.ttf" style="width:100%"></label>
            <label><input type="checkbox" id="wmAll"> ${translations.applyToAll || 'Apply to all pages'}</label>
            <div style="margin-top:8px; text-align:right;">
                <button id="wmCancel" style="margin-right:8px;">${translations.cancel || 'Cancel'}</button>
                <button id="wmOk">${translations.ok || 'OK'}</button>
            </div>
        `;
        modal.appendChild(box);
        document.body.appendChild(modal);
    }
    async function applyWatermark(index, opts, applyAll) {
        const imgs = typeof window.getProcessedImages === 'function'
            ? window.getProcessedImages()
            : (window.processedImages || []);
        const targets = applyAll ? imgs.map((_, i) => i) : [index];
        for (const idx of targets) {
            const src = imgs[idx];
            if (!src) continue;
            const resp = await fetch(src);
            const blob = await resp.blob();
            const fd = new FormData();
            fd.append('image_file', blob, `img${idx}.png`);
            if (opts.text) fd.append('text', opts.text);
            if (opts.file) fd.append('watermark_image', opts.file);
            fd.append('font_size', opts.size);
            fd.append('angle', opts.angle);
            fd.append('color', opts.color);
            fd.append('font_name', opts.font);
            fd.append('scale', opts.scale);
            const r = await fetch('/watermark/', { method: 'POST', body: fd });
            if (r.ok) {
                const data = await r.json();
                if (data.image) {
                    const url = 'data:image/png;base64,' + data.image;
                    if (typeof window.setProcessedImage === 'function') {
                        window.setProcessedImage(idx, url);
                    } else if (window.processedImages) {
                        window.processedImages[idx] = url;
                        if (window.originalImages && window.originalImages[idx]) {
                            window.originalImages[idx] = url;
                        }
                    }
                    const imgEl = document.querySelector(`.thumbContainer[data-index="${idx}"] img`);
                    if (imgEl) imgEl.src = url;
                    window.dispatchEvent(new CustomEvent('imageUpdated', { detail: { index: idx, src: url } }));
                }
            } else {
                alert(translations.watermarkFailed || 'Watermark failed');
            }
        }
    }
    function openWatermarkDialog(index) {
        ensureModal();
        modal.style.display = 'flex';
        const txt = document.getElementById('wmText');
        const img = document.getElementById('wmImage');
        const size = document.getElementById('wmSize');
        const angle = document.getElementById('wmAngle');
        const color = document.getElementById('wmColor');
        const font = document.getElementById('wmFont');
        const all = document.getElementById('wmAll');
        document.getElementById('wmCancel').onclick = () => {
            modal.style.display = 'none';
        };
        document.getElementById('wmOk').onclick = async () => {
            modal.style.display = 'none';
            const opts = {
                text: txt.value.trim(),
                file: img.files[0],
                size: parseInt(size.value, 10) || 20,
                angle: parseFloat(angle.value) || 0,
                color: color.value || '#000000',
                font: font.value || 'arial.ttf',
                scale: 1.0
            };
            await applyWatermark(index, opts, all.checked);
            txt.value = '';
            img.value = '';
            all.checked = false;
        };
    }
    window.openWatermarkDialog = openWatermarkDialog;
}
