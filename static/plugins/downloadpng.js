export function initDownloadPngPlugin(translations, enabled = true) {
    if (!enabled) {
        window.downloadPng = () => {};
        return;
    }
    function downloadPng(index) {
        const src = window.processedImages ? window.processedImages[index] : null;
        if (!src) return;
        fetch(src)
            .then(r => r.blob())
            .then(blob => {
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `page${index + 1}.png`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            })
            .catch(err => console.error('download png', err));
    }
    window.downloadPng = downloadPng;
}
