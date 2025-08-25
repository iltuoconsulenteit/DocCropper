export function initImageEditorPlugin(translations, enabled = true) {
  if (!enabled) {
    window.openImageEditor = () => {};
    return;
  }

  let modal;

  function ensureModal() {
    if (modal) return modal;
    modal = document.createElement('div');
    modal.id = 'imageEditorModal';
    modal.className = 'modal';
    modal.innerHTML = `
      <div class="modal-content" style="max-width:300px;padding:10px;text-align:left;">
        <h3 style="margin-top:0;">${translations.imageEdit || 'Edit'}</h3>
        <label style="display:block;margin-bottom:4px;">${translations.saturation || 'Saturation'}<br>
          <input id="satSlider" type="range" min="0" max="200" value="100" style="width:100%">
        </label>
        <label style="display:block;margin-bottom:4px;">${translations.sharpness || 'Sharpness'}<br>
          <input id="sharpSlider" type="range" min="0" max="200" value="100" style="width:100%">
        </label>
        <div style="text-align:right;margin-top:8px;">
          <button id="ieClose" class="btn">${translations.close || 'Close'}</button>
        </div>
      </div>`;
    document.body.appendChild(modal);

    document.getElementById('ieClose').addEventListener('click', () => {
      modal.style.display = 'none';
    });
    return modal;
  }

  function openImageEditor(index) {
    const m = ensureModal();
    m.style.display = 'block';

    const sat = document.getElementById('satSlider');
    const sharp = document.getElementById('sharpSlider');

    function apply() {
      const img = document.querySelector(`.thumbContainer[data-index="${index}"] img`);
      if (!img) return;
      const satVal = sat.value;
      const sharpVal = sharp.value;
      img.style.filter = `saturate(${satVal}%) contrast(${sharpVal}%)`;
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const im = new Image();
      im.onload = () => {
        canvas.width = im.width;
        canvas.height = im.height;
        ctx.filter = `saturate(${satVal}%) contrast(${sharpVal}%)`;
        ctx.drawImage(im, 0, 0);
        if (typeof window.setProcessedImage === 'function') {
          window.setProcessedImage(index, canvas.toDataURL());
        }
      };
      im.src = img.src;
    }

    sat.oninput = apply;
    sharp.oninput = apply;
  }

  window.openImageEditor = openImageEditor;
}
