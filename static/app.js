import interact from 'https://cdn.interactjs.io/v1.10.11/interactjs/index.js';
import { initSignaturePlugin } from './plugins/mobilesign.js';
import { initRemoveBgPlugin } from './plugins/removebg.js';
import { initPdfCompressPlugin } from './plugins/compresspdf.js';

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
const signBtn = document.getElementById('signBtn');
const mobileSignBtn = document.getElementById('mobileSignBtn');
const exportOptions = document.getElementById('exportOptions');
const downloadPdfBtn = document.getElementById('downloadPdfBtn');
const waShareBtn = document.getElementById('waShareBtn');
const emailShareBtn = document.getElementById('emailShareBtn');
const closeExportBtn = document.getElementById('closeExportBtn');
const layoutControls = document.getElementById('layoutControls');
const blankControls = document.getElementById('blankControls');
const layoutSelect = document.getElementById('layoutSelect');
const orientationSelect = document.getElementById('orientationSelect');
const arrangeSelect = document.getElementById('arrangeSelect');
const scaleMode = document.getElementById('scaleMode');
const scalePercent = document.getElementById('scalePercent');
const scalePercentSymbol = document.getElementById('scalePercentSymbol');
const colorModeSelect = document.getElementById('colorModeSelect');
const colorModeLabel = document.querySelector("label[for='colorModeSelect']");
const blankThresholdInput = document.getElementById('blankThreshold');
const blankThresholdLabel = document.querySelector("label[for='blankThreshold']");
const skipBlankCheckbox = document.getElementById('skipBlank');
const removeBlankBtn = document.getElementById('removeBlankBtn');
const restoreBlankBtn = document.getElementById('restoreBlankBtn');
const clearImagesBtn = document.getElementById('clearImagesBtn');
let globalColorMode = 'color';
let blankThreshold = 95;
let skipBlank = true;
const processedImageElement = document.getElementById('processedImage');
const processedGallery = document.getElementById('processedGallery');
const galleryWrapper = document.getElementById('galleryWrapper');
const statusMessageElement = document.getElementById('statusMessage');
const signedPdfLink = document.getElementById('signedPdfLink');
const exportPreviewFrame = document.getElementById('exportPreviewFrame');
const reorderHint = document.getElementById('reorderHint');
const imageModal = document.getElementById('imageModal');
const modalImage = document.getElementById('modalImage');
const closeModal = document.getElementById('closeModal');
const langSelect = document.getElementById('langSelect');
const layoutPreview = document.getElementById('layoutPreview');
const licenseInfo = document.getElementById('licenseInfo');
const purchaseBox = document.getElementById('purchaseBox');
const licenseBox = document.getElementById('licenseBox');
const settingsBox = document.getElementById('settingsBox');
const loginArea = document.getElementById('loginArea');
const layoutToggleBtn = document.getElementById('layoutToggleBtn');
let galleryHorizontal = true;
const brandBox = document.getElementById('brandBox');
const versionBox = document.getElementById('versionBox');
const donateBox = document.getElementById('donateBox');
const donationModal = document.getElementById('donationModal');
const donationFrame = document.getElementById('donationFrame');
const closeDonation = document.getElementById('closeDonation');
const demoNotice = document.getElementById('demoNotice');
const instructionsBox = document.getElementById('instructionsBox');
const helpBtn = document.getElementById('helpBtn');
const purchaseBtn = document.getElementById('purchaseBtn');
const licenseBtn = document.getElementById('licenseBtn');
const settingsBtn = document.getElementById('settingsBtn');
const DEFAULT_PAYPAL = 'https://www.paypal.com/donate/?hosted_button_id=XGKVRL2YQBPDY';
const bannerBox = document.getElementById('brandArea');
const closeBanner = document.getElementById('closeBanner');
const sloganImg = document.getElementById('sloganImg');
const wikiFrame = document.getElementById('wikiFrame');
const openWikiLink = document.getElementById('openWikiLink');
const clientLogo = document.getElementById('clientLogo');
const sponsorLogo = document.getElementById('sponsorLogo');
const sponsorBadge = document.getElementById('sponsorBadge');
const clientBadge = document.getElementById('clientBadge');
const headerLogo = document.getElementById('headerLogo');
const footerLogo = document.getElementById('footerLogo');
const autoDetectHint = document.getElementById('autoDetectHint');
const adjustControls = document.getElementById('adjustControls');
const brightnessRange = document.getElementById('brightnessRange');
const contrastRange = document.getElementById('contrastRange');
const ocrBtn = document.getElementById('ocrBtn');
const ocrOutput = document.getElementById('ocrOutput');
const signatureControls = document.getElementById('signatureControls');
const signatureUpload = document.getElementById('signatureUpload');
const signaturePreview = document.getElementById('signaturePreview');
const signatureHint = document.getElementById('signatureHint');
const signatureExtra = document.getElementById('signatureExtra');
const signaturePage = document.getElementById('signaturePage');
const signatureScaleInput = document.getElementById('signatureScale');
const signatureTargetSelect = document.getElementById('signatureTarget');
const drawSignatureBtn = document.getElementById('drawSignatureBtn');
const signatureModal = document.getElementById('signatureModal');
const drawArea = document.getElementById('drawArea');
const signatureDrawCanvas = document.getElementById('signatureDrawCanvas');
const clearDrawBtn = document.getElementById('clearDrawBtn');
const useDrawBtn = document.getElementById('useDrawBtn');
const addSignatureBtn = document.getElementById('addSignatureBtn');
const discardSignatureBtn = document.getElementById('discardSignatureBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const saveSignatureBtn = document.getElementById('saveSignatureBtn');
const digitalSignBtn = document.getElementById('remoteSignBtn');
const signQR = document.getElementById('signQR');
const signQrImg = document.getElementById('signQrImg');
const signQrHint = document.getElementById('signQrHint');
const legalDisclaimerEl = document.getElementById('legalDisclaimer');
let signatureImageData = null;
let signatureImg = null;
let signaturePosition = { x: 0.85, y: 0.85 };
let signatureScale = 1;
let signatures = [];
let scaleTarget = 'current';
let mobileSignPoints = {};
window.mobileSignPoints = mobileSignPoints;
let pendingSigPos = null;
let draggingSig = false;
let drawing = false;
let lastPoint = null;
const OCR_ENABLED = false;
let bannerImages = [];
let bannerIndex = 0;
let bannerTimer;
let bannerInterval = 5000;
let brandHeight = 80;
let brandGap = 20;
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
const cameraOverlay = document.getElementById('cameraOverlay');
const cameraMargin = document.getElementById('cameraMargin');
const addPhotoBtn = document.getElementById('addPhotoBtn');
const isMobile = /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);
const cameraFileInput = document.getElementById('cameraFileInput');
const CAPTURE_MAX_DIM = 1600;
const CAPTURE_QUALITY = 0.8;

function updateCameraOverlay() {
    if (!cameraOverlay || !cameraMargin) return;
    const m = parseInt(cameraMargin.value || '0');
    cameraOverlay.style.top = m + '%';
    cameraOverlay.style.left = m + '%';
    cameraOverlay.style.width = (100 - 2 * m) + '%';
    cameraOverlay.style.height = (100 - 2 * m) + '%';
}
if (cameraMargin) {
    cameraMargin.addEventListener('input', updateCameraOverlay);
    updateCameraOverlay();
}

let isLicensed = false;
let licenseName = '';
let appVersion = '';
let appVersionDate = '';
let userInfo = null;
let currentLicenseLevel = 'free';
let demoFullMode = false;
const MAX_IMAGES_FREE = 5;
const MAX_FILE_MB = 20;
const MAX_FILE_BYTES = MAX_FILE_MB * 1024 * 1024;
let MAX_UPLOAD_FILES = 10;

let files = [];
let currentFileIndex = 0;
let processedImages = [];
window.processedImages = processedImages;
let originalImages = [];
let bgOriginals = [];
window.bgOriginals = bgOriginals;
let processedFiles = [];
let removedPages = [];
let editingIndex = null;
let cameraStream = null;
let cameraAvailable = false;
let currentPdfBlob = null;
window.lastSignEmail = '';
window.lastSignPhone = '';
window.lastSignName = '';
window.lastSignToken = '';
window.lastSignedUrl = '';
let sortable = null;
let currentFile = null;
let docusealEnabled = false;
let signEnabled = true;
let mobileSignEnabled = false;
let remoteSignEnabled = false;
let removeBgEnabled = false;
let compressEnabled = false;

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

if (digitalSignBtn) {
    digitalSignBtn.addEventListener('click', async () => {
        if (!docusealEnabled) {
            alert(translations['comingSoon'] || 'Coming soon');
            return;
        }
        statusMessageElement.textContent = translations['signingPdf'] || 'Signing PDF...';
        try {
            const resp = await fetch('/docuseal-sign/', {method: 'POST'});
            const data = await resp.json();
            if (data.url) {
                window.open(data.url, '_blank');
                statusMessageElement.textContent = translations['pdfSigned'] || 'PDF signed.';
            } else {
                statusMessageElement.textContent = data.message || 'Error';
            }
        } catch (e) {
            console.error('Docuseal sign error', e);
            statusMessageElement.textContent = translations['docusealError'] || 'Docuseal request failed';
        }
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

async function capturePhoto() {
    if (!cameraStream || !cameraAvailable) {
        cameraFileInput.click();
        return;
    }
    const video = cameraPreview;
    let w = video.videoWidth;
    let h = video.videoHeight;
    const m = cameraMargin ? parseInt(cameraMargin.value || '0') : 0;
    const cropX = (w * m) / 100;
    const cropY = (h * m) / 100;
    const sw = w - 2 * cropX;
    const sh = h - 2 * cropY;
    const scale = Math.min(1, CAPTURE_MAX_DIM / Math.max(sw, sh));
    const canvas = document.createElement('canvas');
    canvas.width = Math.round(sw * scale);
    canvas.height = Math.round(sh * scale);
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, cropX, cropY, sw, sh, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg', CAPTURE_QUALITY);
    const blob = dataURItoBlob(dataUrl);
    const file = new File([blob], `capture_${Date.now()}.jpg`, { type: 'image/jpeg' });
    await addFiles([file]);
    stopCamera();
    if (statusMessageElement) {
        statusMessageElement.textContent = t('photoAdded');
    }
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

function fileToDataURL(file) {
    return new Promise(resolve => {
        const reader = new FileReader();
        reader.onload = e => resolve(e.target.result);
        reader.readAsDataURL(file);
    });
}

async function convertPdfToImages(file) {
    const form = new FormData();
    form.append('pdf_file', file, file.name);
    form.append('threshold', blankThreshold);
    form.append('skip_blank', skipBlank ? '1' : '0');
    const resp = await fetch('/pdf-to-images/', { method: 'POST', body: form });
    if (!resp.ok) {
        if (resp.status === 413) {
            statusMessageElement.textContent = t('fileTooLarge').replace('{mb}', MAX_FILE_MB);
        }
        throw new Error('PDF conversion failed');
    }
    const data = await resp.json();
    const out = [];
    if (Array.isArray(data.images)) {
        data.images.forEach((dataUrl, idx) => {
            const blob = dataURItoBlob(dataUrl);
            out.push(new File([blob], `${file.name.replace(/\.pdf$/i,'')}_${idx+1}.png`, {type: 'image/png'}));
        });
    }
    return out;
}

async function importPdfPages(file) {
    if (currentLicenseLevel === 'free') {
        statusMessageElement.textContent = t('pdfImportPro');
        return;
    }
    if (file.size > MAX_FILE_BYTES) {
        statusMessageElement.textContent = t('fileTooLarge').replace('{mb}', MAX_FILE_MB);
        return;
    }
    showLoading(t('loading'));
    let pages;
    try {
        pages = await convertPdfToImages(file);
    } finally {
        hideLoading();
    }
    let toAdd = pages;
    for (const p of toAdd) {
        let imgFile = p;
        try {
            imgFile = await compressImageFile(p);
        } catch (e) {
            console.warn('Compress failed', e);
        }
        processedFiles.push(imgFile);
        const dataUrl = await fileToDataURL(imgFile);
        processedImages.push(dataUrl);
        originalImages.push(dataUrl);
        bgOriginals.push(null);
        addThumbnail(dataUrl, processedImages.length - 1);
    }
    if (processedImages.length > 0) {
        exportPdfBtn.style.display = 'inline-block';
        if (signBtn && signEnabled) signBtn.style.display = 'inline-block';
        if (mobileSignBtn && mobileSignEnabled) mobileSignBtn.style.display = 'inline-block';
        if (OCR_ENABLED) ocrBtn.style.display = 'inline-block';
        layoutControls.style.display = 'block';
        if (exportOptions) {
            exportOptions.style.display = 'block';
        }
        if (addPhotoBtn) addPhotoBtn.style.display = 'inline-block';
        if (signedPdfLink) signedPdfLink.style.display = 'none';
        if (exportPreviewFrame) exportPreviewFrame.style.display = 'none';
        if (downloadPdfBtn) downloadPdfBtn.style.display = 'none';
        if (waShareBtn) waShareBtn.style.display = 'none';
        if (emailShareBtn) emailShareBtn.style.display = 'none';
        if (blankControls) blankControls.style.display = 'flex';
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
    currentSettings.enable_sponsor_video = !!cfg.enable_sponsor_video;
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
        if (scalePercentSymbol) scalePercentSymbol.style.display = scaleMode.value === 'percent' ? 'inline' : 'none';
    }
    if (cfg.scale_percent !== undefined) {
        scalePercent.value = cfg.scale_percent;
    }
    if (cfg.color_mode) {
        colorModeSelect.value = cfg.color_mode;
        globalColorMode = cfg.color_mode;
    }
    if (cfg.blank_threshold !== undefined) {
        blankThreshold = parseInt(cfg.blank_threshold);
        if (blankThresholdInput) blankThresholdInput.value = blankThreshold;
    }
    if (cfg.skip_blank !== undefined) {
        skipBlank = !!cfg.skip_blank;
        if (skipBlankCheckbox) skipBlankCheckbox.checked = skipBlank;
    }
    if (cfg.max_upload_files !== undefined) {
        MAX_UPLOAD_FILES = parseInt(cfg.max_upload_files);
    }
    if (cfg.license_level) {
        currentLicenseLevel = cfg.license_level.toLowerCase();
    } else {
        currentLicenseLevel = 'free';
    }
    demoFullMode = !!cfg.demo_full_mode;
    isLicensed = false;
    licenseName = '';
    if (cfg.license_key && cfg.license_key.trim()) {
        isLicensed = true;
    }
    if (cfg.license_name) {
        licenseName = cfg.license_name;
    }
    if (cfg.public_url !== undefined) {
        currentSettings.public_url = cfg.public_url;
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
    if (clientBadge) {
        if (cfg.client_logo) {
            clientBadge.src = `/static/logos/${cfg.client_logo}`;
            clientBadge.style.display = 'block';
            clientBadge.style.maxHeight = (cfg.client_logo_height || 125) + 'px';
        } else {
            clientBadge.style.display = 'none';
        }
    }
    if (sponsorBadge) {
        if (cfg.sponsor_logo) {
            sponsorBadge.src = `/static/logos/${cfg.sponsor_logo}`;
            sponsorBadge.style.display = 'block';
            sponsorBadge.style.maxHeight = (cfg.sponsor_logo_height || 125) + 'px';
        } else {
            sponsorBadge.style.display = 'none';
        }
    }
    if (Array.isArray(cfg.banner_images)) {
        bannerImages = cfg.banner_images;
    } else {
        bannerImages = ['DocCropper_slogan_{{lang}}.png'];
    }
    bannerInterval = parseInt(cfg.banner_interval || 5000);
    bannerIndex = 0;
    startBannerRotation();
    brandHeight = parseInt(cfg.brand_height || 80);
    brandGap = parseInt(cfg.brand_gap || 20);
    if (bannerBox) {
        bannerBox.style.paddingLeft = brandGap + 'px';
        bannerBox.style.paddingRight = brandGap + 'px';
    }
    updateBrandSize();
    if (cfg.version) {
        appVersion = cfg.version;
    }
    if (cfg.version_date) {
        appVersionDate = cfg.version_date;
    }
    docusealEnabled = !!cfg.docuseal_api_url;
    signEnabled = cfg.enable_sign !== false;
    mobileSignEnabled = !!cfg.enable_mobilesign;
    remoteSignEnabled = !!cfg.enable_remotesign;
    removeBgEnabled = !!cfg.enable_removebg;
    if (typeof initRemoveBgPlugin === 'function' && Object.keys(translations).length) {
        initRemoveBgPlugin(translations, removeBgEnabled);
    }
    compressEnabled = !!cfg.enable_compresspdf && currentLicenseLevel !== 'free';
    if (digitalSignBtn) {
        digitalSignBtn.disabled = !docusealEnabled || currentLicenseLevel === 'free' || !remoteSignEnabled;
    }
    if (mobileSignBtn) mobileSignBtn.style.display = mobileSignEnabled ? 'inline-block' : 'none';
    // remove background buttons added per thumbnail when enabled
    if (signBtn && !signEnabled) signBtn.style.display = 'none';
    if (demoNotice) demoNotice.style.display = demoFullMode ? 'block' : 'none';
    if (purchaseBtn) {
        if (demoFullMode) {
            purchaseBtn.style.display = 'none';
        } else {
            purchaseBtn.style.display = 'inline-block';
            purchaseBtn.dataset.i18n = 'purchase';
        }
    }
    if (donateBox) {
        const link = currentSettings.paypal_link || DEFAULT_PAYPAL;
        if (cfg.payment_mode && cfg.payment_mode.toLowerCase() === 'donation' && link) {
            donateBox.innerHTML = `<button id="donateBtn"><img src="https://www.paypalobjects.com/it_IT/IT/i/btn/btn_donateCC_LG.gif" alt="Donate"></button>`;
            donateBox.style.display = 'block';
            document.getElementById('donateBtn').addEventListener('click', (e) => {
                e.preventDefault();
                openDonationModal(link);
            });
        } else {
            donateBox.style.display = 'none';
            donateBox.innerHTML = '';
        }
    }
    if (settingsBtn) {
        settingsBtn.style.display = demoFullMode ? 'none' : 'inline-block';
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

function updateGalleryLayout() {
    if (!galleryWrapper || !processedGallery || !layoutToggleBtn) return;
    if (galleryHorizontal) {
        galleryWrapper.classList.add('horizontal');
        galleryWrapper.classList.remove('vertical');
        processedGallery.classList.add('horizontal');
        processedGallery.classList.remove('vertical');
        layoutToggleBtn.textContent = t('verticalView');
    } else {
        galleryWrapper.classList.add('vertical');
        galleryWrapper.classList.remove('horizontal');
        processedGallery.classList.add('vertical');
        processedGallery.classList.remove('horizontal');
        layoutToggleBtn.textContent = t('horizontalView');
    }
}

if (layoutToggleBtn) {
    layoutToggleBtn.addEventListener('click', () => {
        galleryHorizontal = !galleryHorizontal;
        updateGalleryLayout();
    });
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
    processedGallery.querySelectorAll('.thumbMenu option').forEach(opt => {
        const key = opt.dataset.key;
        if (translations[key]) {
            opt.textContent = translations[key];
        }
    });
    if (versionBox && appVersion) {
        const txt = translations['version'] ? `${translations['version']} ${appVersion}` : `Version ${appVersion}`;
        if (appVersionDate) {
            versionBox.innerHTML = txt + '<br>' + appVersionDate;
        } else {
            versionBox.textContent = txt;
        }
    }
    if (sloganImg) {
        sloganImg.src = `/static/logos/DocCropper_slogan_${currentLang}.png`;
    }
    if (autoDetectHint) {
        autoDetectHint.textContent = translations['autoHint'] || 'Double click to auto-detect';
    }
    updateGalleryLayout();
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
        }, bannerInterval);
    }
}

function updateBrandSize() {
    const maxH = Math.min(brandHeight, window.innerHeight * 0.25);
    [clientLogo, sloganImg, sponsorLogo].forEach(el => {
        if (el) el.style.maxHeight = maxH + 'px';
    });
}

window.addEventListener('resize', updateBrandSize);

function showLoading(message) {
    if (!loadingOverlay) return;
    const span = loadingOverlay.querySelector('span');
    span.textContent = message || t('loading');
    loadingOverlay.style.display = 'block';
}

function hideLoading() {
    if (loadingOverlay) loadingOverlay.style.display = 'none';
}

// expose loading helpers for other modules
window.showLoading = showLoading;
window.hideLoading = hideLoading;

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
    if (!layoutPreview || layoutPreview.style.display === 'none') return;
    const {cols, rows} = calculateGrid();
    layoutPreview.innerHTML = '';
    const orientation = orientationSelect.value || 'portrait';
    layoutPreview.style.width = orientation === 'portrait' ? '180px' : '220px';
    layoutPreview.style.height = orientation === 'portrait' ? '220px' : '180px';
    layoutPreview.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
    layoutPreview.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
    const total = cols * rows;
    for (let i = 0; i < total; i++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        const src = processedImages[i];
        if (src) {
            const img = document.createElement('img');
            img.src = src;
            img.style.width = '100%';
            img.style.height = '100%';
            img.style.objectFit = scaleMode.value === 'fit' ? 'cover' : 'contain';
            if (globalColorMode === 'gray') {
                img.style.filter = 'grayscale(100%)';
            } else if (globalColorMode === 'bw') {
                img.style.filter = 'grayscale(100%) contrast(200%)';
            }
            cell.appendChild(img);
        }
        layoutPreview.appendChild(cell);
    }
}
window.updateLayoutPreview = updateLayoutPreview;

function openModal(src) {
    modalImage.src = src;
    imageModal.style.display = 'block';
}

function showSponsorModal() {
    if (!currentSettings.enable_sponsor_video) {
        return Promise.resolve();
    }
    return new Promise(resolve => {
        const modal = document.getElementById('sponsorModal');
        const closeBtn = document.getElementById('closeSponsor');
        const countdownEl = document.getElementById('sponsorCountdown');
        const video = document.getElementById('sponsorVideo');

        video.src = 'https://www.youtube.com/embed/DerpUM0uK9g?autoplay=1';
        modal.style.display = 'block';
        closeBtn.style.display = 'none';
        let remaining = 15;
        countdownEl.textContent = remaining;

        const close = () => {
            video.src = '';
            modal.style.display = 'none';
            closeBtn.removeEventListener('click', close);
            resolve();
        };

        const timer = setInterval(() => {
            remaining--;
            countdownEl.textContent = remaining;
            if (remaining <= 0) {
                clearInterval(timer);
                countdownEl.style.display = 'none';
                close();
            }
        }, 1000);

        closeBtn.addEventListener('click', () => {
            clearInterval(timer);
            close();
        });
    });
}

function openDonationModal(url) {
    window.open(url, '_blank');
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
        if (originalImages[index]) originalImages[index] = rotatedData;
        const container = processedGallery.children[index];
        container.querySelector('img').src = rotatedData;
        if (imageModal.style.display === 'block') {
            openModal(rotatedData);
        }
    };
    img.src = originalImages[index] || processedImages[index];
}

function flipImage(index) {
    const img = new Image();
    img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext('2d');
        ctx.translate(canvas.width, 0);
        ctx.scale(-1, 1);
        ctx.drawImage(img, 0, 0);
        const flippedData = canvas.toDataURL('image/png');
        processedImages[index] = flippedData;
        if (originalImages[index]) originalImages[index] = flippedData;
        const container = processedGallery.children[index];
        container.querySelector('img').src = flippedData;
        window.dispatchEvent(new CustomEvent('imageUpdated', { detail: { index, src: flippedData } }));
    };
    img.src = originalImages[index] || processedImages[index];
}

function invertImage(index) {
    const img = new Image();
    img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext('2d');
        ctx.translate(canvas.width, canvas.height);
        ctx.rotate(Math.PI);
        ctx.drawImage(img, 0, 0);
        const invertedData = canvas.toDataURL('image/png');
        processedImages[index] = invertedData;
        if (originalImages[index]) originalImages[index] = invertedData;
        const container = processedGallery.children[index];
        container.querySelector('img').src = invertedData;
        window.dispatchEvent(new CustomEvent('imageUpdated', { detail: { index, src: invertedData } }));
    };
    img.src = originalImages[index] || processedImages[index];
}

function convertColor(index, mode) {
    if (mode === 'color') {
        if (originalImages[index]) {
            processedImages[index] = originalImages[index];
            const container = processedGallery.children[index];
            container.querySelector('img').src = processedImages[index];
            if (imageModal.style.display === 'block') {
                openModal(processedImages[index]);
            }
            // keep the latest color version for future edits
            originalImages[index] = processedImages[index];
        }
        return;
    }
    const img = new Image();
    img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);
        const data = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const d = data.data;
        for (let i = 0; i < d.length; i += 4) {
            const r = d[i];
            const g = d[i+1];
            const b = d[i+2];
            const gray = 0.299*r + 0.587*g + 0.114*b;
            if (mode === 'gray') {
                d[i] = d[i+1] = d[i+2] = gray;
            } else if (mode === 'bw') {
                const bw = gray > 128 ? 255 : 0;
                d[i] = d[i+1] = d[i+2] = bw;
            }
        }
        ctx.putImageData(data, 0, 0);
        const out = canvas.toDataURL('image/png');
        if (!originalImages[index]) originalImages[index] = processedImages[index];
        processedImages[index] = out;
        const container = processedGallery.children[index];
        container.querySelector('img').src = out;
        if (imageModal.style.display === 'block') {
            openModal(out);
        }
    };
    img.src = originalImages[index] || processedImages[index];
}

function deleteImage(index) {
    processedImages.splice(index, 1);
    originalImages.splice(index, 1);
    bgOriginals.splice(index, 1);
    processedFiles.splice(index, 1);
    processedGallery.removeChild(processedGallery.children[index]);
    refreshThumbnailIndexes();
    if (processedImages.length === 0) {
        exportPdfBtn.style.display = 'none';
        if (signBtn) signBtn.style.display = 'none';
        if (mobileSignBtn) mobileSignBtn.style.display = 'none';
        ocrBtn.style.display = 'none';
        ocrOutput.style.display = 'none';
        layoutControls.style.display = 'none';
        if (exportOptions) exportOptions.style.display = 'none';
        if (signedPdfLink) signedPdfLink.style.display = 'none';
        if (exportPreviewFrame) exportPreviewFrame.style.display = 'none';
        if (downloadPdfBtn) downloadPdfBtn.style.display = 'none';
        if (waShareBtn) waShareBtn.style.display = 'none';
        if (emailShareBtn) emailShareBtn.style.display = 'none';
        if (blankControls) blankControls.style.display = 'none';
        signatureControls.style.display = 'none';
        signaturePreview.style.display = 'none';
        signatureHint.style.display = 'none';
        if (legalDisclaimerEl) legalDisclaimerEl.style.display = 'none';
    }
}

function openSignatureForPage(idx) {
    populateSignaturePages();
    signaturePage.value = idx;
    scaleTarget = 'current';
    updateSignatureTargetOptions();
    signatureControls.style.display = 'block';
    signatureExtra.style.display = 'block';
    signaturePreview.style.display = 'block';
    signatureHint.style.display = 'block';
    if (legalDisclaimerEl) legalDisclaimerEl.style.display = 'block';
    renderSignaturePreview();
}

// Expose signature helpers for global adapters
window.openSignatureForPage = openSignatureForPage;
window.startSign = () => openSignatureForPage(0);

function cropImage(index) {
    editingIndex = index;
    const file = processedFiles[index];
    currentFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        setupImage(e.target.result);
    };
    reader.readAsDataURL(file);
    exportPdfBtn.style.display = 'none';
    if (signBtn) signBtn.style.display = 'none';
    if (mobileSignBtn) mobileSignBtn.style.display = 'none';
    ocrBtn.style.display = 'none';
    ocrOutput.style.display = 'none';
    layoutControls.style.display = 'none';
    if (exportOptions) exportOptions.style.display = 'none';
    if (signedPdfLink) signedPdfLink.style.display = 'none';
    if (exportPreviewFrame) exportPreviewFrame.style.display = 'none';
    if (downloadPdfBtn) downloadPdfBtn.style.display = 'none';
    if (waShareBtn) waShareBtn.style.display = 'none';
    if (emailShareBtn) emailShareBtn.style.display = 'none';
    if (blankControls) blankControls.style.display = 'none';
    signatureControls.style.display = 'none';
    if (legalDisclaimerEl) legalDisclaimerEl.style.display = 'none';
    statusMessageElement.textContent = t('cropHint') || 'Crop image and press Process Image to save.';
}


async function shareWhatsApp(phone) {
    if (!currentPdfBlob) return;
    if (!phone) {
        phone = prompt(translations['enterPhone'] || 'Enter phone number (optional)');
    }
    phone = phone ? phone.replace(/[^0-9]/g, '') : '';
    const url = window.lastSignedUrl || URL.createObjectURL(currentPdfBlob);
    const params = new URLSearchParams({ text: url });
    if (phone) params.set('phone', phone);
    const wa = `https://web.whatsapp.com/send?${params.toString()}`;
    window.open(wa, '_blank');
}

function shareWhatsAppLink(phone, link) {
    if (!link) return;
    phone = phone ? phone.replace(/[^0-9]/g, '') : '';
    const params = new URLSearchParams({ text: link });
    if (phone) params.set('phone', phone);
    const wa = `https://web.whatsapp.com/send?${params.toString()}`;
    window.open(wa, '_blank');
}

async function shareEmail(email) {
    if (!currentPdfBlob) return;
    if (!email) {
        email = prompt(translations['enterEmail'] || 'Enter email address (optional)');
    }
    email = email ? encodeURIComponent(email) : '';
    const url = window.lastSignedUrl || URL.createObjectURL(currentPdfBlob);
    const mailto = `mailto:${email}?body=${encodeURIComponent(url)}`;
    window.open(mailto, '_blank');
}

function shareEmailLink(email, link) {
    if (!link) return;
    const mail = email ? encodeURIComponent(email) : '';
    const mailto = `mailto:${mail}?body=${encodeURIComponent(link)}`;
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

    const menu = document.createElement('select');
    menu.className = 'thumbMenu';
    menu.style.display = 'none';

    function addOption(val, key) {
        const opt = document.createElement('option');
        opt.value = val;
        opt.dataset.key = key;
        opt.textContent = t(key);
        menu.appendChild(opt);
    }

    addOption('', 'chooseAction');
    addOption('rotate', 'rotate');
    addOption('flip', 'flip');
    addOption('invert', 'invert');
    if (isLicensed && currentLicenseLevel !== 'free') {
        addOption('gray', 'toGray');
        addOption('bw', 'toBW');
        addOption('color', 'toColor');
    }
    addOption('edit', 'edit');
    if (removeBgEnabled) {
        addOption('removeBg', 'removeBg');
    }
    addOption('delete', 'delete');

    const cropBtnEl = document.createElement('button');
    cropBtnEl.className = 'thumbBtn cropBtn';
    cropBtnEl.textContent = '✂';
    cropBtnEl.title = t('edit');
    cropBtnEl.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = parseInt(container.dataset.index);
        cropImage(idx);
    });
    container.appendChild(cropBtnEl);

    const delBtnEl = document.createElement('button');
    delBtnEl.className = 'thumbBtn deleteBtn';
    delBtnEl.textContent = '✖';
    delBtnEl.title = t('delete');
    delBtnEl.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = parseInt(container.dataset.index);
        deleteImage(idx);
    });
    container.appendChild(delBtnEl);
    const actions = document.createElement('div');
    actions.className = 'thumbActions';

    const rotateBtnEl = document.createElement('button');
    rotateBtnEl.className = 'thumbBtn rotateBtn';
    rotateBtnEl.textContent = '↻';
    rotateBtnEl.title = t('rotate');
    rotateBtnEl.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = parseInt(container.dataset.index);
        rotateImage(idx);
    });
    actions.appendChild(rotateBtnEl);

    const flipBtnEl = document.createElement('button');
    flipBtnEl.className = 'thumbBtn flipBtn';
    flipBtnEl.textContent = '⇄';
    flipBtnEl.title = t('flip');
    flipBtnEl.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = parseInt(container.dataset.index);
        flipImage(idx);
    });
    actions.appendChild(flipBtnEl);

    const invertBtnEl = document.createElement('button');
    invertBtnEl.className = 'thumbBtn invertBtn';
    invertBtnEl.textContent = '⇅';
    invertBtnEl.title = t('invert');
    invertBtnEl.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = parseInt(container.dataset.index);
        invertImage(idx);
    });
    actions.appendChild(invertBtnEl);

    let thrWrap;
    if (removeBgEnabled) {
        const bgBtnEl = document.createElement('button');
        bgBtnEl.className = 'thumbBtn removeBgBtn';
        if (bgOriginals[index]) {
            bgBtnEl.textContent = '↩';
            bgBtnEl.title = t('restoreBg');
        } else {
            bgBtnEl.textContent = '⌦';
            bgBtnEl.title = t('removeBg');
        }
        bgBtnEl.addEventListener('click', (e) => {
            e.stopPropagation();
            const idx = parseInt(container.dataset.index);
            if (typeof window.removeBackground === 'function') {
                window.removeBackground(idx);
            }
        });
        actions.appendChild(bgBtnEl);

        thrWrap = document.createElement('div');
        thrWrap.className = 'thumbBgThreshold';
        const thrInput = document.createElement('input');
        thrInput.type = 'range';
        thrInput.min = '0';
        thrInput.max = '100';
        thrInput.value = '50';
        thrInput.title = t('removeBgThresholdPrompt');
        thrInput.addEventListener('input', (e) => {
            e.stopPropagation();
            if (typeof window.setRemoveBgThreshold === 'function') {
                window.setRemoveBgThreshold(parseInt(e.target.value, 10));
            }
        });
        thrWrap.appendChild(thrInput);
    }

    if (signEnabled) {
        const signPageBtn = document.createElement('button');
        signPageBtn.className = 'thumbBtn signPageBtn';
        signPageBtn.textContent = '✒';
        signPageBtn.title = t('sign');
        signPageBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const idx = parseInt(container.dataset.index);
            openSignatureForPage(idx);
        });
        actions.appendChild(signPageBtn);
    }

    if (isLicensed && currentLicenseLevel !== 'free') {
        const grayBtn = document.createElement('button');
        grayBtn.className = 'thumbBtn thumbCircle grayBtn';
        grayBtn.title = t('toGray');
        grayBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const idx = parseInt(container.dataset.index);
            convertColor(idx, 'gray');
        });
        actions.appendChild(grayBtn);

        const bwBtn = document.createElement('button');
        bwBtn.className = 'thumbBtn thumbCircle bwBtn';
        bwBtn.title = t('toBW');
        bwBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const idx = parseInt(container.dataset.index);
            convertColor(idx, 'bw');
        });
        actions.appendChild(bwBtn);

        const colBtn = document.createElement('button');
        colBtn.className = 'thumbBtn thumbCircle colorBtn';
        colBtn.title = t('toColor');
        colBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const idx = parseInt(container.dataset.index);
            convertColor(idx, 'color');
        });
        actions.appendChild(colBtn);
    }

    menu.addEventListener('change', (e) => {
        const val = menu.value;
        const idx = Array.from(processedGallery.children).indexOf(container);
        switch (val) {
            case 'rotate':
                rotateImage(idx);
                break;
            case 'flip':
                flipImage(idx);
                break;
            case 'invert':
                invertImage(idx);
                break;
            case 'gray':
                convertColor(idx, 'gray');
                break;
            case 'bw':
                convertColor(idx, 'bw');
                break;
            case 'color':
                convertColor(idx, 'color');
                break;
            case 'edit':
                cropImage(idx);
                break;
            case 'delete':
                deleteImage(idx);
                break;
            case 'removeBg':
                if (typeof window.removeBackground === 'function') window.removeBackground(idx);
                break;
        }
        menu.value = '';
    });

    container.appendChild(actions);
    if (removeBgEnabled) container.appendChild(thrWrap);
    container.appendChild(menu);
    processedGallery.appendChild(container);
    originalImages[index] = src;
}

function refreshThumbnailIndexes() {
    Array.from(processedGallery.children).forEach((c, i) => {
        c.dataset.index = i;
    });
}

function updateProcessedArrays() {
    const newImages = [];
    const newFiles = [];
    const newOriginals = [];
    const newBg = [];
    Array.from(processedGallery.children).forEach(c => {
        const idx = parseInt(c.dataset.index);
        newImages.push(processedImages[idx]);
        newFiles.push(processedFiles[idx]);
        newOriginals.push(originalImages[idx]);
        newBg.push(bgOriginals[idx]);
    });
    processedImages = newImages;
    window.processedImages = processedImages;
    processedFiles = newFiles;
    originalImages = newOriginals;
    bgOriginals = newBg;
    window.bgOriginals = bgOriginals;
    refreshThumbnailIndexes();
}

function rebuildGallery() {
    processedGallery.innerHTML = '';
    processedImages.forEach((img, idx) => addThumbnail(img, idx));
    if (sortable) {
        sortable.destroy();
        sortable = null;
    }
    if (typeof Sortable !== 'undefined') {
        sortable = Sortable.create(processedGallery, {
            animation: 150,
            onEnd: updateProcessedArrays,
            handle: 'img',
            filter: '.thumbMenu, .thumbBtn',
            preventOnFilter: false
        });
    }
    refreshThumbnailIndexes();
}

async function isBlankImage(src, thr) {
    return new Promise(resolve => {
        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement('canvas');
            const scale = Math.min(100 / img.width, 100 / img.height, 1);
            canvas.width = Math.floor(img.width * scale);
            canvas.height = Math.floor(img.height * scale);
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
            let white = 0;
            for (let i = 0; i < data.length; i += 4) {
                if (data[i] > 240 && data[i + 1] > 240 && data[i + 2] > 240) white++;
            }
            const ratio = white / (data.length / 4);
            resolve(ratio >= thr);
        };
        img.src = src;
    });
}

async function removeBlankPages() {
    await showSponsorModal();
    showLoading(t('loading'));
    const thr = blankThreshold / 100;
    removedPages = [];
    const keepImages = [];
    const keepFiles = [];
    const keepOriginals = [];
    const keepBg = [];
    for (let i = 0; i < processedImages.length; i++) {
        const blank = await isBlankImage(processedImages[i], thr);
        if (blank) {
            removedPages.push({ index: i, image: processedImages[i], file: processedFiles[i], original: originalImages[i], bgOriginal: bgOriginals[i] });
        } else {
            keepImages.push(processedImages[i]);
            keepFiles.push(processedFiles[i]);
            keepOriginals.push(originalImages[i]);
            keepBg.push(bgOriginals[i]);
        }
    }
    processedImages = keepImages;
    window.processedImages = processedImages;
    processedFiles = keepFiles;
    originalImages = keepOriginals;
    bgOriginals = keepBg;
    window.bgOriginals = bgOriginals;
    rebuildGallery();
    hideLoading();
    if (removedPages.length > 0) {
        restoreBlankBtn.style.display = 'inline-block';
        statusMessageElement.textContent = t('pagesRemoved').replace('{n}', removedPages.length);
    }
}

function restoreBlankPages() {
    if (removedPages.length === 0) return;
    removedPages.sort((a, b) => a.index - b.index);
    for (const p of removedPages) {
        const idx = Math.min(p.index, processedImages.length);
        processedImages.splice(idx, 0, p.image);
        processedFiles.splice(idx, 0, p.file);
        originalImages.splice(idx, 0, p.original);
        bgOriginals.splice(idx, 0, p.bgOriginal || null);
    }
    removedPages = [];
    rebuildGallery();
    restoreBlankBtn.style.display = 'none';
    statusMessageElement.textContent = t('pagesRestored');
}

closeModal.addEventListener('click', () => {
    imageModal.style.display = 'none';
});

imageModal.addEventListener('click', (e) => {
    if (e.target === imageModal) {
        imageModal.style.display = 'none';
    }
});

closeDonation.addEventListener('click', () => {
    donationModal.style.display = 'none';
    donationFrame.src = '';
});

donationModal.addEventListener('click', (e) => {
    if (e.target === donationModal) {
        donationModal.style.display = 'none';
        donationFrame.src = '';
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
    imageModal.style.display = 'none';
    modalImage.src = '';
    processedImageElement.style.display = 'none';
    processedImageElement.src = '';
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

    imageElement.src = imageUrl;
    imageElement.style.display = 'block';
    wrapperElement.style.display = 'block';
    if (autoDetectHint) autoDetectHint.style.display = 'block';
    statusMessageElement.textContent = 'Loading image...';
}


async function addFiles(newFiles) {
    showLoading(t('loading'));
    if (currentLicenseLevel === 'free') {
        const allowed = MAX_IMAGES_FREE - processedImages.length;
        if (allowed <= 0) {
            statusMessageElement.textContent = t('maxImagesFree');
            hideLoading();
            return;
        }
        newFiles = Array.from(newFiles).slice(0, allowed);
    }
    const compressed = [];
    for (const f of Array.from(newFiles)) {
        if (f.size > MAX_FILE_BYTES) {
            statusMessageElement.textContent = t('fileTooLarge').replace('{mb}', MAX_FILE_MB);
            continue;
        }
        try {
            compressed.push(await compressImageFile(f));
        } catch (e) {
            console.warn('Compress failed', e);
            compressed.push(f);
        }
    }
    if (processedImages.length === 0 && files.length === 0) {
        files = [];
        currentFileIndex = 0;
        processedGallery.innerHTML = '';
        processedFiles = [];
        originalImages = [];
        bgOriginals = [];
        window.bgOriginals = bgOriginals;
        editingIndex = null;
        if (addPhotoBtn) addPhotoBtn.style.display = 'none';
    }
    for (const f of compressed) {
        files.push(f);
        processedFiles.push(f);
        const dataUrl = await fileToDataURL(f);
        processedImages.push(dataUrl);
        originalImages.push(dataUrl);
        bgOriginals.push(null);
        addThumbnail(dataUrl, processedImages.length - 1);
    }
    if (files.length > processedImages.length && wrapperElement.style.display === 'none') {
        currentFile = files[currentFileIndex];
        const reader = new FileReader();
        reader.onload = (e) => {
            setupImage(e.target.result);
        };
        reader.readAsDataURL(currentFile);
    }
    if (files.length > 0) {
        exportPdfBtn.style.display = 'inline-block';
        if (signBtn && signEnabled) signBtn.style.display = 'inline-block';
        if (mobileSignBtn && mobileSignEnabled) mobileSignBtn.style.display = 'inline-block';
        if (OCR_ENABLED) ocrBtn.style.display = 'inline-block';
        layoutControls.style.display = 'block';
        if (exportOptions) {
            exportOptions.style.display = 'block';
        }
        if (signedPdfLink) signedPdfLink.style.display = 'none';
        if (exportPreviewFrame) exportPreviewFrame.style.display = 'none';
        if (downloadPdfBtn) downloadPdfBtn.style.display = 'none';
        if (waShareBtn) waShareBtn.style.display = 'none';
        if (emailShareBtn) emailShareBtn.style.display = 'none';
        if (blankControls) blankControls.style.display = 'flex';
        if (signatureImg) {
            signaturePreview.style.display = 'block';
            signatureHint.style.display = 'block';
            signatureExtra.style.display = 'block';
            populateSignaturePages();
            renderSignaturePreview();
        }
        updateLayoutPreview();
    }
    hideLoading();
    if (imageUploadElement) imageUploadElement.value = '';
}

imageUploadElement.addEventListener('change', async (event) => {
    const all = Array.from(event.target.files);
    const list = all.slice(0, MAX_UPLOAD_FILES);
    if (all.length > MAX_UPLOAD_FILES) {
        statusMessageElement.textContent = t('maxUploadLimit').replace('{n}', MAX_UPLOAD_FILES);
    }
    const toProcess = [];
    for (const f of list) {
        if (f.type === 'application/pdf' || f.name.toLowerCase().endsWith('.pdf')) {
            if (currentLicenseLevel === 'free') {
                statusMessageElement.textContent = t('pdfImportPro');
            } else {
                try {
                    await importPdfPages(f);
                } catch (e) {
                    console.error('PDF conversion failed', e);
                }
            }
        } else {
            toProcess.push(f);
        }
    }
    if (toProcess.length) await addFiles(toProcess);
    imageUploadElement.value = '';
});

async function handleDrop(event) {
    event.preventDefault();
    if (event.dataTransfer && event.dataTransfer.files) {
        const all = Array.from(event.dataTransfer.files);
        const list = all.slice(0, MAX_UPLOAD_FILES);
        if (all.length > MAX_UPLOAD_FILES) {
            statusMessageElement.textContent = t('maxUploadLimit').replace('{n}', MAX_UPLOAD_FILES);
        }
        const toProcess = [];
        for (const f of list) {
            if (f.type === 'application/pdf' || f.name.toLowerCase().endsWith('.pdf')) {
                if (currentLicenseLevel === 'free') {
                    statusMessageElement.textContent = t('pdfImportPro');
                } else {
                    try {
                        await importPdfPages(f);
                    } catch (e) {
                        console.error('PDF conversion failed', e);
                    }
                }
            } else {
                toProcess.push(f);
            }
        }
        if (toProcess.length) await addFiles(toProcess);
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
            if (response.status === 413) {
                statusMessageElement.textContent = t('fileTooLarge').replace('{mb}', MAX_FILE_MB);
            }
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
                originalImages[editingIndex] = data.processed_image;
                const container = processedGallery.children[editingIndex];
                container.querySelector('img').src = data.processed_image;
                editingIndex = null;
                statusMessageElement.textContent = 'Image reprocessed.';
                wrapperElement.style.display = 'none';
                if (autoDetectHint) autoDetectHint.style.display = 'none';
                adjustControls.style.display = 'none';
                exportPdfBtn.style.display = 'inline-block';
                if (signBtn && signEnabled) signBtn.style.display = 'inline-block';
                if (mobileSignBtn && mobileSignEnabled) mobileSignBtn.style.display = 'inline-block';
                if (OCR_ENABLED) ocrBtn.style.display = 'inline-block';
        layoutControls.style.display = 'block';
        if (exportOptions) {
            exportOptions.style.display = 'block';
        }
        if (signedPdfLink) signedPdfLink.style.display = 'none';
        if (exportPreviewFrame) exportPreviewFrame.style.display = 'none';
        if (downloadPdfBtn) downloadPdfBtn.style.display = 'none';
        if (waShareBtn) waShareBtn.style.display = 'none';
        if (emailShareBtn) emailShareBtn.style.display = 'none';
        if (blankControls) blankControls.style.display = 'flex';
                updateLayoutPreview();
            } else {
                processedImages[currentFileIndex] = data.processed_image;
                originalImages[currentFileIndex] = data.processed_image;
                processedFiles[currentFileIndex] = currentFile;
                const container = processedGallery.children[currentFileIndex];
                if (container) container.querySelector('img').src = data.processed_image;
                exportPdfBtn.style.display = 'inline-block';
                if (signBtn && signEnabled) signBtn.style.display = 'inline-block';
                if (mobileSignBtn && mobileSignEnabled) mobileSignBtn.style.display = 'inline-block';
                if (OCR_ENABLED) ocrBtn.style.display = 'inline-block';
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
                    if (signBtn && signEnabled) signBtn.style.display = 'inline-block';
                    if (mobileSignBtn && mobileSignEnabled) mobileSignBtn.style.display = 'inline-block';
                    if (OCR_ENABLED) ocrBtn.style.display = 'inline-block';
                    layoutControls.style.display = 'block';
                    if (exportOptions) {
                        exportOptions.style.display = 'block';
                    }
                    if (signedPdfLink) signedPdfLink.style.display = 'none';
                    if (exportPreviewFrame) exportPreviewFrame.style.display = 'none';
                    if (downloadPdfBtn) downloadPdfBtn.style.display = 'none';
                    if (waShareBtn) waShareBtn.style.display = 'none';
                    if (emailShareBtn) emailShareBtn.style.display = 'none';
                    if (blankControls) blankControls.style.display = 'flex';
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

async function generatePdf() {
    if (processedImages.length === 0) {
        statusMessageElement.textContent = 'No processed images to export.';
        return;
    }
    await mergeAllSignatures();
    if (signedPdfLink) signedPdfLink.style.display = 'none';
    if (exportPreviewFrame) exportPreviewFrame.style.display = 'none';
    statusMessageElement.textContent = 'Generating PDF...';
    const layout = parseInt(layoutSelect.value || '1');
    const orientation = orientationSelect.value || 'portrait';
    const arrangement = arrangeSelect.value || 'auto';
    const scale_mode = scaleMode.value || 'fit';
    const scale_percent = parseInt(scalePercent.value || '100');
    const compression = window.getCompressionLevel ? window.getCompressionLevel() : 'none';
    const jpeg_quality = window.getJpegQuality ? window.getJpegQuality() : 75;
    const pdfa_version = window.getPdfaVersion ? window.getPdfaVersion() : null;
    const payload = { images: processedImages, layout, orientation, arrangement, scale_mode, scale_percent, color_mode: globalColorMode, signature_image: signatureImageData, signatures, remove_signature_bg: window.removeSignatureBackground !== false, compression, jpeg_quality, pdfa_version };
    if (window.lastSignEmail || window.lastSignPhone || window.lastSignName) {
        payload.sign_info = { email: window.lastSignEmail, phone: window.lastSignPhone, name: window.lastSignName };
    }
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
            if (downloadPdfBtn) downloadPdfBtn.style.display = 'inline-block';
            if (waShareBtn) waShareBtn.style.display = 'inline-block';
            if (emailShareBtn) emailShareBtn.style.display = 'inline-block';
            statusMessageElement.textContent = 'PDF ready.';
            if (window.lastSignToken) {
                const url = window.lastSignedUrl || URL.createObjectURL(currentPdfBlob);
                if (signedPdfLink) {
                    signedPdfLink.href = url;
                    signedPdfLink.textContent = translations['downloadPdf'] || 'Download PDF';
                    signedPdfLink.style.display = 'inline';
                }
                if (exportPreviewFrame) {
                    exportPreviewFrame.src = url + '#toolbar=0&navpanes=0';
                    exportPreviewFrame.style.display = 'block';
                }
                if (window.lastSignPhone) shareWhatsAppLink(window.lastSignPhone, url);
                if (window.lastSignEmail) shareEmailLink(window.lastSignEmail, url);
            } else {
                if (window.lastSignPhone) {
                    shareWhatsApp(window.lastSignPhone);
                }
                if (window.lastSignEmail) {
                    shareEmail(window.lastSignEmail);
                }
                if (signedPdfLink) {
                    const url = URL.createObjectURL(currentPdfBlob);
                    signedPdfLink.href = url;
                    signedPdfLink.textContent = translations['downloadPdf'] || 'Download PDF';
                    signedPdfLink.style.display = 'inline';
                    if (exportPreviewFrame) {
                        exportPreviewFrame.src = url + '#toolbar=0&navpanes=0';
                        exportPreviewFrame.style.display = 'block';
                    }
                }
            }
        } else {
            statusMessageElement.textContent = data.message || 'Failed to create PDF.';
        }
    })
    .catch(error => {
        console.error('Error creating PDF:', error);
        statusMessageElement.textContent = `Error: ${error.message}`;
    });
}

exportPdfBtn.addEventListener('click', async () => {
    await showSponsorModal();
    await generatePdf();
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
if (addPhotoBtn) {
    addPhotoBtn.addEventListener('click', () => {
        wrapperElement.style.display = 'none';
        imageElement.style.display = 'none';
        if (adjustControls) adjustControls.style.display = 'none';
        if (statusMessageElement) statusMessageElement.textContent = '';
        inputMode.value = 'camera';
        updateInputMode();
    });
}
cameraSelect.addEventListener('change', () => {
    if (inputMode.value === 'camera') {
        startCamera();
    }
});
let lastTap = 0;
imageElement.addEventListener('dblclick', (e) => {
    console.debug('dblclick on imageElement', { x: e.clientX, y: e.clientY });
    autoDetectCorners();
});
imageElement.addEventListener('touchstart', (e) => {
    const now = Date.now();
    if (now - lastTap < 300) {
        e.preventDefault();
        console.debug('double tap on imageElement');
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
    if (demoFullMode) {
        const link = currentSettings.paypal_link || DEFAULT_PAYPAL;
        window.open(link, '_blank');
    } else {
        const rect = purchaseBtn.getBoundingClientRect();
        purchaseBox.style.top = (rect.bottom + window.scrollY) + 'px';
        purchaseBox.classList.toggle('visible');
    }
});
licenseBtn.addEventListener('click', () => {
    const rect = licenseBtn.getBoundingClientRect();
    licenseBox.style.display = 'block';
    licenseBox.style.top = (rect.bottom + window.scrollY) + 'px';
    licenseBox.classList.toggle('visible');
});
if (signBtn) {
    signBtn.addEventListener('click', () => {
        openSignatureForPage(0);
    });
}
settingsBtn.addEventListener('click', () => {
    const rect = settingsBtn.getBoundingClientRect();
    settingsBox.style.display = 'block';
    settingsBox.style.top = (rect.bottom + window.scrollY) + 'px';
    renderSettingsBox();
    settingsBox.classList.toggle('visible');
});
if (closeBanner) {
    closeBanner.addEventListener('click', () => {
        bannerBox.style.display = 'none';
    });
}
if (headerLogo) {
    headerLogo.addEventListener('click', () => {
        location.reload();
    });
}
if (footerLogo) {
    footerLogo.addEventListener('click', () => {
        window.location.href = 'https://www.iltuoconsulenteit.it/site/index.php/applicazioni/doccropper';
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
    });
}

if (waShareBtn) {
    waShareBtn.addEventListener('click', async () => {
        await shareWhatsApp(window.lastSignPhone);
    });
}

if (emailShareBtn) {
    emailShareBtn.addEventListener('click', async () => {
        await shareEmail(window.lastSignEmail);
    });
}

cameraFileInput.addEventListener('change', (e) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const all = Array.from(e.target.files);
    const list = all.slice(0, MAX_UPLOAD_FILES);
    if (all.length > MAX_UPLOAD_FILES) {
        statusMessageElement.textContent = t('maxUploadLimit').replace('{n}', MAX_UPLOAD_FILES);
    }
    addFiles(list);
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

if (drawSignatureBtn && signatureDrawCanvas) {
    const ctx = signatureDrawCanvas.getContext('2d');
    const getPos = (e) => {
        const rect = signatureDrawCanvas.getBoundingClientRect();
        const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
        const y = (e.touches ? e.touches[0].clientY : e.clientY) - rect.top;
        return { x, y };
    };
    const startDraw = (e) => { drawing = true; lastPoint = getPos(e); e.preventDefault(); };
    const moveDraw = (e) => {
        if (!drawing) return;
        const p = getPos(e);
        ctx.beginPath();
        ctx.moveTo(lastPoint.x, lastPoint.y);
        ctx.lineTo(p.x, p.y);
        ctx.stroke();
        lastPoint = p;
        e.preventDefault();
    };
    const endDraw = () => { drawing = false; };
    signatureDrawCanvas.addEventListener('mousedown', startDraw);
    signatureDrawCanvas.addEventListener('touchstart', startDraw);
    signatureDrawCanvas.addEventListener('mousemove', moveDraw);
    signatureDrawCanvas.addEventListener('touchmove', moveDraw);
    document.addEventListener('mouseup', endDraw);
    document.addEventListener('touchend', endDraw);
    clearDrawBtn.addEventListener('click', () => { ctx.clearRect(0,0,signatureDrawCanvas.width,signatureDrawCanvas.height); });
    useDrawBtn.addEventListener('click', () => {
        signatureImageData = signatureDrawCanvas.toDataURL('image/png');
        signatureImg = new Image();
        signatureImg.onload = () => {
            signatureModal.style.display = 'none';
            if (pendingSigPos) {
                signaturePosition.x = pendingSigPos.x;
                signaturePosition.y = pendingSigPos.y;
                pendingSigPos = null;
            }
            if (processedImages.length > 0) {
                signaturePreview.style.display = 'block';
                signatureHint.style.display = 'block';
                signatureExtra.style.display = 'block';
                populateSignaturePages();
                renderSignaturePreview();
            }
        };
        signatureImg.src = signatureImageData;
    });
    if (signatureModal) {
        signatureModal.addEventListener('click', (e) => {
            if (e.target === signatureModal) signatureModal.style.display = 'none';
        });
    }
    drawSignatureBtn.addEventListener('click', () => {
        signatureModal.style.display = signatureModal.style.display === 'none' ? 'block' : 'none';
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
    signaturePreview.addEventListener('dblclick', (e) => {
        const rect = signaturePreview.getBoundingClientRect();
        const x = (e.clientX - rect.left) / signaturePreview.width;
        const y = (e.clientY - rect.top) / signaturePreview.height;
        console.debug('dblclick on signaturePreview', { clientX: e.clientX, clientY: e.clientY, x, y });
        if (signatureImg) {
            signaturePosition.x = x;
            signaturePosition.y = y;
            addCurrentSignature();
        } else {
            pendingSigPos = { x, y };
            signatureModal.style.display = 'block';
        }
    });
}

langSelect.addEventListener('change', async () => {
    currentLang = langSelect.value;
    await loadTranslations(currentLang);
    applyTranslations();
    renderPaymentBox(currentSettings);
    renderLicenseBox();
    settingsBox.innerHTML = '';
    saveSettings({ language: currentLang });
});

function maybeRegenerate() {
    if (currentPdfBlob) generatePdf();
}

layoutSelect.addEventListener('change', () => {
    updateLayoutPreview();
    saveSettings({ layout: parseInt(layoutSelect.value || '1') });
    maybeRegenerate();
});

orientationSelect.addEventListener('change', () => {
    updateLayoutPreview();
    saveSettings({ orientation: orientationSelect.value });
    maybeRegenerate();
});

arrangeSelect.addEventListener('change', () => {
    updateLayoutPreview();
    saveSettings({ arrangement: arrangeSelect.value });
    maybeRegenerate();
});

scaleMode.addEventListener('change', () => {
    const show = scaleMode.value === 'percent';
    scalePercent.style.display = show ? 'inline-block' : 'none';
    if (scalePercentSymbol) scalePercentSymbol.style.display = show ? 'inline' : 'none';
    saveSettings({ scale_mode: scaleMode.value, scale_percent: parseInt(scalePercent.value || '100') });
    maybeRegenerate();
});

scalePercent.addEventListener('change', () => {
    saveSettings({ scale_percent: parseInt(scalePercent.value || '100') });
    maybeRegenerate();
});
colorModeSelect.addEventListener("change", () => {
    globalColorMode = colorModeSelect.value;
    saveSettings({ color_mode: globalColorMode });
    updateLayoutPreview();
    maybeRegenerate();
});
if (closeExportBtn) {
    closeExportBtn.addEventListener('click', () => {
        if (exportPreviewFrame) {
            exportPreviewFrame.src = '';
            exportPreviewFrame.style.display = 'none';
        }
        if (signedPdfLink) signedPdfLink.style.display = 'none';
        if (downloadPdfBtn) downloadPdfBtn.style.display = 'none';
        if (waShareBtn) waShareBtn.style.display = 'none';
        if (emailShareBtn) emailShareBtn.style.display = 'none';
        if (exportOptions) exportOptions.style.display = 'none';
    });
}
if (blankThresholdInput) {
    blankThresholdInput.addEventListener('change', () => {
        blankThreshold = parseInt(blankThresholdInput.value || '95');
        saveSettings({ blank_threshold: blankThreshold });
    });
}
if (skipBlankCheckbox) {
    skipBlankCheckbox.addEventListener('change', () => {
        skipBlank = skipBlankCheckbox.checked;
        saveSettings({ skip_blank: skipBlank });
    });
}
if (removeBlankBtn) {
    removeBlankBtn.addEventListener('click', removeBlankPages);
}
if (restoreBlankBtn) {
    restoreBlankBtn.addEventListener('click', restoreBlankPages);
}
if (clearImagesBtn) {
    clearImagesBtn.addEventListener('click', () => {
        if (confirm(t('confirmClearImages'))) {
            while (processedImages.length > 0) {
                deleteImage(processedImages.length - 1);
            }
        }
    });
}

brightnessRange.addEventListener('input', () => {
    updateImageFilters();
});

contrastRange.addEventListener('input', () => {
    updateImageFilters();
});

if (signatureScaleInput) {
    signatureScaleInput.addEventListener('input', () => {
        const val = parseFloat(signatureScaleInput.value || '1');
        const pageIdx = parseInt(signaturePage.value || '0');
        if (scaleTarget === 'current') {
            signatureScale = val;
        } else if (scaleTarget === 'all') {
            for (const sig of signatures) {
                if (sig.page === pageIdx) sig.scale = val;
            }
            signatureScale = val;
        } else {
            const idx = parseInt(scaleTarget);
            let count = -1;
            for (const sig of signatures) {
                if (sig.page === pageIdx) {
                    count++;
                    if (count === idx) { sig.scale = val; break; }
                }
            }
        }
        renderSignaturePreview();
    });
}

if (signatureTargetSelect) {
    signatureTargetSelect.addEventListener('change', () => {
        scaleTarget = signatureTargetSelect.value;
        updateSignatureTargetOptions();
        renderSignaturePreview();
    });
}

if (signaturePage) {
    signaturePage.addEventListener('change', () => {
        renderSignaturePreview();
        updateSignatureTargetOptions();
    });
}

function addCurrentSignature() {
    const page = parseInt(signaturePage.value || '0');
    if (!signatureImg) {
        if (!mobileSignPoints[page]) mobileSignPoints[page] = [];
        mobileSignPoints[page].push({ x: signaturePosition.x, y: signaturePosition.y });
    } else {
        signatures.push({ page, x: signaturePosition.x, y: signaturePosition.y, scale: signatureScale });
        const pageSigs = signatures.filter(s => s.page === page);
        scaleTarget = (pageSigs.length - 1).toString();
    }
    const OFFSET = 0.05;
    signaturePosition.x += OFFSET;
    if (signaturePosition.x > 0.95) signaturePosition.x = OFFSET;
    signaturePosition.y += OFFSET;
    if (signaturePosition.y > 0.95) signaturePosition.y = OFFSET;
    renderSignaturePreview();
    updateSignatureTargetOptions();
}

if (addSignatureBtn) {
    addSignatureBtn.addEventListener('click', addCurrentSignature);
}

if (discardSignatureBtn) {
    discardSignatureBtn.addEventListener('click', () => {
        const pageIdx = parseInt(signaturePage.value || '0');
        signatures = signatures.filter(s => s.page !== pageIdx);
        delete mobileSignPoints[pageIdx];
        signatureControls.style.display = 'none';
        signaturePreview.style.display = 'none';
        signatureHint.style.display = 'none';
        if (legalDisclaimerEl) legalDisclaimerEl.style.display = 'none';
        updateSignatureTargetOptions();
    });
}

    if (saveSignatureBtn) {
        saveSignatureBtn.addEventListener('click', () => {
        const pageIdx = parseInt(signaturePage.value || '0');
        let stamps = signatures.filter(s => s.page === pageIdx);
        // also include the currently positioned stamp in case the user
        // did not press Add before saving
        if (signatureImg) {
            stamps = stamps.concat([{ page: pageIdx, x: signaturePosition.x, y: signaturePosition.y, scale: signatureScale }]);
        }
        if (!signatureImg || stamps.length === 0) {
            statusMessageElement.textContent = translations['noSignatures'] || 'No signatures to save';
            return;
        }
        const base = new Image();
        base.onload = async () => {
            const canvas = document.createElement('canvas');
            canvas.width = base.width;
            canvas.height = base.height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(base, 0, 0);
            const baseRatio = (canvas.height / 10) / signatureImg.height;
            const drawOne = sig => {
                const w = signatureImg.width * baseRatio * sig.scale;
                const h = signatureImg.height * baseRatio * sig.scale;
                const x = sig.x * canvas.width - w / 2;
                const y = sig.y * canvas.height - h / 2;
                ctx.drawImage(signatureImg, x, y, w, h);
            };
            stamps.forEach(drawOne);
            const url = canvas.toDataURL('image/png');
            processedImages[pageIdx] = url;
            if (originalImages[pageIdx]) originalImages[pageIdx] = url;
            const container = processedGallery.children[pageIdx];
            if (container) container.querySelector('img').src = url;
            try {
                const blob = await (await fetch(url)).blob();
                processedFiles[pageIdx] = new File([blob], processedFiles[pageIdx]?.name || `image_${pageIdx}.png`, { type: 'image/png' });
            } catch {}
            signatures = signatures.filter(s => s.page !== pageIdx);
            updateSignatureTargetOptions();
            renderSignaturePreview();
            statusMessageElement.textContent = translations['imageSaved'] || 'Image updated';
        };
        base.src = processedImages[pageIdx];
    });
}

async function mergeAllSignatures() {
    if (!signatureImg) return;
    const pages = new Set(signatures.map(s => s.page));
    const current = parseInt(signaturePage.value || '0');
    pages.add(current);
    for (const page of pages) {
        let stamps = signatures.filter(s => s.page === page);
        if (page === current) {
            stamps = stamps.concat([{ page, x: signaturePosition.x, y: signaturePosition.y, scale: signatureScale }]);
        }
        if (stamps.length === 0) continue;
        const base = new Image();
        await new Promise(res => { base.onload = res; base.src = processedImages[page]; });
        const canvas = document.createElement('canvas');
        canvas.width = base.width;
        canvas.height = base.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(base, 0, 0);
        const baseRatio = (canvas.height / 10) / signatureImg.height;
        for (const sig of stamps) {
            const w = signatureImg.width * baseRatio * sig.scale;
            const h = signatureImg.height * baseRatio * sig.scale;
            const x = sig.x * canvas.width - w / 2;
            const y = sig.y * canvas.height - h / 2;
            ctx.drawImage(signatureImg, x, y, w, h);
        }
        const url = canvas.toDataURL('image/png');
        processedImages[page] = url;
        if (originalImages[page]) originalImages[page] = url;
        const container = processedGallery.children[page];
        if (container) container.querySelector('img').src = url;
        try {
            const blob = await (await fetch(url)).blob();
            processedFiles[page] = new File([blob], processedFiles[page]?.name || `image_${page}.png`, { type: 'image/png' });
        } catch {}
    }
    signatures = [];
    signatureImageData = null;
    signatureImg = null;
    renderSignaturePreview();
    updateSignatureTargetOptions();
}

async function applyRemoteSignature(data) {
    const pageIdx = parseInt(data.page || 0);
    const base = new Image();
    await new Promise(res => { base.onload = res; base.src = processedImages[pageIdx]; });
    const canvas = document.createElement('canvas');
    canvas.width = base.width;
    canvas.height = base.height;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(base, 0, 0);
    const list = data.signatures || [{image:data.image, x:data.x, y:data.y, scale:1}];
    for (const sigData of list) {
        const img = new Image();
        await new Promise(res => { img.onload = res; img.src = sigData.image; });
        const baseRatio = (canvas.height / 10) * (sigData.scale || 1) / img.height;
        const w = img.width * baseRatio;
        const h = img.height * baseRatio;
        const x = sigData.x * canvas.width - w / 2;
        const y = sigData.y * canvas.height - h / 2;
        ctx.drawImage(img, x, y, w, h);
    }
    const url = canvas.toDataURL('image/png');
    processedImages[pageIdx] = url;
    if (originalImages[pageIdx]) originalImages[pageIdx] = url;
    const cont = processedGallery.children[pageIdx];
    if (cont) cont.querySelector('img').src = url;
    try {
        const blob = await (await fetch(url)).blob();
        processedFiles[pageIdx] = new File([blob], processedFiles[pageIdx]?.name || `image_${pageIdx}.png`, {type:'image/png'});
    } catch {}
    statusMessageElement.textContent = translations['pageSigned'] || 'Page signed';
}

window.addEventListener('remoteSignature', (e) => applyRemoteSignature(e.detail));
window.addEventListener('mobileSignComplete', () => {
    statusMessageElement.textContent = translations['waitingPdf'] || 'Waiting for signed PDF...';
});
window.addEventListener('signedPdfAvailable', (e) => {
    const url = e.detail.url;
    exportOptions.style.display = 'block';
    if (signedPdfLink) {
        signedPdfLink.href = url;
        signedPdfLink.textContent = translations['downloadPdf'] || 'Download PDF';
        signedPdfLink.style.display = 'inline';
    }
    if (exportPreviewFrame) {
        exportPreviewFrame.src = url + '#toolbar=0&navpanes=0';
        exportPreviewFrame.style.display = 'block';
    }
    if (downloadPdfBtn) downloadPdfBtn.style.display = 'inline-block';
    if (waShareBtn) waShareBtn.style.display = 'inline-block';
    if (emailShareBtn) emailShareBtn.style.display = 'inline-block';
    if (e.detail.hash) {
        window.lastPdfHash = e.detail.hash;
    }
    statusMessageElement.textContent = translations['pdfReady'] || 'PDF ready.';
    if (window.lastSignPhone) shareWhatsAppLink(window.lastSignPhone, url);
    if (window.lastSignEmail) shareEmailLink(window.lastSignEmail, url);
});

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
        let maxDim = 600;
        let w = baseImg.width;
        let h = baseImg.height;
        if (w > h) {
            if (w > maxDim) {
                h = h * (maxDim / w);
                w = maxDim;
            }
        } else {
            if (h > maxDim) {
                w = w * (maxDim / h);
                h = maxDim;
            }
        }
        signaturePreview.width = w;
        signaturePreview.height = h;
        const cw = w;
        const ch = h;
        ctx.clearRect(0, 0, cw, ch);
        ctx.drawImage(baseImg, 0, 0, cw, ch);
        if (mobileSignPoints[pageIdx]) {
            ctx.strokeStyle = '#ff0000';
            ctx.lineWidth = 2;
            for (const pt of mobileSignPoints[pageIdx]) {
                const x = pt.x * cw;
                const y = pt.y * ch;
                ctx.beginPath();
                ctx.moveTo(x - 10, y);
                ctx.lineTo(x + 10, y);
                ctx.moveTo(x, y - 10);
                ctx.lineTo(x, y + 10);
                ctx.stroke();
            }
        }
        if (signatureImg) {
            const drawOne = (sig) => {
                const scale = (ch / 10) * sig.scale / signatureImg.height;
                const sw = signatureImg.width * scale;
                const sh = signatureImg.height * scale;
                const x = sig.x * cw - sw / 2;
                const y = sig.y * ch - sh / 2;
                ctx.drawImage(signatureImg, x, y, sw, sh);
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
    console.debug('autoDetectCorners triggered');
    statusMessageElement.textContent = translations['detectingEdges'] || 'Detecting edges...';
    const formData = new FormData();
    formData.append('image_file', currentFile);
    fetch('/detect-corners/', { method: 'POST', body: formData })
        .then(resp => {
            if (!resp.ok) {
                if (resp.status === 413) {
                    statusMessageElement.textContent = t('fileTooLarge').replace('{mb}', MAX_FILE_MB);
                }
            }
            return resp.json();
        })
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

function updateSignatureTargetOptions() {
    if (!signatureTargetSelect) return;
    const pageIdx = parseInt(signaturePage.value || '0');
    signatureTargetSelect.innerHTML = '';
    const optCurr = document.createElement('option');
    optCurr.value = 'current';
    optCurr.textContent = translations['currentSig'] || 'Current';
    signatureTargetSelect.appendChild(optCurr);
    const pageSigs = signatures.filter(s => s.page === pageIdx);
    pageSigs.forEach((s, i) => {
        const opt = document.createElement('option');
        opt.value = i.toString();
        const label = (translations['sigLabel'] || 'Signature {n}').replace('{n}', i + 1);
        opt.textContent = label;
        signatureTargetSelect.appendChild(opt);
    });
    if (pageSigs.length > 1) {
        const optAll = document.createElement('option');
        optAll.value = 'all';
        optAll.textContent = translations['allSigs'] || 'All';
        signatureTargetSelect.appendChild(optAll);
    }
    signatureTargetSelect.value = scaleTarget;
    if (signatureTargetSelect.value !== scaleTarget) {
        scaleTarget = signatureTargetSelect.value;
    }
    if (signatureScaleInput) {
        if (scaleTarget === 'current') {
            signatureScaleInput.value = signatureScale;
        } else if (scaleTarget === 'all') {
            if (pageSigs[0]) signatureScaleInput.value = pageSigs[0].scale;
        } else {
            const idx = parseInt(scaleTarget);
            if (pageSigs[idx]) signatureScaleInput.value = pageSigs[idx].scale;
        }
    }
}

function applyProStatus() {
    // In demo mode features remain usable but PDF pages beyond the first
    // will include a DEMO watermark. We simply update the button style
    // to reflect the license status without disabling functionality.
    if (!isLicensed || currentLicenseLevel === 'free') {
        exportPdfBtn.classList.remove('pro-disabled');
        imageUploadElement.multiple = true;
        imageUploadElement.accept = 'image/*';
        document.querySelectorAll('.shareBtn').forEach(btn => btn.style.display = 'none');
        if (sortable) { sortable.destroy(); sortable = null; }
        if (reorderHint) reorderHint.style.display = 'none';
        if (colorModeSelect) colorModeSelect.style.display = 'none';
        if (colorModeLabel) colorModeLabel.style.display = 'none';
        if (blankThresholdInput) blankThresholdInput.style.display = 'none';
        if (blankThresholdLabel) blankThresholdLabel.style.display = 'none';
        if (skipBlankCheckbox) skipBlankCheckbox.style.display = 'none';
    } else {
        exportPdfBtn.classList.remove('pro-disabled');
        imageUploadElement.multiple = true;
        imageUploadElement.accept = 'image/*,application/pdf';
        document.querySelectorAll('.shareBtn').forEach(btn => btn.style.display = 'inline-block');
        if (!sortable && typeof Sortable !== 'undefined') {
            sortable = Sortable.create(processedGallery, {
                animation: 150,
                onEnd: updateProcessedArrays,
                handle: 'img',
                filter: '.thumbMenu, .thumbBtn',
                preventOnFilter: false
            });
        }
        if (reorderHint) reorderHint.style.display = 'block';
        if (colorModeSelect) colorModeSelect.style.display = 'inline-block';
        if (colorModeLabel) colorModeLabel.style.display = 'inline-block';
        if (blankThresholdInput) blankThresholdInput.style.display = 'inline-block';
        if (blankThresholdLabel) blankThresholdLabel.style.display = 'inline-block';
        if (skipBlankCheckbox) skipBlankCheckbox.style.display = 'inline-block';
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
            html += `<li><a href="#" id="donatePaypalLink">${t('donatePaypal')}</a></li>`;
            hasItem = true;
        }
    } else if (mode === 'subscription') {
        if (cfg.paypal_link) {
            html += `<li><a href="#" id="payPaypalLink">${t('payPaypal')}</a></li>`;
            hasItem = true;
        }
        if (cfg.stripe_price_pro) {
            html += `<li><button id="stripeProBtn">${t('payStripe')} - ${t('proEdition')}</button></li>`;
            hasItem = true;
        }
        if (cfg.stripe_price_full) {
            html += `<li><button id="stripeFullBtn">${t('payStripe')} - ${t('fullEdition')}</button></li>`;
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
    const donateLink = document.getElementById('donatePaypalLink');
    if (donateLink) {
        donateLink.addEventListener('click', (e) => {
            e.preventDefault();
            openDonationModal(cfg.paypal_link);
        });
    }
    const payPaypalLink = document.getElementById('payPaypalLink');
    if (payPaypalLink) {
        payPaypalLink.addEventListener('click', (e) => {
            e.preventDefault();
            openDonationModal(cfg.paypal_link);
        });
    }
    const proBtn = document.getElementById('stripeProBtn');
    if (proBtn) {
        proBtn.addEventListener('click', async () => {
            const res = await fetch('/stripe-checkout/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({level: 'pro'})
            });
            if (res.ok) {
                const data = await res.json();
                if (data.session_url) {
                    window.location.href = data.session_url;
                }
            } else {
                alert('Stripe checkout failed');
            }
        });
    }
    const fullBtn = document.getElementById('stripeFullBtn');
    if (fullBtn) {
        fullBtn.addEventListener('click', async () => {
            const res = await fetch('/stripe-checkout/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({level: 'full'})
            });
            if (res.ok) {
                const data = await res.json();
                if (data.session_url) {
                    window.location.href = data.session_url;
                }
            } else {
                alert('Stripe checkout failed');
            }
        });
    }
}

function renderLicenseBox() {
    let html = `
    <h3>${t('licenseOptions')}</h3>
    <ul>
        <li><strong>${t('freeEdition')}</strong> - ${t('freeFeatures')}</li>
        <li><strong>${t('proEdition')}</strong> - ${t('proFeatures')}</li>
        <li><strong>${t('fullEdition')}</strong> - ${t('fullFeatures')}</li>
    </ul>`;
    if (demoFullMode) {
        html += `
    <p>${t('demoLicenseDisabled')}</p>
    <p><strong>${t('licenseKey')}</strong> ${currentSettings.license_key || ''}</p>
    <p><strong>${t('licenseName')}</strong> ${currentSettings.license_name || ''}</p>`;
    } else {
        html += `
    <div class="licenseForm">
        <label>${t('licenseKey')}</label>
        <input type="text" id="licenseKeyInput" value="${currentSettings.license_key || ''}"><br>
        <label>${t('licenseName')}</label>
        <input type="text" id="licenseNameInput" value="${currentSettings.license_name || ''}"><br>
        <button id="saveLicenseBtn">${t('saveLicense')}</button>
    </div>`;
    }
    licenseBox.innerHTML = html;
    licenseBox.style.display = 'block';
    if (!demoFullMode) {
        const btn = document.getElementById('saveLicenseBtn');
        btn.addEventListener('click', async () => {
            const key = document.getElementById('licenseKeyInput').value.trim();
            const name = document.getElementById('licenseNameInput').value.trim();
            await saveSettings({license_key: key, license_name: name});
            await fetch('/restart/', {method: 'POST'});
            alert(t('licenseSaved'));
            licenseBox.classList.remove('visible');
            setTimeout(() => { location.reload(); }, 1000);
        });
    }
}

function renderSettingsBox() {
    const level = currentSettings.license_level || 'free';
    const html = `
    <div class="settingsForm">
        <label>${t('licenseType')}</label>
        <select id="licenseLevelSelect">
            <option value="free" ${level==='free'?'selected':''}>${t('freeEdition')}</option>
            <option value="pro" ${level==='pro'?'selected':''}>${t('proEdition')}</option>
            <option value="full" ${level==='full'?'selected':''}>${t('fullEdition')}</option>
        </select>
        <div id="googleSettings" style="${level==='pro'||level==='full'?'':'display:none;'}">
            <label>${t('googleClientId')}</label>
            <input type="text" id="googleClientIdInput" value="${currentSettings.google_client_id || ''}">
        </div>
        <div id="docusealSettings" style="${level==='full'?'':'display:none;'}">
            <label>${t('docusealUrl')}</label>
            <input type="text" id="docusealUrlInput" value="${currentSettings.docuseal_api_url || ''}">
            <label>${t('docusealKey')}</label>
            <input type="text" id="docusealKeyInput" value="${currentSettings.docuseal_api_key || ''}">
        </div>
        <div>
            <label>${t('publicUrl')}</label>
            <input type="text" id="publicUrlInput" value="${currentSettings.public_url || ''}">
        </div>
        <button id="saveSettingsBtn">${t('saveSettings')}</button>
    </div>`;
    settingsBox.innerHTML = html;
    settingsBox.style.display = 'block';
    const levelSelect = document.getElementById('licenseLevelSelect');
    const googleDiv = document.getElementById('googleSettings');
    const docusealDiv = document.getElementById('docusealSettings');
    levelSelect.addEventListener('change', () => {
        const val = levelSelect.value;
        googleDiv.style.display = (val === 'pro' || val === 'full') ? 'block' : 'none';
        docusealDiv.style.display = val === 'full' ? 'block' : 'none';
    });
    document.getElementById('saveSettingsBtn').addEventListener('click', async () => {
        const lvl = levelSelect.value;
        const update = { license_level: lvl };
        if (lvl === 'pro' || lvl === 'full') {
            update.google_client_id = document.getElementById('googleClientIdInput').value.trim();
        } else {
            update.google_client_id = '';
        }
        if (lvl === 'full') {
            update.docuseal_api_url = document.getElementById('docusealUrlInput').value.trim();
            update.docuseal_api_key = document.getElementById('docusealKeyInput').value.trim();
        } else {
            update.docuseal_api_url = '';
            update.docuseal_api_key = '';
        }
        update.public_url = document.getElementById('publicUrlInput').value.trim();
        await saveSettings(update);
        const cfg = await loadSettings();
        applySettings(cfg);
        alert(t('settingsSaved'));
        settingsBox.classList.remove('visible');
    });
}

function renderLogin(cfg) {
    if (demoFullMode) {
        loginArea.style.display = 'none';
        return;
    }
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
    initSignaturePlugin(translations, mobileSignEnabled);
    initRemoveBgPlugin(translations, removeBgEnabled);
    initPdfCompressPlugin(translations, compressEnabled);
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
