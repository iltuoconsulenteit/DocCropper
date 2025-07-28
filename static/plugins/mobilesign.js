export function initSignaturePlugin(translations, enabled = true) {
    const qrSignBtn = document.getElementById('qrSignBtn');
    const qrSignPageBtn = document.getElementById('qrSignPageBtn');
    const mobileSignBtn = document.getElementById('mobileSignBtn');
    const signQR = document.getElementById('signQR');
    const signQrImg = document.getElementById('signQrImg');
    const signQrHint = document.getElementById('signQrHint');
    const signQrLink = document.getElementById('signQrLink');
    const copySignLink = document.getElementById('copySignLink');
    const waSignLink = document.getElementById('waSignLink');
    const signaturePage = document.getElementById('signaturePage');

    if (!enabled) {
        if (qrSignBtn) qrSignBtn.style.display = 'none';
        if (qrSignPageBtn) qrSignPageBtn.style.display = 'none';
        if (mobileSignBtn) mobileSignBtn.style.display = 'none';
        return;
    }

    async function pollSignature(token) {
        try {
            const resp = await fetch(`/signature-result/${token}`);
            if (resp.status === 200) {
                const data = await resp.json();
                if (data.signatures && typeof data.signatures === 'object') {
                    Object.keys(data.signatures).forEach(p => {
                        window.dispatchEvent(new CustomEvent('remoteSignature', {detail: {page: p, signatures: data.signatures[p]}}));
                    });
                } else {
                    window.dispatchEvent(new CustomEvent('remoteSignature', {detail: data}));
                }
                window.dispatchEvent(new Event('mobileSignComplete'));
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
        if (window.showLoading) window.showLoading(translations['loading'] || 'Loading...');
        try {
            const images = window.processedImages || [];
            if (!images.length) return;
            if (signaturePage && signaturePage.options.length === 0) {
                signaturePage.innerHTML = '';
                for (let i = 0; i < images.length; i++) {
                    const opt = document.createElement('option');
                    opt.value = i;
                    opt.textContent = (i + 1).toString();
                    signaturePage.appendChild(opt);
                }
            }
            const page = parseInt(signaturePage?.value || '0');
            const payload = { page, images };
            payload.image = images[page];
            if (window.mobileSignPoints && Object.keys(window.mobileSignPoints).length) {
                payload.points = window.mobileSignPoints;
            }
            const resp = await fetch('/start-sign/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
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
        } finally {
            if (window.hideLoading) window.hideLoading();
        }
    }
    if (qrSignBtn) {
        qrSignBtn.addEventListener('click', async () => {
            await startQrSign();
            const exportOptions = document.getElementById('exportOptions');
            if (exportOptions) exportOptions.style.display = 'none';
        });
    }
    if (mobileSignBtn) {
        mobileSignBtn.addEventListener('click', startQrSign);
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
