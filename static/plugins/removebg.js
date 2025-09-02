export function initRemoveBgPlugin(translations, enabled = true) {
    if (!enabled) {
        window.removeBackground = () => {};
        return;
    }
    const originals = window.bgOriginals || [];
    const thresholds = {};
    window.bgOriginals = originals;

    function updateBtn(index, removed) {
        const btn = document.querySelector(`.thumbContainer[data-index="${index}"] .removeBgBtn`);
        if (!btn) return;
        if (removed) {
            btn.title = translations.restoreBg || 'Restore background';
            btn.textContent = '↩';
        } else {
            btn.title = translations.removeBg || 'Remove background';
            btn.textContent = '⌦';
        }
    }
    async function removeBackground(index, t) {
        try {
            if (originals[index] && typeof t !== 'number') {
                const url = originals[index];
                window.processedImages[index] = url;
                if (window.originalImages) window.originalImages[index] = url;
                const imgEl = document.querySelector(`.thumbContainer[data-index="${index}"] img`);
                if (imgEl) imgEl.src = url;
                originals[index] = null;
                updateBtn(index, false);
                const wrap = document.querySelector(`.thumbContainer[data-index="${index}"] .thumbBgThreshold`);
                if (wrap) wrap.style.display = 'none';
                window.dispatchEvent(new CustomEvent('imageUpdated', { detail: { index, src: url } }));
                return;
            }
            const threshold = typeof t === 'number' ? t : thresholds[index] ?? 50;
            thresholds[index] = threshold;
            const src = originals[index] || (window.processedImages ? window.processedImages[index] : null);
            if (!src) return;
            if (!originals[index]) originals[index] = src;
            const resp = await fetch(src);
            const blob = await resp.blob();
            const fd = new FormData();
            fd.append('image_file', blob, `image${index}.png`);
            const r = await fetch(`/remove-background/?threshold=${threshold}`, {
                method: 'POST',
                body: fd,
            });
            if (!r.ok) {
                alert(translations.removeBgFailed || 'Background removal failed');
                originals[index] = null;
                return;
            }
            const data = await r.json();
            if (data.image) {
                const url = 'data:image/png;base64,' + data.image;
                window.processedImages[index] = url;
                if (window.originalImages && window.originalImages[index]) {
                    window.originalImages[index] = url;
                }
                const container = document.querySelector(`.thumbContainer[data-index="${index}"] img`);
                if (container) container.src = url;
                updateBtn(index, true);
                const wrap = document.querySelector(`.thumbContainer[data-index="${index}"] .thumbBgThreshold`);
                if (wrap) wrap.style.display = 'block';
                window.dispatchEvent(new CustomEvent('imageUpdated', { detail: { index, src: url } }));
            } else {
                originals[index] = null;
            }
        } catch (e) {
            console.error('remove background error', e);
            alert(translations.removeBgFailed || 'Background removal failed');
        }
    }
    window.removeBackground = removeBackground;
}
