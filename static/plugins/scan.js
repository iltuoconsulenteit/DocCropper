export function initScanPlugin(translations, enabled = true) {
    if (!enabled) {
        window.scanDocument = () => {};
        window.scanGetScanners = async () => [];
        return;
    }

    const helperUrl = 'http://127.0.0.1:28672';

    window.scanGetScanners = async () => {
        try {
            const resp = await fetch(`${helperUrl}/scanners`);
            if (!resp.ok) throw new Error('request failed');
            const data = await resp.json();
            return Array.isArray(data.scanners) ? data.scanners : [];
        } catch (err) {
            console.warn('scanGetScanners', err);
            return [];
        }
    };

    window.scanDocument = async (opts = {}) => {
        try {
            const resp = await fetch(`${helperUrl}/scan`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(opts)
            });
            if (!resp.ok) throw new Error('request failed');
            const blob = await resp.blob();
            const url = URL.createObjectURL(blob);
            window.open(url, '_blank');
        } catch (err) {
            alert(translations.installScanner || 'Scanner helper not installed');
        }
    };
}
