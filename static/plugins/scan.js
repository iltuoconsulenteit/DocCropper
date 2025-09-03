export function initScanPlugin(translations, enabled = true) {
    if (!enabled) {
        window.scanDocument = () => {};
        window.scanGetScanners = async () => [];
        return;
    }

    window.scanGetScanners = async () => {
        // Placeholder list – real implementation should query a helper app
        return ['Default Scanner'];
    };

    window.scanDocument = (opts = {}) => {
        try {
            const params = new URLSearchParams(opts).toString();
            const url = 'doccropper-scan://start' + (params ? '?' + params : '');
            window.location.href = url;
        } catch (err) {
            alert(translations.installScanner || 'Scanner helper not installed');
        }
    };
}
