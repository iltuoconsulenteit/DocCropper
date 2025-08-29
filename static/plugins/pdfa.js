export function initPdfaPlugin(translations, enabled = false) {
    if (!enabled) {
        window.getPdfaVersion = () => null;
        return;
    }
    const exportBox = document.getElementById('exportOptions');
    if (!exportBox) return;
    const controls = document.createElement('div');
    controls.id = 'pdfaControls';
    controls.style.cssText = 'text-align:left; margin:24px 4px 8px 4px; font-size:13px; padding:6px; border:2px solid #2563eb; border-radius:4px; background:#eff6ff;';
    controls.innerHTML = `
      <div>
        <label for="pdfaVersion" style="font-weight:bold;">${translations['pdfa'] || 'PDF/A'}</label>
        <select id="pdfaVersion">
          <option value="none">${translations['pdfaNone'] || 'None'}</option>
          <option value="1">${translations['pdfa1'] || 'PDF/A-1'}</option>
          <option value="2">${translations['pdfa2'] || 'PDF/A-2'}</option>
          <option value="3">${translations['pdfa3'] || 'PDF/A-3'}</option>
          <option value="4">${translations['pdfa4'] || 'PDF/A-4'}</option>
        </select>
      </div>
    `;
    exportBox.insertBefore(controls, exportBox.firstChild.nextSibling);
    const versionSelect = controls.querySelector('#pdfaVersion');
    window.getPdfaVersion = () => {
        const v = versionSelect.value;
        return v === 'none' ? null : v;
    };
}
