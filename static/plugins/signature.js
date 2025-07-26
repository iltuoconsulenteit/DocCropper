export function initSignaturePlugin(translations) {
    const qrSignBtn = document.getElementById('qrSignBtn');
    const qrSignPageBtn = document.getElementById('qrSignPageBtn');
    const signQR = document.getElementById('signQR');
    const signQrImg = document.getElementById('signQrImg');
    const signQrHint = document.getElementById('signQrHint');
    async function startQrSign() {
        try {
            const resp = await fetch('/start-sign/');
            const data = await resp.json();
            if (data.qr) {
                signQrImg.src = data.qr;
                signQrHint.textContent = translations['qrScanHint'] || '';
                signQR.style.display = 'block';
            }
        } catch (e) {
            console.error('start sign error', e);
        }
    }
    if (qrSignBtn) {
        qrSignBtn.addEventListener('click', async () => {
            await startQrSign();
            const exportOptions = document.getElementById('exportOptions');
            if (exportOptions) exportOptions.style.display = 'none';
        });
    }
    if (qrSignPageBtn) {
        qrSignPageBtn.addEventListener('click', startQrSign);
    }
    if (signQR) {
        signQR.addEventListener('click', () => { signQR.style.display = 'none'; });
    }
}
