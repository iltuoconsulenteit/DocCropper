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
    const msDisclaimer = document.getElementById('msDisclaimer');
    window.lastSignToken = '';

    if (!enabled) {
        if (mobileSignBtn) mobileSignBtn.style.display = 'none';
        return;
    }

    if (msDisclaimer) {
        msDisclaimer.textContent = translations['legalDisclaimer'] || 'DocCropper and its authors accept no liability for illegal use.';
    }

    async function pollPdf(token) {
        try {
            const r = await fetch(`/signed-pdf/${token}`);
            if (r.status === 200) {
                const d = await r.json();
                if (d.url) {
                    window.lastSignedUrl = d.url;
                    window.dispatchEvent(new CustomEvent('signedPdfAvailable', { detail: d }));
                    return;
                }
            }
        } catch (err) {
            console.error('pdf poll error', err);
        }
        setTimeout(() => pollPdf(token), 3000);
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
                pollPdf(token);
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
            const payload = { page: 0, images };
            payload.image = images[0];
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
            if (!signQrLink) return;
            const text = signQrLink.href;
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text);
            } else {
                const tmp = document.createElement('textarea');
                tmp.value = text;
                document.body.appendChild(tmp);
                tmp.select();
                document.execCommand('copy');
                document.body.removeChild(tmp);
            }
            const original = copySignLink.textContent;
            copySignLink.style.background = '#4ade80';
            copySignLink.textContent = translations['copied'] || 'Copied!';
            setTimeout(() => {
                copySignLink.style.background = '#e5e7eb';
                copySignLink.textContent = original;
            }, 1200);
        });
    }
    if (waSignLink) {
        waSignLink.addEventListener('click', (e) => {
            e.stopPropagation();
            const url = signQrLink ? signQrLink.href : '';
            const phone = window.lastSignPhone ? window.lastSignPhone.replace(/[^0-9]/g, '') : '';
            const params = new URLSearchParams({ text: url });
            if (phone) params.set('phone', phone);
            const wa = `https://web.whatsapp.com/send?${params.toString()}`;
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
