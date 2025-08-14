export function initPdfCompressPlugin(translations, enabled = false) {
    if (!enabled) {
        window.getCompressionLevel = () => 'none';
        window.getJpegQuality = () => 75;
        return;
    }
    const exportBox = document.getElementById('exportOptions');
    if (!exportBox) return;
    const controls = document.createElement('div');
    controls.id = 'compressionControls';
    controls.style.cssText = 'text-align:left; margin-bottom:8px; font-size:13px; padding:6px; border:2px solid #2563eb; border-radius:4px; background:#eff6ff;';
    controls.innerHTML = `
      <div>
        <label for="compressionLevel" style="font-weight:bold;">${translations['compression'] || 'Compression'}</label>
        <select id="compressionLevel">
          <option value="low">${translations['compressionLow'] || 'Low'}</option>
          <option value="medium" selected>${translations['compressionMedium'] || 'Medium'}</option>
          <option value="extreme">${translations['compressionExtreme'] || 'Extreme'}</option>
        </select>
      </div>
      <div id="extremeOptions" style="display:none; margin-top:4px;">
        <label for="jpegQuality">${translations['jpegQuality'] || 'JPEG Quality'}</label>
        <input type="number" id="jpegQuality" value="50" min="10" max="95" />
      </div>
    `;
    exportBox.insertBefore(controls, exportBox.firstChild.nextSibling);
    const levelSelect = controls.querySelector('#compressionLevel');
    const extremeOpts = controls.querySelector('#extremeOptions');
    levelSelect.value = 'medium';
    levelSelect.addEventListener('change', () => {
        extremeOpts.style.display = levelSelect.value === 'extreme' ? 'block' : 'none';
    });
    window.getCompressionLevel = () => levelSelect.value;
    window.getJpegQuality = () => parseInt(controls.querySelector('#jpegQuality').value || '50');
}
