import interact from 'https://cdn.interactjs.io/v1.10.11/interactjs/index.js';

let scaling_factor_w;
let scaling_factor_h;
let origW;
let origH;
let currentPointsOnDisplayedImage = []; // Stores [x1,y1,x2,y2,x3,y3,x4,y4] for displayed image

const imageElement = document.getElementById('imageToCrop');
const wrapperElement = document.getElementById('wrapper');
const svgOverlayElement = document.getElementById('svgOverlay');
// console.log('DEBUG: svgOverlayElement right after declaration:', svgOverlayElement); 
const fogPathElement = document.getElementById('fogPath');
// console.log('DEBUG: fogPathElement right after declaration:', fogPathElement); 
const imageUploadElement = document.getElementById('imageUpload');
const submitBtn = document.getElementById('submitBtn');
const exportPdfBtn = document.getElementById('exportPdfBtn');
const exportOptions = document.getElementById('exportOptions');
const downloadPdfBtn = document.getElementById('downloadPdfBtn');
const waShareBtn = document.getElementById('waShareBtn');
const emailShareBtn = document.getElementById('emailShareBtn');
const layoutControls = document.getElementById('layoutControls');
const layoutSelect = document.getElementById('layoutSelect');
const orientationSelect = document.getElementById('orientationSelect');
const arrangeSelect = document.getElementById('arrangeSelect');
const scaleMode = document.getElementById('scaleMode');
const scalePercent = document.getElementById('scalePercent');
const processedImageElement = document.getElementById('processedImage');
const processedGallery = document.getElementById('processedGallery');
const statusMessageElement = document.getElementById('statusMessage');
const reorderHint = document.getElementById('reorderHint');
const imageModal = document.getElementById('imageModal');
const modalImage = document.getElementById('modalImage');
const closeModal = document.getElementById('closeModal');
const langSelect = document.getElementById('langSelect');
const layoutPreview = document.getElementById('layoutPreview');
const licenseInfo = document.getElementById('licenseInfo');
const purchaseBox = document.getElementById('purchaseBox');
const licenseBox = document.getElementById('licenseBox');
const loginArea = document.getElementById('loginArea');
const brandBox = document.getElementById('brandBox');
const versionBox = document.getElementById('versionBox');
const instructionsBox = document.getElementById('instructionsBox');
const helpBtn = document.getElementById('helpBtn');
const purchaseBtn = document.getElementById('purchaseBtn');
const licenseBtn = document.getElementById('licenseBtn');
const bannerBox = document.getElementById('bannerBox');
const closeBanner = document.getElementById('closeBanner');
const sloganImg = document.getElementById('sloganImg');
const wikiFrame = document.getElementById('wikiFrame');
const openWikiLink = document.getElementById('openWikiLink');
const clientLogo = document.getElementById('clientLogo');
const sponsorLogo = document.getElementById('sponsorLogo');
const autoDetectHint = document.getElementById('autoDetectHint');
const adjustControls = document.getElementById('adjustControls');
const brightnessRange = document.getElementById('brightnessRange');
const contrastRange = document.getElementById('contrastRange');
const ocrBtn = document.getElementById('ocrBtn');
const ocrOutput = document.getElementById('ocrOutput');
const signatureControls = document.getElementById('signatureControls');
const signatureUpload = document.getElementById('signatureUpload');
const remoteSignCheckbox = document.getElementById('remoteSign');
const signaturePreview = document.getElementById('signaturePreview');
const signatureHint = document.getElementById('signatureHint');
const signatureExtra = document.getElementById('signatureExtra');
const signaturePage = document.getElementById('signaturePage');
const signatureScaleInput = document.getElementById('signatureScale');
const addSignatureBtn = document.getElementById('addSignatureBtn');
let signatureImageData = null;
let signatureImg = null;
let signaturePosition = { x: 0.85, y: 0.85 };
let signatureScale = 1;
let signatures = [];
let draggingSig = false;
const OCR_ENABLED = false;
let bannerImages = [];
let bannerIndex = 0;
let bannerTimer;
if (!OCR_ENABLED) {
    if (ocrBtn) ocrBtn.style.display = 'none';
    if (ocrOutput) ocrOutput.style.display = 'none';
}
const inputMode = document.getElementById('inputMode');
const fileInputArea = document.getElementById('fileInputArea');
const cameraControls = document.getElementById('cameraControls');
const cameraPreview = document.getElementById('cameraPreview');
const cameraSelect = document.getElementById('cameraSelect');
const captureBtn = document.getElementById('captureBtn');
const isMobile = /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);
const cameraFileInput = document.getElementById('cameraFileInput');
const CAPTURE_MAX_DIM = 1600;
const CAPTURE_QUALITY = 0.8;

let isLicensed = false;
let licenseName = '';
let appVersion = '';
let userInfo = null;
let currentLicenseLevel = 'free';
const MAX_IMAGES_FREE = 5;

let files = [];
let currentFileIndex = 0;
let processedImages = [];
let processedFiles = [];
let editingIndex = null;
let cameraStream = null;
let cameraAvailable = false;
let currentPdfBlob = null;
let sortable = null;
let currentFile = null;

let translations = {};
let currentLang = 'en';
let currentSettings = {};

async function enumerateCameras() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
        return;
    }
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const cams = devices.filter(d => d.kind === 'videoinput');
        cameraSelect.innerHTML = '';
        cams.forEach((c, idx) => {
            const opt = document.createElement('option');
            opt.value = c.deviceId;
            opt.textContent = c.label || `${t('modeCamera')} ${idx + 1}`;
            cameraSelect.appendChild(opt);
        });
        cameraSelect.style.display = cams.length > 1 ? 'block' : 'none';
    } catch (err) {
        console.warn('Failed to enumerate cameras', err);
    }
}

function setupDeviceMode() {
    if (isMobile) {
        inputMode.style.display = 'inline-block';
        if (!Array.from(inputMode.options).some(o => o.value === 'camera')) {
            const opt = document.createElement('option');
            opt.value = 'camera';
            opt.textContent = t('modeCamera');
            inputMode.appendChild(opt);
        }
        inputMode.value = 'upload';
        enumerateCameras();
    } else {
        inputMode.style.display = 'none';
        inputMode.value = 'upload';
    }
}


function updateInputMode() {
    const mode = inputMode.value;
    fileInputArea.style.display = mode === 'upload' ? 'block' : 'none';
    cameraControls.style.display = mode === 'camera' ? 'block' : 'none';
    if (mode === 'camera') {
        enumerateCameras();
        startCamera();
    } else {
        stopCamera();
    }
}


function startCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        cameraAvailable = false;
        return;
    }
    if (cameraStream) {
        stopCamera();
    }
    const constraints = { video: { deviceId: cameraSelect.value ? { exact: cameraSelect.value } : undefined } };
    navigator.mediaDevices.getUserMedia(constraints).then(stream => {
        cameraStream = stream;
        cameraAvailable = true;
        cameraPreview.srcObject = stream;
    }).catch(err => {
        console.warn('Camera unavailable, using file input', err);
        cameraAvailable = false;
    });
}

function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(t => t.stop());
        cameraStream = null;
        cameraPreview.srcObject = null;
    }
    cameraAvailable = false;
}

function capturePhoto() {
    if (!cameraStream || !cameraAvailable) {
        cameraFileInput.click();
        return;
    }
    const video = cameraPreview;
    let w = video.videoWidth;
    let h = video.videoHeight;
    const scale = Math.min(1, CAPTURE_MAX_DIM / Math.max(w, h));
    const canvas = document.createElement('canvas');
    canvas.width = Math.round(w * scale);
    canvas.height = Math.round(h * scale);
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg', CAPTURE_QUALITY);
    const blob = dataURItoBlob(dataUrl);
    files.push(blob);
    currentFileIndex = files.length - 1;
    currentFile = blob;
    setupImage(dataUrl);
}

function dataURItoBlob(dataURI) {
    const parts = dataURI.split(',');
    const mimeMatch = parts[0].match(/:(.*?);/);
    const mime = mimeMatch ? mimeMatch[1] : 'image/png';
    const byteString = atob(parts[1]);
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: mime });
}

function compressImageFile(file) {
    return new Promise(resolve => {
        const img = new Image();
        img.onload = () => {
            let w = img.width;
            let h = img.height;
            const scale = Math.min(1, CAPTURE_MAX_DIM / Math.max(w, h));
            const canvas = document.createElement('canvas');
            canvas.width = Math.round(w * scale);
            canvas.height = Math.round(h * scale);
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            canvas.toBlob(blob => {
                resolve(new File([blob], file.name, { type: 'image/jpeg' }));
            }, 'image/jpeg', CAPTURE_QUALITY);
        };
        img.src = URL.createObjectURL(file);
    });
}

async function loadSettings() {
    const url = userInfo ? '/user-settings/' : '/settings/';
    try {
        const resp = await fetch(url);
        if (resp.ok) {
            return await resp.json();
        }
    } catch (e) {
        console.error('Failed to load settings', e);
    }
    return {};
}

function saveSettings(data) {
    const url = userInfo ? '/user-settings/' : '/settings/';
    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).catch(e => console.error('Save settings error', e));
}

function applySettings(cfg) {
    currentSettings = cfg;
    if (cfg.language) {
        currentLang = cfg.language;
        langSelect.value = cfg.language;
    }
    if (cfg.layout) {
        layoutSelect.value = cfg.layout;
    }
    if (cfg.orientation) {
        orientationSelect.value = cfg.orientation;
    }
    if (cfg.arrangement) {
        arrangeSelect.value = cfg.arrangement;
    }
    if (cfg.scale_mode) {
        scaleMode.value = cfg.scale_mode;
        scalePercent.style.display = scaleMode.value === 'percent' ? 'inline-block' : 'none';
    }
    if (cfg.scale_percent !== undefined) {
        scalePercent.value = cfg.scale_percent;
    }
    if (cfg.license_level) {
        currentLicenseLevel = cfg.license_level.toLowerCase();
    } else {
        currentLicenseLevel = 'free';
    }
    isLicensed = false;
    licenseName = '';
    if (cfg.license_key && cfg.license_key.trim()) {
        isLicensed = true;
    }
    if (cfg.license_name) {
        licenseName = cfg.license_name;
    }
    if (brandBox) {
        brandBox.innerHTML = cfg.brand_html || '';
    }
    if (clientLogo) {
        if (cfg.client_logo) {
            clientLogo.src = `/static/logos/${cfg.client_logo}`;
            clientLogo.style.display = 'block';
        } else {
            clientLogo.style.display = 'none';
        }
    }
    if (sponsorLogo) {
        if (cfg.sponsor_logo) {
            sponsorLogo.src = `/static/logos/${cfg.sponsor_logo}`;
            sponsorLogo.style.display = 'block';
        } else {
            sponsorLogo.style.display = 'none';
        }
    }
    if (Array.isArray(cfg.banner_images)) {
        bannerImages = cfg.banner_images;
    } else {
        bannerImages = ['DocCropper_slogan_{{lang}}.png'];
    }
    bannerIndex = 0;
    startBannerRotation();
    if (sloganImg) {
        const scale = parseFloat(cfg.sponsor_scale || 100) / 100;
        sloganImg.style.maxHeight = (200 * scale) + 'px';
    }
    if (cfg.version) {
        appVersion = cfg.version;
    }
}

async function loadTranslations(lang) {
    try {
        const resp = await fetch(`/static/lang/${lang}.json`);
        translations = await resp.json();
    } catch (e) {
        translations = {};
    }
}

function t(key) {
    return translations[key] || key;
}

function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const k = el.getAttribute('data-i18n');
        if (translations[k]) {
            el.textContent = translations[k];
        }
    });
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
        const k = el.getAttribute('data-i18n-title');
        if (translations[k]) {
            el.title = translations[k];
        }
    });
    // also update dynamic option labels
    orientationSelect.querySelectorAll('option').forEach(opt => {
        const k = opt.getAttribute('data-i18n');
        if (translations[k]) {
            opt.textContent = translations[k];
        }
    });
    scaleMode.querySelectorAll('option').forEach(opt => {
        const k = opt.getAttribute('data-i18n');
        if (translations[k]) {
            opt.textContent = translations[k];
        }
    });
    langSelect.querySelectorAll('option').forEach(opt => {
        const k = opt.getAttribute('data-i18n');
        if (translations[k]) {
            opt.textContent = translations[k];
        }
    });
    arrangeSelect.querySelectorAll('option').forEach(opt => {
        const k = opt.getAttribute('data-i18n');
        if (translations[k]) {
            opt.textContent = translations[k];
        }
    });
    processedGallery.querySelectorAll('.thumbButtons button').forEach(btn => {
        const key = btn.dataset.key;
        if (translations[key]) {
            btn.textContent = translations[key];
        }
    });
    if (versionBox && appVersion) {
        versionBox.textContent = translations['version'] ? `${translations['version']} ${appVersion}` : `Version ${appVersion}`;
    }
    if (sloganImg) {
        sloganImg.src = `/static/logos/DocCropper_slogan_${currentLang}.png`;
    }
    if (autoDetectHint) {
        autoDetectHint.textContent = translations['autoHint'] || 'Double click to auto-detect';
    }
    updateWikiLinks();
    startBannerRotation();
}

function updateWikiLinks() {
    const url = `/wiki/${currentLang}/index.html`;
    if (wikiFrame) wikiFrame.src = url;
    if (openWikiLink) openWikiLink.href = url;
}

function updateBannerImage() {
    if (!sloganImg || bannerImages.length === 0) return;
    let img = bannerImages[bannerIndex % bannerImages.length];
    img = img.replace('{{lang}}', currentLang);
    sloganImg.src = `/static/logos/${img}`;
}

function startBannerRotation() {
    updateBannerImage();
    if (bannerTimer) clearInterval(bannerTimer);
    if (bannerImages.length > 1) {
        bannerTimer = setInterval(() => {
            bannerIndex = (bannerIndex + 1) % bannerImages.length;
            updateBannerImage();
        }, 5000);
    }
}

function calculateGrid() {
    const layout = parseInt(layoutSelect.value || '1');
    const orientation = orientationSelect.value || 'portrait';
    const arrangement = arrangeSelect.value || 'auto';
    let cols = 1, rows = 1;
    if (layout === 2) {
        if (arrangement === 'horizontal') {
            cols = 2; rows = 1;
        } else if (arrangement === 'vertical') {
            cols = 1; rows = 2;
        } else if (arrangement === 'auto') {
            if (orientation === 'landscape') { cols = 2; rows = 1; } else { cols = 1; rows = 2; }
        }
    } else if (layout === 4) {
        if (arrangement === 'horizontal') {
            cols = 4; rows = 1;
        } else if (arrangement === 'vertical') {
            cols = 1; rows = 4;
        } else { // grid or auto
            cols = 2; rows = 2;
        }
    }
    return {cols, rows};
}

function updateLayoutPreview() {
    const {cols, rows} = calculateGrid();
    layoutPreview.innerHTML = '';
    const orientation = orientationSelect.value || 'portrait';
    layoutPreview.style.display = 'block';
    layoutPreview.style.width = orientation === 'portrait' ? '200px' : '250px';
    layoutPreview.style.height = orientation === 'portrait' ? '250px' : '200px';
    layoutPreview.style.display = 'grid';
    layoutPreview.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
    layoutPreview.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
    const total = cols * rows;
    for (let i = 0; i < total; i++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        layoutPreview.appendChild(cell);
    }
}

function openModal(src) {
    modalImage.src = src;
    imageModal.style.display = 'block';
}

function rotateImage(index) {
    const img = new Image();
    img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = img.height;
        canvas.height = img.width;
        const ctx = canvas.getContext('2d');
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.rotate(Math.PI / 2);
        ctx.drawImage(img, -img.width / 2, -img.height / 2);
        const rotatedData = canvas.toDataURL('image/png');
        processedImages[index] = rotatedData;
        const container = processedGallery.children[index];
        container.querySelector('img').src = rotatedData;
        if (imageModal.style.display === 'block') {
            openModal(rotatedData);
        }
    };
    img.src = processedImages[index];
}

function deleteImage(index) {
    processedImages.splice(index, 1);
    processedFiles.splice(index, 1);
    processedGallery.removeChild(processedGallery.children[index]);
    refreshThumbnailIndexes();
    if (processedImages.length === 0) {
        exportPdfBtn.style.display = 'none';
        ocrBtn.style.display = 'none';
        ocrOutput.style.display = 'none';
        layoutControls.style.display = 'none';
        signatureControls.style.display = 'none';
        signaturePreview.style.display = 'none';
        signatureHint.style.display = 'none';
    }
}

function editImage(index) {
    editingIndex = index;
    const file = processedFiles[index];
    currentFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        setupImage(e.target.result);
    };
    reader.readAsDataURL(file);
    exportPdfBtn.style.display = 'none';
    ocrBtn.style.display = 'none';
    ocrOutput.style.display = 'none';
    layoutControls.style.display = 'none';
    signatureControls.style.display = 'none';
    statusMessageElement.textContent = 'Edit image and press Process Image to save.';
}


async function shareWhatsApp() {
    if (!currentPdfBlob) return;
    const file = new File([currentPdfBlob], 'DocCropper.pdf', { type: 'application/pdf' });
    if (navigator.canShare && navigator.canShare({ files: [file] })) {
        try {
            await navigator.share({ files: [file], title: 'DocCropper PDF' });
            return;
        } catch (e) {
            console.error('Web Share failed', e);
        }
    }
    let phone = prompt(translations['enterPhone'] || 'Enter phone number (optional)');
    phone = phone ? phone.replace(/[^0-9]/g, '') : '';
    const encoded = encodeURIComponent(translations['shareText'] || 'See attached document.');
    const url = phone ?
        `https://web.whatsapp.com/send?phone=${phone}&text=${encoded}` :
        `https://web.whatsapp.com/send?text=${encoded}`;
    window.open(url, '_blank');
}

async function shareEmail() {
    if (!currentPdfBlob) return;
    const file = new File([currentPdfBlob], 'DocCropper.pdf', { type: 'application/pdf' });
    if (navigator.canShare && navigator.canShare({ files: [file] })) {
        try {
            await navigator.share({ files: [file], title: 'DocCropper PDF' });
            return;
        } catch (e) {
            console.error('Web Share failed', e);
        }
    }
    let email = prompt(translations['enterEmail'] || 'Enter email address (optional)');
    email = email ? encodeURIComponent(email) : '';
    const subject = encodeURIComponent('DocCropper PDF');
    const body = encodeURIComponent(translations['shareText'] || 'See attached document.');
    const mailto = `mailto:${email}?subject=${subject}&body=${body}`;
    window.open(mailto, '_blank');
}

function addThumbnail(src, index) {
    const container = document.createElement('div');
    container.className = 'thumbContainer';
    container.dataset.index = index;

    const imgEl = document.createElement('img');
    imgEl.src = src;
    imgEl.addEventListener('click', () => {
        const idx = Array.from(processedGallery.children).indexOf(container);
        openModal(processedImages[idx]);
    });
    container.appendChild(imgEl);

    const btns = document.createElement('div');
    btns.className = 'thumbButtons';

    const rotateBtn = document.createElement('button');
    rotateBtn.dataset.key = 'rotate';
    rotateBtn.textContent = t('rotate');
    rotateBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = Array.from(processedGallery.children).indexOf(container);
        rotateImage(idx);
    });
    btns.appendChild(rotateBtn);

    const editBtn = document.createElement('button');
    editBtn.dataset.key = 'edit';
    editBtn.textContent = t('edit');
    editBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = Array.from(processedGallery.children).indexOf(container);
        editImage(idx);
    });
    btns.appendChild(editBtn);

    const delBtn = document.createElement('button');
    delBtn.dataset.key = 'delete';
    delBtn.textContent = t('delete');
    delBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = Array.from(processedGallery.children).indexOf(container);
        deleteImage(idx);
    });
    btns.appendChild(delBtn);

    /* Share button removed per feedback */

    container.appendChild(btns);
    processedGallery.appendChild(container);
}

function refreshThumbnailIndexes() {
    Array.from(processedGallery.children).forEach((c, i) => {
        c.dataset.index = i;
    });
}

function updateProcessedArrays() {
    const newImages = [];
    const newFiles = [];
    Array.from(processedGallery.children).forEach(c => {
        const idx = parseInt(c.dataset.index);
        newImages.push(processedImages[idx]);
        newFiles.push(processedFiles[idx]);
    });
    processedImages = newImages;
    processedFiles = newFiles;
    refreshThumbnailIndexes();
}

closeModal.addEventListener('click', () => {
    imageModal.style.display = 'none';
});

imageModal.addEventListener('click', (e) => {
    if (e.target === imageModal) {
        imageModal.style.display = 'none';
    }
});

const draggableElements = {
    p1: document.getElementById('p1'),
    p2: document.getElementById('p2'),
    p3: document.getElementById('p3'),
    p4: document.getElementById('p4'),
};

function updatePolygonAndPoints() {
    const displayedPoints = [];
    // Order: p1 (TL), p2 (TR), p3 (BR), p4 (BL)
    console.log("--- Updating Polygon ---"); // General log to see if function is called

    ['p1', 'p2', 'p3', 'p4'].forEach((id, index) => {
        const dragEl = draggableElements[id];

        // Detailed logging for the first point (p1) for clarity during debugging
        if (index === 0) { // Only log verbosely for p1 to avoid console spam
            console.log(`--- Debug Point ${id} ---`);
            console.log(`Element style.left: '${dragEl.style.left}', style.top: '${dragEl.style.top}'`);
        }

        const initialLeft = parseFloat(dragEl.style.left || "0"); // Ensure string "0" if style is empty
        const initialTop = parseFloat(dragEl.style.top || "0");  // Ensure string "0" if style is empty
        
        const dataX = dragEl.getAttribute('data-x');
        const dataY = dragEl.getAttribute('data-y');
        const translateX = parseFloat(dataX || "0");
        const translateY = parseFloat(dataY || "0");

        if (index === 0) {
            console.log(`InitialLeft: ${initialLeft}, InitialTop: ${initialTop}`);
            console.log(`Attribute data-x: '${dataX}', data-y: '${dataY}'`);
            console.log(`TranslateX: ${translateX}, TranslateY: ${translateY}`);
            console.log(`OffsetWidth: ${dragEl.offsetWidth}, OffsetHeight: ${dragEl.offsetHeight}`);
        }

        const x = initialLeft + translateX + (dragEl.offsetWidth / 2);
        const y = initialTop + translateY + (dragEl.offsetHeight / 2);
        
        if (index === 0) {
            console.log(`Calculated center x: ${x}, y: ${y}`);
        }
        
        displayedPoints.push(x, y);
    });
    currentPointsOnDisplayedImage = displayedPoints;
    // console.log("Displayed Points for SVG:", JSON.stringify(currentPointsOnDisplayedImage));


    const imgWidth = imageElement.offsetWidth;
    const imgHeight = imageElement.offsetHeight;

    if (!fogPathElement) {
        console.error("ERROR: fogPathElement is null in updatePolygonAndPoints. Cannot draw fog.");
        return;
    }

    if (imgWidth > 0 && imgHeight > 0 && currentPointsOnDisplayedImage.length === 8) {
        const p = currentPointsOnDisplayedImage;
        const pathData = `M0,0 H${imgWidth} V${imgHeight} H0 Z ` +
                         `M${p[0]},${p[1]} L${p[2]},${p[3]} L${p[4]},${p[5]} L${p[6]},${p[7]} Z`;
        // console.log("SVG Path Data:", pathData);
        fogPathElement.setAttribute('d', pathData);
    } else {
        // console.log("Skipping fog path update (imgWidth/Height or points invalid)");
        fogPathElement.setAttribute('d', '');
    }
}

function initializeDraggablePoints(imgDisplayWidth, imgDisplayHeight) {
    const pointSize = draggableElements.p1.offsetWidth;

    Object.values(draggableElements).forEach(el => {
        el.style.transform = 'translate(0px, 0px)';
        el.setAttribute('data-x', '0');
        el.setAttribute('data-y', '0');
    });
    
    draggableElements.p1.style.top = `0px`;
    draggableElements.p1.style.left = `0px`;
    draggableElements.p2.style.top = `0px`;
    draggableElements.p2.style.left = `${imgDisplayWidth - pointSize}px`;
    draggableElements.p3.style.top = `${imgDisplayHeight - pointSize}px`;
    draggableElements.p3.style.left = `${imgDisplayWidth - pointSize}px`;
    draggableElements.p4.style.top = `${imgDisplayHeight - pointSize}px`;
    draggableElements.p4.style.left = `0px`;

    updatePolygonAndPoints();
}

function setDraggablePoints(displayPoints) {
    ['p1','p2','p3','p4'].forEach((id, idx) => {
        const el = draggableElements[id];
        const x = displayPoints[idx * 2];
        const y = displayPoints[idx * 2 + 1];
        el.style.transform = 'translate(0px, 0px)';
        el.setAttribute('data-x', '0');
        el.setAttribute('data-y', '0');
        el.style.left = `${x - el.offsetWidth / 2}px`;
        el.style.top = `${y - el.offsetHeight / 2}px`;
    });
    updatePolygonAndPoints();
}

function setupImage(imageUrl) {
    imageElement.src = imageUrl;
    imageElement.style.display = 'block';
    wrapperElement.style.display = 'block';
    if (autoDetectHint) autoDetectHint.style.display = 'block';
    processedImageElement.style.display = 'none';
    statusMessageElement.textContent = 'Loading image...';

    imageElement.onload = () => {
        origW = imageElement.naturalWidth;
        origH = imageElement.naturalHeight;

        if (origW === 0 || origH === 0) {
            console.error("Image natural dimensions are zero. Image might be invalid or not loaded.");
            statusMessageElement.textContent = "Error: Image data is invalid or not fully loaded.";
            wrapperElement.style.display = 'none';
            if (autoDetectHint) autoDetectHint.style.display = 'none';
            adjustControls.style.display = 'none';
            return;
        }

        let displayWidthForWrapper;
        let displayHeightForWrapper;
        const MAX_DISPLAY_WIDTH = Math.min(window.innerWidth * 0.9, 800);
        const MAX_DISPLAY_HEIGHT = Math.min(window.innerHeight * 0.8, 700);

        if (origW > MAX_DISPLAY_WIDTH || origH > MAX_DISPLAY_HEIGHT) {
            const widthRatio = MAX_DISPLAY_WIDTH / origW;
            const heightRatio = MAX_DISPLAY_HEIGHT / origH;
            const scale = Math.min(widthRatio, heightRatio); 
            displayWidthForWrapper = origW * scale;
            displayHeightForWrapper = origH * scale;
        } else {
            displayWidthForWrapper = origW;
            displayHeightForWrapper = origH;
        }
        
        wrapperElement.style.width = `${displayWidthForWrapper}px`;
        wrapperElement.style.height = `${displayHeightForWrapper}px`;

        setTimeout(() => {
            const actualDisplayedWidth = imageElement.offsetWidth;
            const actualDisplayedHeight = imageElement.offsetHeight;

            // console.log(`Image Loaded: Natural WxH: ${origW}x${origH}`);
            // console.log(`Wrapper target WxH: ${displayWidthForWrapper.toFixed(2)}x${displayHeightForWrapper.toFixed(2)}`);
            // console.log(`Image actual displayed WxH: ${actualDisplayedWidth}x${actualDisplayedHeight}`);
            
            // console.log('DEBUG: svgOverlayElement inside setTimeout, before setAttribute:', svgOverlayElement);
            if (!svgOverlayElement) {
                console.error('ERROR: svgOverlayElement is NULL or UNDEFINED at the point of setAttribute!');
                statusMessageElement.textContent = "Critical Error: SVG Overlay element not found. Cannot draw fog.";
                return; 
            }
            if (!fogPathElement) {
                 console.error('ERROR: fogPathElement is NULL or UNDEFINED before initializeDraggablePoints!');
                 statusMessageElement.textContent = "Critical Error: SVG Fog Path element not found.";
                 return;
            }

            if (actualDisplayedWidth === 0 || actualDisplayedHeight === 0) {
                console.error("Image displayed dimensions are zero even after setting wrapper. Check CSS or layout timing.");
                statusMessageElement.textContent = "Error: Image failed to render with correct dimensions.";
                return;
            }

            scaling_factor_w = origW / actualDisplayedWidth;
            scaling_factor_h = origH / actualDisplayedHeight;

            // console.log(`Scaling factors: W=${scaling_factor_w}, H=${scaling_factor_h}`);

            svgOverlayElement.setAttribute('viewBox', `0 0 ${actualDisplayedWidth} ${actualDisplayedHeight}`);
            svgOverlayElement.setAttribute('width', actualDisplayedWidth);
            svgOverlayElement.setAttribute('height', actualDisplayedHeight);
            
            initializeDraggablePoints(actualDisplayedWidth, actualDisplayedHeight);
            statusMessageElement.textContent = 'Image loaded. Adjust points.';
            brightnessRange.value = 100;
            contrastRange.value = 100;
            imageElement.style.filter = 'brightness(100%) contrast(100%)';
            adjustControls.style.display = 'block';
        }, 50);

    };

    imageElement.onerror = () => {
        console.error("Error loading image source.");
        statusMessageElement.textContent = "Error: Could not load the selected image file.";
        wrapperElement.style.display = 'none';
        if (autoDetectHint) autoDetectHint.style.display = 'none';
        adjustControls.style.display = 'none';
    };
}


async function addFiles(newFiles) {
    if (currentLicenseLevel === 'free') {
        const allowed = MAX_IMAGES_FREE - files.length;
        if (allowed <= 0) {
            statusMessageElement.textContent = t('maxImagesFree');
            return;
        }
        newFiles = Array.from(newFiles).slice(0, allowed);
    }
    const compressed = [];
    for (const f of Array.from(newFiles)) {
        try {
            compressed.push(await compressImageFile(f));
        } catch (e) {
            console.warn('Compress failed', e);
            compressed.push(f);
        }
    }
    if (files.length === 0 && processedImages.length === 0) {
        // first batch of files
        files = compressed;
        currentFileIndex = 0;
        processedImages = [];
        processedFiles = [];
        editingIndex = null;
        processedGallery.innerHTML = '';
        exportPdfBtn.style.display = 'none';
        layoutControls.style.display = 'none';
        signatureControls.style.display = 'none';
        if (files.length > 0) {
            currentFile = files[0];
            const reader = new FileReader();
            reader.onload = (e) => {
                setupImage(e.target.result);
            };
            reader.readAsDataURL(files[0]);
        }
    } else {
        // add new files to existing queue
        const startProcessing = currentFileIndex >= files.length;
        files = files.concat(compressed);
        if (startProcessing && newFiles.length > 0) {
            currentFile = files[currentFileIndex];
            const reader = new FileReader();
            reader.onload = (e) => {
                setupImage(e.target.result);
            };
            reader.readAsDataURL(files[currentFileIndex]);
        }
    }

}

imageUploadElement.addEventListener('change', (event) => {
    addFiles(event.target.files);
});

function handleDrop(event) {
    event.preventDefault();
    if (event.dataTransfer && event.dataTransfer.files) {
        addFiles(event.dataTransfer.files);
    }
}

document.addEventListener('dragover', (e) => e.preventDefault());
document.addEventListener('drop', handleDrop);

interact('.draggable').draggable({
    modifiers: [
        interact.modifiers.restrictRect({
            restriction: 'parent',
            endOnly: false,
            elementRect: { left: 0.5, top: 0.5, right: 0.5, bottom: 0.5 }
        })
    ],
    listeners: {
        move(event) {
            const target = event.target;
            let x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
            let y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

            target.style.transform = `translate(${x}px, ${y}px)`;
            target.setAttribute('data-x', x);
            target.setAttribute('data-y', y);

            updatePolygonAndPoints();
        }
    }
});


submitBtn.addEventListener('click', () => {
    if (files.length === 0) {
        statusMessageElement.textContent = t('noImage');
        return;
    }
    if (currentPointsOnDisplayedImage.length !== 8) {
        statusMessageElement.textContent = 'Points not initialized correctly or image not fully loaded.';
        return;
    }
     if (!origW || !origH || !scaling_factor_w || !scaling_factor_h ) {
        statusMessageElement.textContent = 'Image properties (origW, origH, scaling factors) not set. Please re-upload.';
        return;
    }

    statusMessageElement.textContent = 'Processing...';

    const pointsForBackend = currentPointsOnDisplayedImage.map((coord, index) => {
        const scale = index % 2 === 0 ? Number(scaling_factor_w) : Number(scaling_factor_h);
        return coord * scale;
    });

    // console.log("--- Frontend Data for Backend ---");
    // console.log("currentPointsOnDisplayedImage (displayed GUI coords):", JSON.stringify(currentPointsOnDisplayedImage));
    // console.log(`scaling_factor_w: ${scaling_factor_w}, scaling_factor_h: ${scaling_factor_h}`);
    // console.log(`origW (natural): ${origW}, origH (natural): ${origH}`);
    // console.log("pointsForBackend (scaled to original image):", JSON.stringify(pointsForBackend));

    const currentFile = editingIndex !== null ? processedFiles[editingIndex] : files[currentFileIndex];
    const formData = new FormData();
    formData.append('image_file', currentFile);
    formData.append('points', JSON.stringify(pointsForBackend));
    formData.append('original_width', Math.round(origW));
    formData.append('original_height', Math.round(origH));
    formData.append('brightness', brightnessRange.value);
    formData.append('contrast', contrastRange.value);

    fetch('/process-image/', {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.detail || err.message || `HTTP error! status: ${response.status}`) });
        }
        return response.json();
    })
    .then(data => {
        if (data.processed_image) {
            processedImageElement.src = data.processed_image;
            openModal(data.processed_image);
            if (editingIndex !== null) {
                processedImages[editingIndex] = data.processed_image;
                const container = processedGallery.children[editingIndex];
                container.querySelector('img').src = data.processed_image;
                editingIndex = null;
                statusMessageElement.textContent = 'Image reprocessed.';
                wrapperElement.style.display = 'none';
                if (autoDetectHint) autoDetectHint.style.display = 'none';
                adjustControls.style.display = 'none';
                exportPdfBtn.style.display = 'inline-block';
                if (OCR_ENABLED) ocrBtn.style.display = 'inline-block';
                layoutControls.style.display = 'block';
                signatureControls.style.display = 'block';
                updateLayoutPreview();
            } else {
                processedImages.push(data.processed_image);
                processedFiles.push(currentFile);
                addThumbnail(data.processed_image, processedImages.length - 1);
                currentFileIndex++;
                if (currentFileIndex < files.length) {
                    statusMessageElement.textContent = 'Image processed. Load next...';
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        setupImage(e.target.result);
                    };
                    currentFile = files[currentFileIndex];
                    reader.readAsDataURL(currentFile);
                } else {
                    statusMessageElement.textContent = 'All images processed.';
                    wrapperElement.style.display = 'none';
                    if (autoDetectHint) autoDetectHint.style.display = 'none';
                    adjustControls.style.display = 'none';
                    exportPdfBtn.style.display = 'inline-block';
                    if (OCR_ENABLED) ocrBtn.style.display = 'inline-block';
                    layoutControls.style.display = 'block';
                    signatureControls.style.display = 'block';
                    if (signatureImg) {
                        signaturePreview.style.display = 'block';
                        signatureHint.style.display = 'block';
                        signatureExtra.style.display = 'block';
                        populateSignaturePages();
                        renderSignaturePreview();
                    }
                    updateLayoutPreview();
                }
            }
        } else {
            statusMessageElement.textContent = data.message || 'Failed to process image.';
        }
    })
    .catch(error => {
        console.error('Error submitting for processing:', error);
        statusMessageElement.textContent = `Error: ${error.message}`;
    });
});

exportPdfBtn.addEventListener('click', () => {
    if (processedImages.length === 0) {
        statusMessageElement.textContent = 'No processed images to export.';
        return;
    }
    statusMessageElement.textContent = 'Generating PDF...';
    const layout = parseInt(layoutSelect.value || '1');
    const orientation = orientationSelect.value || 'portrait';
    const arrangement = arrangeSelect.value || 'auto';
    const scale_mode = scaleMode.value || 'fit';
    const scale_percent = parseInt(scalePercent.value || '100');
    const remote_sign = remoteSignCheckbox && remoteSignCheckbox.checked;
    const payload = { images: processedImages, layout, orientation, arrangement, scale_mode, scale_percent, signature_image: signatureImageData, signatures, remote_sign };
    fetch('/create-pdf/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.detail || err.message || `HTTP error! status: ${response.status}`) });
        }
        return response.json();
    })
    .then(data => {
        if (data.pdf) {
            const base64 = data.pdf.split(',')[1];
            const byteChars = atob(base64);
            const byteNumbers = new Array(byteChars.length);
            for (let i = 0; i < byteChars.length; i++) {
                byteNumbers[i] = byteChars.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            currentPdfBlob = new Blob([byteArray], {type: 'application/pdf'});
            exportOptions.style.display = 'block';
            statusMessageElement.textContent = 'PDF ready.';
        } else {
            statusMessageElement.textContent = data.message || 'Failed to create PDF.';
        }
    })
    .catch(error => {
        console.error('Error creating PDF:', error);
        statusMessageElement.textContent = `Error: ${error.message}`;
    });
});

if (OCR_ENABLED) {
    ocrBtn.addEventListener('click', () => {
        if (processedImages.length === 0) {
            statusMessageElement.textContent = 'No images for OCR.';
            return;
        }
        statusMessageElement.textContent = 'Extracting text...';
        fetch('/ocr/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ images: processedImages })
        })
        .then(resp => resp.json())
        .then(data => {
            if (data.text) {
                ocrOutput.style.display = 'block';
                ocrOutput.value = data.text;
                statusMessageElement.textContent = translations['ocrResult'] ? translations['ocrResult'] : 'Recognized Text:';
            } else {
                statusMessageElement.textContent = data.message || (translations['ocrNoSupport'] || 'OCR not available');
            }
        })
        .catch(err => {
            statusMessageElement.textContent = 'OCR error';
            console.error('OCR error', err);
        });
    });
}

inputMode.addEventListener('change', updateInputMode);
captureBtn.addEventListener('click', capturePhoto);
cameraSelect.addEventListener('change', () => {
    if (inputMode.value === 'camera') {
        startCamera();
    }
});
let lastTap = 0;
imageElement.addEventListener('dblclick', autoDetectCorners);
imageElement.addEventListener('touchend', (e) => {
    const now = Date.now();
    if (now - lastTap < 300) {
        e.preventDefault();
        autoDetectCorners();
    }
    lastTap = now;
});
helpBtn.addEventListener('click', () => {
    const rect = helpBtn.getBoundingClientRect();
    instructionsBox.style.top = (rect.bottom + window.scrollY) + 'px';
    instructionsBox.classList.toggle('visible');
});
purchaseBtn.addEventListener('click', () => {
    const rect = purchaseBtn.getBoundingClientRect();
    purchaseBox.style.top = (rect.bottom + window.scrollY) + 'px';
    purchaseBox.classList.toggle('visible');
});
licenseBtn.addEventListener('click', () => {
    const rect = licenseBtn.getBoundingClientRect();
    licenseBox.style.display = 'block';
    licenseBox.style.top = (rect.bottom + window.scrollY) + 'px';
    licenseBox.classList.toggle('visible');
});
if (closeBanner) {
    closeBanner.addEventListener('click', () => {
        bannerBox.style.display = 'none';
    });
}

if (downloadPdfBtn) {
    downloadPdfBtn.addEventListener('click', () => {
        if (!currentPdfBlob) return;
        const url = URL.createObjectURL(currentPdfBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'documents.pdf';
        link.click();
        URL.revokeObjectURL(url);
        exportOptions.style.display = 'none';
    });
}

if (waShareBtn) {
    waShareBtn.addEventListener('click', async () => {
        await shareWhatsApp();
        exportOptions.style.display = 'none';
    });
}

if (emailShareBtn) {
    emailShareBtn.addEventListener('click', async () => {
        await shareEmail();
        exportOptions.style.display = 'none';
    });
}
cameraFileInput.addEventListener('change', (e) => {
    if (!e.target.files || e.target.files.length === 0) return;
    addFiles(e.target.files);
});

if (signatureUpload) {
    signatureUpload.addEventListener('change', (e) => {
        const file = e.target.files && e.target.files[0];
        if (!file) { signatureImageData = null; signatureImg = null; signaturePreview.style.display = 'none'; signatureHint.style.display = 'none'; return; }
        const reader = new FileReader();
        reader.onload = (ev) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                const data = ctx.getImageData(0, 0, canvas.width, canvas.height);
                for (let i = 0; i < data.data.length; i += 4) {
                    if (data.data[i] > 240 && data.data[i+1] > 240 && data.data[i+2] > 240) {
                        data.data[i+3] = 0;
                    }
                }
                ctx.putImageData(data, 0, 0);
                signatureImageData = canvas.toDataURL('image/png');
                signatureImg = new Image();
                signatureImg.onload = renderSignaturePreview;
                signatureImg.src = signatureImageData;
                if (processedImages.length > 0) {
                    signaturePreview.style.display = 'block';
                    signatureHint.style.display = 'block';
                    signatureExtra.style.display = 'block';
                    populateSignaturePages();
                    renderSignaturePreview();
                }
            };
            img.src = ev.target.result;
        };
        reader.readAsDataURL(file);
    });
}

if (signaturePreview) {
    signaturePreview.addEventListener('mousedown', (e) => {
        draggingSig = true;
        updateSigPosition(e);
    });
    signaturePreview.addEventListener('mousemove', (e) => {
        if (draggingSig) updateSigPosition(e);
    });
    document.addEventListener('mouseup', () => { draggingSig = false; });
}

langSelect.addEventListener('change', async () => {
    currentLang = langSelect.value;
    await loadTranslations(currentLang);
    applyTranslations();
    renderPaymentBox(currentSettings);
    renderLicenseBox();
    saveSettings({ language: currentLang });
});

layoutSelect.addEventListener('change', () => {
    updateLayoutPreview();
    saveSettings({ layout: parseInt(layoutSelect.value || '1') });
});

orientationSelect.addEventListener('change', () => {
    updateLayoutPreview();
    saveSettings({ orientation: orientationSelect.value });
});

arrangeSelect.addEventListener('change', () => {
    updateLayoutPreview();
    saveSettings({ arrangement: arrangeSelect.value });
});

scaleMode.addEventListener('change', () => {
    scalePercent.style.display = scaleMode.value === 'percent' ? 'inline-block' : 'none';
    saveSettings({ scale_mode: scaleMode.value, scale_percent: parseInt(scalePercent.value || '100') });
});

scalePercent.addEventListener('change', () => {
    saveSettings({ scale_percent: parseInt(scalePercent.value || '100') });
});

brightnessRange.addEventListener('input', () => {
    updateImageFilters();
});

contrastRange.addEventListener('input', () => {
    updateImageFilters();
});

if (signatureScaleInput) {
    signatureScaleInput.addEventListener('input', () => {
        signatureScale = parseFloat(signatureScaleInput.value || '1');
        renderSignaturePreview();
    });
}

if (signaturePage) {
    signaturePage.addEventListener('change', () => {
        renderSignaturePreview();
    });
}

if (addSignatureBtn) {
    addSignatureBtn.addEventListener('click', () => {
        const page = parseInt(signaturePage.value || '0');
        signatures.push({ page, x: signaturePosition.x, y: signaturePosition.y, scale: signatureScale });
        // offset next signature preview so added stamps do not overlap by default
        const OFFSET = 0.05;
        signaturePosition.x += OFFSET;
        if (signaturePosition.x > 0.95) signaturePosition.x = OFFSET;
        signaturePosition.y += OFFSET;
        if (signaturePosition.y > 0.95) signaturePosition.y = OFFSET;
        renderSignaturePreview();
    });
}

function updateImageFilters() {
    const b = brightnessRange.value;
    const c = contrastRange.value;
    imageElement.style.filter = `brightness(${b}%) contrast(${c}%)`;
}

function renderSignaturePreview() {
    if (!signaturePreview || processedImages.length === 0) return;
    const pageIdx = parseInt(signaturePage.value || '0');
    const ctx = signaturePreview.getContext('2d');
    const baseImg = new Image();
    baseImg.onload = () => {
        const cw = signaturePreview.width;
        const ch = signaturePreview.height;
        ctx.clearRect(0, 0, cw, ch);
        ctx.drawImage(baseImg, 0, 0, cw, ch);
        if (signatureImg) {
            const drawOne = (sig) => {
                const scale = (ch / 10) * sig.scale / signatureImg.height;
                const w = signatureImg.width * scale;
                const h = signatureImg.height * scale;
                const x = sig.x * cw - w / 2;
                const y = sig.y * ch - h / 2;
                ctx.drawImage(signatureImg, x, y, w, h);
            };
            signatures.filter(s => s.page === pageIdx).forEach(drawOne);
            // current editing signature
            drawOne({x: signaturePosition.x, y: signaturePosition.y, scale: signatureScale});
        }
    };
    baseImg.src = processedImages[pageIdx];
}

function updateSigPosition(evt) {
    const rect = signaturePreview.getBoundingClientRect();
    const x = (evt.clientX - rect.left) / signaturePreview.width;
    const y = (evt.clientY - rect.top) / signaturePreview.height;
    signaturePosition.x = Math.max(0, Math.min(1, x));
    signaturePosition.y = Math.max(0, Math.min(1, y));
    renderSignaturePreview();
}

function autoDetectCorners() {
    if (!currentFile) return;
    statusMessageElement.textContent = translations['detectingEdges'] || 'Detecting edges...';
    const formData = new FormData();
    formData.append('image_file', currentFile);
    fetch('/detect-corners/', { method: 'POST', body: formData })
        .then(resp => resp.json())
        .then(data => {
            if (data.points && data.points.length === 8) {
                const disp = data.points.map((v,i)=> v / (i%2===0 ? scaling_factor_w : scaling_factor_h));
                setDraggablePoints(disp);
                statusMessageElement.textContent = 'Image loaded. Adjust points.';
            } else {
                statusMessageElement.textContent = data.message || (translations['detectFail'] || 'Detection failed');
            }
        })
        .catch(err => {
            console.error('Detect error', err);
            statusMessageElement.textContent = translations['detectFail'] || 'Detection failed';
        });
}

function populateSignaturePages() {
    signaturePage.innerHTML = '';
    for (let i = 0; i < processedImages.length; i++) {
        const opt = document.createElement('option');
        opt.value = i;
        opt.textContent = (i + 1).toString();
        signaturePage.appendChild(opt);
    }
}

function applyProStatus() {
    // In demo mode features remain usable but PDF pages beyond the first
    // will include a DEMO watermark. We simply update the button style
    // to reflect the license status without disabling functionality.
    if (!isLicensed) {
        exportPdfBtn.classList.remove('pro-disabled');
        imageUploadElement.multiple = true;
        document.querySelectorAll('.shareBtn').forEach(btn => btn.style.display = 'none');
        if (sortable) { sortable.destroy(); sortable = null; }
        if (reorderHint) reorderHint.style.display = 'none';
    } else {
        exportPdfBtn.classList.remove('pro-disabled');
        imageUploadElement.multiple = true;
        document.querySelectorAll('.shareBtn').forEach(btn => btn.style.display = 'inline-block');
        if (!sortable && typeof Sortable !== 'undefined') {
            sortable = Sortable.create(processedGallery, { animation: 150, onEnd: updateProcessedArrays });
        }
        if (reorderHint) reorderHint.style.display = 'block';
    }
}

function renderPaymentBox(cfg) {
    if (!cfg || !cfg.payment_mode) {
        purchaseBox.style.display = 'none';
        return;
    }
    const mode = cfg.payment_mode.toLowerCase();
    if (mode === 'none') {
        purchaseBox.style.display = 'none';
        return;
    }
    purchaseBox.style.display = 'block';
    let html = `<h3>${t('purchaseInfo')}</h3><ul>`;
    let hasItem = false;
    if (mode === 'donation') {
        if (cfg.paypal_link) {
            html += `<li><a href="${cfg.paypal_link}" target="_blank">${t('donatePaypal')}</a></li>`;
            hasItem = true;
        }
    } else if (mode === 'subscription') {
        if (cfg.paypal_link) {
            html += `<li><a href="${cfg.paypal_link}" target="_blank">${t('payPaypal')}</a></li>`;
            hasItem = true;
        }
        if (cfg.stripe_link) {
            html += `<li><a href="${cfg.stripe_link}" target="_blank">${t('payStripe')}</a></li>`;
            hasItem = true;
        }
        if (cfg.bank_info) {
            html += `<li>${t('bankInfo')}: ${cfg.bank_info}</li>`;
            hasItem = true;
        }
    }
    if (!hasItem) {
        html += `<li>${t('noPaymentInfo')}</li>`;
    }
    html += '</ul>';
    purchaseBox.innerHTML = html;
}

function renderLicenseBox() {
    const html = `
    <h3>${t('licenseOptions')}</h3>
    <ul>
        <li><strong>${t('freeEdition')}</strong> - ${t('freeFeatures')}</li>
        <li><strong>${t('proEdition')}</strong> - ${t('proFeatures')}</li>
        <li><strong>${t('fullEdition')}</strong> - ${t('fullFeatures')}</li>
    </ul>`;
    licenseBox.innerHTML = html;
    licenseBox.style.display = 'block';
}

function renderLogin(cfg) {
    if (!cfg || !cfg.google_client_id) {
        loginArea.style.display = 'block';
        loginArea.textContent = t('loginDisabled');
        return;
    }
    loginArea.style.display = 'block';
    function init() {
        google.accounts.id.initialize({
            client_id: cfg.google_client_id,
            callback: async (response) => {
                const res = await fetch('/google-login/', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({token: response.credential})
                });
                if (res.ok) {
                    const data = await res.json();
                    userInfo = data;
                    loginArea.innerHTML = `${t('loggedInAs')} ${data.name || data.email} <button id="signOutBtn">${t('signOut')}</button>`;
                    document.getElementById('signOutBtn').addEventListener('click', async () => {
                        google.accounts.id.disableAutoSelect();
                        userInfo = null;
                        loginArea.innerHTML = '';
                        renderLogin(cfg);
                        const baseCfg = await loadSettings();
                        applySettings(baseCfg);
                        await loadTranslations(currentLang);
                        applyTranslations();
                        renderPaymentBox(baseCfg);
                        licenseInfo.textContent = isLicensed ? `${t('licensedTo')} ${licenseName}` : t('demoVersion');
                        applyProStatus();
                        updateLayoutPreview();
                    });
                    const newCfg = await loadSettings();
                    applySettings(newCfg);
                    await loadTranslations(currentLang);
                    applyTranslations();
                    renderPaymentBox(newCfg);
                    licenseInfo.textContent = isLicensed ? `${t('licensedTo')} ${licenseName}` : t('demoVersion');
                    applyProStatus();
                    updateLayoutPreview();
                } else {
                    loginArea.textContent = t('signInFailed');
                }
            }
        });
        google.accounts.id.renderButton(loginArea, {theme: 'outline', size: 'medium'});
    }
    if (typeof google === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://accounts.google.com/gsi/client';
        script.onload = init;
        document.head.appendChild(script);
    } else {
        init();
    }
}

// initial load of settings and translations
loadSettings().then(async (cfg) => {
    applySettings(cfg);
    await loadTranslations(currentLang);
    applyTranslations();
    renderPaymentBox(cfg);
    renderLicenseBox();
    renderLogin(cfg);
    licenseInfo.textContent = isLicensed ? `${t('licensedTo')} ${licenseName}` : t('demoVersion');
    applyProStatus();
    updateLayoutPreview();
    setupDeviceMode();
    updateInputMode();
});

if (window.safari) {
    history.pushState(null, null, location.href);
    window.onpopstate = function(event) {
        history.go(1);
    };
}
