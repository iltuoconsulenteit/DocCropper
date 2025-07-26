export function initSignaturePlugin(translations) {
    const qrSignBtn = document.getElementById('qrSignBtn');
    const qrSignPageBtn = document.getElementById('qrSignPageBtn');
    const signQR = document.getElementById('signQR');
    const signQrImg = document.getElementById('signQrImg');
    const signQrHint = document.getElementById('signQrHint');
    const signQrLink = document.getElementById('signQrLink');
    const copySignLink = document.getElementById('copySignLink');
    const waSignLink = document.getElementById('waSignLink');
    const signaturePage = document.getElementById('signaturePage');

    async function pollSignature(token) {
        try {
            const resp = await fetch(`/signature-result/${token}`);
            if (resp.status === 200) {
                const data = await resp.json();
                window.dispatchEvent(new CustomEvent('remoteSignature', {detail: data}));
                signQR.style.display = 'none';
                return;
            } else if (resp.status === 202) {
                setTimeout(() => pollSignature(token), 3000);
            } else {
                signQR.style.display = 'none';
            }
        } catch (e) {
            console.error('poll error', e);
            signQR.style.display = 'none';
        }
    }

    async function startQrSign() {
        try {
            const page = parseInt(signaturePage?.value || '0');
            const img = window.processedImages ? window.processedImages[page] : null;
            if (!img) return;
            const resp = await fetch('/start-sign/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ page, image: img })
            });
            const data = await resp.json();
            if (data.qr) {
                signQrImg.src = data.qr;
                signQrHint.textContent = translations['qrScanHint'] || '';
                if (signQrLink) {
                    signQrLink.textContent = data.url;
                    signQrLink.href = data.url;
                }
                signQR.style.display = 'block';
                pollSignature(data.token);
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
    if (copySignLink) {
        copySignLink.addEventListener('click', (e) => {
            e.stopPropagation();
            if (signQrLink) navigator.clipboard.writeText(signQrLink.href);
        });
    }
    if (waSignLink) {
        waSignLink.addEventListener('click', (e) => {
            e.stopPropagation();
            const url = signQrLink ? signQrLink.href : '';
            window.open('https://wa.me/?text=' + encodeURIComponent(url), '_blank');
        });
    }
}
