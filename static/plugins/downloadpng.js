export function initDownloadPngPlugin(translations, enabled = true) {
    if (!enabled) {
        window.downloadPng = () => {};
        return;
    }
    function downloadPng(index) {
        const images = window.processedImages || [];
        const src = images[index];
        if (!src) return;

        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
            try {
                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                canvas.toBlob(blob => {
                    if (!blob) return;
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `page${index + 1}.png`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }, 'image/png');
            } catch (err) {
                console.error('download png', err);
            }
        };
        img.src = src;
    }
    window.downloadPng = downloadPng;
}
