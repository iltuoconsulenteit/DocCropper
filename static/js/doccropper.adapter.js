window.DC = window.DC || {};

window.DC.export = window.DC.export || (async function () {
  const fire = () => window.dispatchEvent(new CustomEvent('dc-exported'));
  const poll = () => {
    if (window.currentPdfBlob) return fire();
    const t = setInterval(() => {
      if (window.currentPdfBlob) { clearInterval(t); fire(); }
    }, 500);
  };
  const call = (fn) => {
    try {
      const res = fn();
      if (res && typeof res.then === 'function') {
        res.then(fire).catch(() => {});
      } else {
        poll();
      }
      return res;
    } catch (e) {
      console.error(e);
    }
  };

  if (typeof window.exportPdf === 'function') return call(window.exportPdf);
  if (typeof window.doExport === 'function') return call(window.doExport);
  if (typeof window.generatePdf === 'function') return call(window.generatePdf);
  if (typeof window.handleExport === 'function') return call(window.handleExport);
  if (typeof window.startExport === 'function') return call(window.startExport);

  const btn = document.getElementById('exportPdfBtn');
  if (btn) { btn.click(); poll(); return; }

  const url = window.DC_EXPORT_ENDPOINT || '/api/export';
  const headers = { 'X-Requested-With': 'XMLHttpRequest' };
  let body;
  if (window.DC_CSRF) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded';
    body = new URLSearchParams({ [window.DC_CSRF]: 1 });
  }
  const resp = await fetch(url, { method: 'POST', headers, body });
  let downloadUrl;
  try {
    const data = await resp.json();
    downloadUrl = data && data.downloadUrl;
    if (downloadUrl) window.DC_DOWNLOAD_ENDPOINT = downloadUrl;
  } catch {}
  if (downloadUrl) {
    const box = document.getElementById('exportOptions');
    if (box) box.style.display = 'block';
    const dl = document.getElementById('downloadPdfBtn');
    if (dl) {
      dl.style.display = 'inline-block';
      dl.onclick = () => window.location.href = downloadUrl;
    }
    const frame = document.getElementById('exportPreviewFrame');
    if (frame) {
      frame.src = downloadUrl + '#toolbar=0&navpanes=0';
      frame.style.display = 'block';
    }
  }
  fire();
});

window.DC.download = window.DC.download || (async function () {
  if (typeof window.getLastPdfUrl === 'function') {
    const href = await window.getLastPdfUrl();
    if (href) return (window.location.href = href);
  }
  if (typeof window.lastPdfUrl === 'string') {
    return (window.location.href = window.lastPdfUrl);
  }
  const btn = document.getElementById('downloadPdfBtn');
  if (btn) { btn.click(); return; }
  const link = document.getElementById('signedPdfLink');
  if (link && link.href) return (window.location.href = link.href);
  if (window.currentPdfBlob) {
    const url = URL.createObjectURL(window.currentPdfBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'document.pdf';
    a.click();
    URL.revokeObjectURL(url);
    return;
  }
  const url = window.DC_DOWNLOAD_ENDPOINT || '/api/export/download';
  window.location.href = url;
});

window.DC.sign = window.DC.sign || (async function () {
  if (typeof window.startSign === 'function') return window.startSign();
  if (typeof window.openSignatureForPage === 'function') return window.openSignatureForPage(0);
  if (typeof window.startMobileSign === 'function') return window.startMobileSign();
  const btn = document.getElementById('signBtn') || document.getElementById('mobileSignBtn');
  if (btn) { btn.click(); return; }
  const url = window.DC_SIGN_ENDPOINT || '/api/sign';
  const headers = { 'X-Requested-With': 'XMLHttpRequest' };
  let body;
  if (window.DC_CSRF) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded';
    body = new URLSearchParams({ [window.DC_CSRF]: 1 });
  }
  await fetch(url, { method: 'POST', headers, body });
});

window.DC.mobileSign = window.DC.mobileSign || (async function () {
  if (typeof window.startMobileSign === 'function') return window.startMobileSign();
  const btn = document.getElementById('mobileSignBtn');
  if (btn) { btn.click(); return; }
  const url = window.DC_MOBILE_SIGN_ENDPOINT || window.DC_SIGN_ENDPOINT || '/api/sign/mobile';
  const headers = { 'X-Requested-With': 'XMLHttpRequest' };
  let body;
  if (window.DC_CSRF) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded';
    body = new URLSearchParams({ [window.DC_CSRF]: 1 });
  }
  await fetch(url, { method: 'POST', headers, body });
});

window.DC.import = window.DC.import || (async function () {
  if (typeof window.startImport === 'function') return window.startImport();
  const input = document.getElementById('imageUpload');
  if (input) { input.click(); return; }
  const url = window.DC_IMPORT_ENDPOINT || '/api/import';
  const headers = { 'X-Requested-With': 'XMLHttpRequest' };
  let body;
  if (window.DC_CSRF) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded';
    body = new URLSearchParams({ [window.DC_CSRF]: 1 });
  }
  await fetch(url, { method: 'POST', headers, body });
});

window.DC.guide = window.DC.guide || (function () {
  const url = window.DC_GUIDE_URL || '/wiki/usage.html';
  window.open(url, '_blank');
});

window.DC.donate = window.DC.donate || (function () {
  const url = window.DC_DONATE_URL || '/donate';
  window.open(url, '_blank');
});

