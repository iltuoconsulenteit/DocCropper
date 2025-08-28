export function initImageEditorPlugin(translations, enabled = true) {
  if (!enabled) {
    window.openImageEditor = () => {};
    return;
  }

  function openImageEditor(index) {
    let sidebar = document.getElementById('imageEditorSidebar');
    if (!sidebar) {
      sidebar = document.createElement('div');
      sidebar.id = 'imageEditorSidebar';
      sidebar.className = 'toolSidebar';
      sidebar.innerHTML = `
        <h3>${translations.imageEdit || 'Edit'}</h3>
        <label>${translations.saturation || 'Saturation'}<input id="satSlider" type="range" min="0" max="200" value="100"></label>
        <label>${translations.sharpness || 'Sharpness'}<input id="sharpSlider" type="range" min="0" max="200" value="100"></label>
      `;
      document.body.appendChild(sidebar);
    }
    sidebar.style.display = 'block';

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
