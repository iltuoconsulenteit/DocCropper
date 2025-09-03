export function initDownloadPngPlugin(translations, enabled = true) {
    if (!enabled) {
        window.downloadPng = () => {};
        return;
    }

    async function downloadPng(index) {
        try {
            const imgs = typeof window.getProcessedImages === 'function'
                ? window.getProcessedImages()
                : (window.processedImages || []);
            const src = imgs[index];
            if (!src) return;

            const img = new Image();
            img.crossOrigin = 'anonymous';

            img.onload = () => {
                const canvas = document.createElement('canvas');
                canvas.width = img.naturalWidth;
                canvas.height = img.naturalHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                canvas.toBlob(blob => {
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `page${index + 1}.png`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }, 'image/png');
            };

            img.onerror = (err) => {
                console.error('download png', err);
            };

            img.src = src;
        } catch (err) {
            console.error('download png', err);
        }
    }

    window.downloadPng = downloadPng;
}
