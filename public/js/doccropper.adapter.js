window.DC = window.DC || {};

window.DC.export = window.DC.export || (async function() {
  if (typeof window.exportPdf === 'function') return window.exportPdf();
  if (typeof window.doExport === 'function') return window.doExport();

  const url = window.DC_EXPORT_ENDPOINT || '/api/export';
  const headers = { 'X-Requested-With': 'XMLHttpRequest' };
  let body;
  if (window.DC_CSRF) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded';
    body = new URLSearchParams({ [window.DC_CSRF]: 1 });
  }
  await fetch(url, { method: 'POST', headers, body });
  window.dispatchEvent(new CustomEvent('dc-exported'));
});

window.DC.download = window.DC.download || (async function() {
  if (typeof window.getLastPdfUrl === 'function') {
    const href = await window.getLastPdfUrl();
    if (href) return (window.location.href = href);
  }
  const url = window.DC_DOWNLOAD_ENDPOINT || '/api/export/download';
  window.location.href = url;
});

window.DC.sign = window.DC.sign || (async function() {
  if (typeof window.startMobileSign === 'function') return window.startMobileSign();
  const url = window.DC_SIGN_ENDPOINT || '/api/sign';
  const headers = { 'X-Requested-With': 'XMLHttpRequest' };
  let body;
  if (window.DC_CSRF) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded';
    body = new URLSearchParams({ [window.DC_CSRF]: 1 });
  }
  await fetch(url, { method: 'POST', headers, body });
});
