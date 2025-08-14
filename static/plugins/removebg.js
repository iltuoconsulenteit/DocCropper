export function initRemoveBgPlugin(translations, enabled = true) {
    if (!enabled) {
        window.removeBackground = () => {};
        window.setRemoveBgThreshold = () => {};
        return;
    }
    let threshold = 50;
    const originals = window.bgOriginals || [];
    window.bgOriginals = originals;

    function updateBtn(index, removed) {
        const btn = document.querySelector(`.thumbContainer[data-index="${index}"] .removeBgBtn`);
        if (!btn) return;
        if (removed) {
            btn.title = translations.restoreBg || 'Restore background';
            btn.textContent = '↺';
        } else {
            btn.title = translations.removeBg || 'Remove background';
            btn.textContent = '⌦';
        }
    }
    function setRemoveBgThreshold() {
        const val = prompt(
            translations.removeBgThresholdPrompt || 'Threshold (%)',
            String(threshold)
        );
        const num = parseInt(val, 10);
        if (!isNaN(num) && num >= 0 && num <= 100) {
            threshold = num;
        }
    }
    async function removeBackground(index) {
        try {
            if (originals[index]) {
                const url = originals[index];
                window.processedImages[index] = url;
                if (window.originalImages) window.originalImages[index] = url;
                const imgEl = document.querySelector(`.thumbContainer[data-index="${index}"] img`);
                if (imgEl) imgEl.src = url;
                originals[index] = null;
                updateBtn(index, false);
                window.dispatchEvent(new CustomEvent('imageUpdated', { detail: { index, src: url } }));
                return;
            }
            const src = window.processedImages ? window.processedImages[index] : null;
            if (!src) return;
            originals[index] = src;
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
    window.setRemoveBgThreshold = setRemoveBgThreshold;
}
