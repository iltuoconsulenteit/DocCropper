export function initRemoveBgPlugin(translations, enabled = true) {
    if (!enabled) {
        window.removeBackground = () => {};
        window.setRemoveBgThreshold = () => {};
        return;
    }
    let threshold = 50;
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
            const src = window.processedImages ? window.processedImages[index] : null;
            if (!src) return;
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
                window.dispatchEvent(new CustomEvent('imageUpdated', { detail: { index, src: url } }));
            }
        } catch (e) {
            console.error('remove background error', e);
            alert(translations.removeBgFailed || 'Background removal failed');
        }
    }
    window.removeBackground = removeBackground;
    window.setRemoveBgThreshold = setRemoveBgThreshold;
}
