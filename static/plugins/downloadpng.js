export function initDownloadPngPlugin(translations, enabled = true) {
    if (!enabled) {
        window.downloadPng = () => {};
        return;
    }

    async function downloadPng(index) {
        const imgs = typeof window.getProcessedImages === 'function'
            ? window.getProcessedImages()
            : (window.processedImages || []);
        const src = imgs[index];
        if (!src) return;

        try {
            const response = await fetch(src);
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `page${index + 1}.png`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (err) {
            try {
                const a = document.createElement('a');
                a.href = src;
                a.download = `page${index + 1}.png`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            } catch (e) {
                console.error('download png', err);
            }
        }
    }

    window.downloadPng = downloadPng;
}
