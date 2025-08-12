export function initSignaturePlugin(translations, enabled = true) {
    const mobileSignBtn = document.getElementById('mobileSignBtn');
    const signQR = document.getElementById('signQR');
    const signQrImg = document.getElementById('signQrImg');
    const signQrHint = document.getElementById('signQrHint');
    const signQrLink = document.getElementById('signQrLink');
    const copySignLink = document.getElementById('copySignLink');
    const waSignLink = document.getElementById('waSignLink');
    const emailSignLink = document.getElementById('emailSignLink');
    const detailsModal = document.getElementById('mobileDetailsModal');
    const detailsName = document.getElementById('mobileNameInput');
    const detailsEmail = document.getElementById('mobileEmailInput');
    const detailsPhone = document.getElementById('mobilePhoneInput');
    const detailsStart = document.getElementById('mobileDetailsStart');
    const detailsCancel = document.getElementById('mobileDetailsCancel');
    const signaturePage = document.getElementById('signaturePage');
    window.lastSignToken = '';

    if (!enabled) {
        if (mobileSignBtn) mobileSignBtn.style.display = 'none';
        return;
    }

    async function pollSignature(token) {
        try {
            const resp = await fetch(`/signature-result/${token}`);
            if (resp.status === 200) {
                const data = await resp.json();
                window.lastSignName = data.name || '';
                window.lastSignEmail = data.email || '';
                window.lastSignPhone = data.phone || '';
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
            const images = typeof window.getProcessedImages === 'function'
                ? window.getProcessedImages()
                : (window.processedImages || []);
            if (!images.length) {
                alert(translations['noFiles'] || 'No files available.');
                return;
            }
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
            if (window.lastSignName) payload.name = window.lastSignName;
            if (window.lastSignEmail) payload.email = window.lastSignEmail;
            if (window.lastSignPhone) payload.phone = window.lastSignPhone;
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
                signQR.style.display = 'flex';
                window.lastSignToken = data.token;
                pollSignature(data.token);
            }
        } catch (e) {
            console.error('start sign error', e);
        } finally {
            if (window.hideLoading) window.hideLoading();
        }
    }
    function openDetailsModal() {
        if (!detailsModal) { startQrSign(); return; }
        if (detailsName) detailsName.value = window.lastSignName || '';
        if (detailsEmail) detailsEmail.value = window.lastSignEmail || '';
        if (detailsPhone) detailsPhone.value = window.lastSignPhone || '';
        detailsModal.style.display = 'flex';
    }
    // Expose starter so global adapter can trigger the mobile signing flow
    window.startMobileSign = openDetailsModal;
    if (mobileSignBtn) {
        mobileSignBtn.addEventListener('click', openDetailsModal);
    }
    if (detailsStart) {
        detailsStart.addEventListener('click', () => {
            window.lastSignName = detailsName ? detailsName.value.trim() : '';
            window.lastSignEmail = detailsEmail ? detailsEmail.value.trim() : '';
            window.lastSignPhone = detailsPhone ? detailsPhone.value.trim() : '';
            if (detailsModal) detailsModal.style.display = 'none';
            startQrSign();
        });
    }
    if (detailsCancel) {
        detailsCancel.addEventListener('click', () => {
            if (detailsModal) detailsModal.style.display = 'none';
        });
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
            const phone = window.lastSignPhone ? window.lastSignPhone.replace(/[^0-9]/g, '') : '';
            const wa = phone ? `https://wa.me/${phone}?text=${encodeURIComponent(url)}` :
                `https://wa.me/?text=${encodeURIComponent(url)}`;
            window.open(wa, '_blank');
        });
    }
    if (emailSignLink) {
        emailSignLink.addEventListener('click', (e) => {
            e.stopPropagation();
            const url = signQrLink ? signQrLink.href : '';
            const mail = window.lastSignEmail ? encodeURIComponent(window.lastSignEmail) : '';
            const mailto = `mailto:${mail}?body=${encodeURIComponent(url)}`;
            window.open(mailto, '_blank');
        });
    }
}
