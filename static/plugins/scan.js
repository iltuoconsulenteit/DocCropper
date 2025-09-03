export function initScanPlugin(translations, enabled = true) {
    if (!enabled) {
        window.scanDocument = () => {};
        return;
    }

    function scanDocument() {
        try {
            window.location.href = 'doccropper-scan://start';
        } catch (err) {
            alert(translations.installScanner || 'Scanner helper not installed');
        }
    }

    window.scanDocument = scanDocument;
}
