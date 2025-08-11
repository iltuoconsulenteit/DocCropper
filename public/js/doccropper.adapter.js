window.DC = window.DC || {};

if (typeof window.generatePdf === 'function' && !window.generatePdf._dcPatched) {
  const origGeneratePdf = window.generatePdf;
  window.generatePdf = function (...args) {
    const res = origGeneratePdf.apply(this, args);
    const poll = setInterval(() => {
      if (window.currentPdfBlob) {
        clearInterval(poll);
        window.dispatchEvent(new CustomEvent('dc-exported'));
      }
    }, 500);
    return res;
  };
  window.generatePdf._dcPatched = true;
}

window.DC.export = window.DC.export || (async function () {
  if (typeof window.exportPdf === 'function') {
    const result = await window.exportPdf();
    window.dispatchEvent(new CustomEvent('dc-exported'));
    return result;
  }
  if (typeof window.doExport === 'function') {
    const result = await window.doExport();
    window.dispatchEvent(new CustomEvent('dc-exported'));
    return result;
  }
  const btn = document.getElementById('exportPdfBtn');
  if (btn) {
    btn.click();
    return;
  }
  const url = window.DC_EXPORT_ENDPOINT || '/api/export';
  const headers = { 'X-Requested-With': 'XMLHttpRequest' };
  let body;
  if (window.DC_CSRF) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded';
    body = new URLSearchParams({ [window.DC_CSRF]: 1 });
  }
  const resp = await fetch(url, { method: 'POST', headers, body });
  try {
    const data = await resp.json();
    if (data && data.downloadUrl) {
      window.DC_DOWNLOAD_ENDPOINT = data.downloadUrl;
    }
  } catch (e) {
    // ignore json parse errors
  }
  window.dispatchEvent(new CustomEvent('dc-exported'));
});

window.DC.download = window.DC.download || (async function () {
  if (typeof window.getLastPdfUrl === 'function') {
    const href = await window.getLastPdfUrl();
    if (href) return (window.location.href = href);
  }
  const btn = document.getElementById('downloadPdfBtn');
  if (btn) {
    btn.click();
    return;
  }
  const link = document.getElementById('signedPdfLink');
  if (link && link.href) {
    window.location.href = link.href;
    return;
  }
  const url = window.DC_DOWNLOAD_ENDPOINT || '/api/export/download';
  window.location.href = url;
});

window.DC.sign = window.DC.sign || (async function () {
  if (typeof window.startMobileSign === 'function') return window.startMobileSign();
  const btn = document.getElementById('signBtn');
  if (btn) {
    btn.click();
    return;
  }
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
  if (btn) {
    btn.click();
    return;
  }
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
  if (input) {
    input.click();
    return;
  }
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
  const url = window.DC_GUIDE_URL || '/guide';
  window.open(url, '_blank');
});

window.DC.donate = window.DC.donate || (function () {
  const url = window.DC_DONATE_URL || '/donate';
  window.open(url, '_blank');
});
