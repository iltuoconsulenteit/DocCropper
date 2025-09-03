export function initCloudSavePlugin(translations, enabled = true) {
    if (!enabled) {
        return;
    }

    const localBtn = document.getElementById('localSaveBtn');
    const cloudBtn = document.getElementById('cloudSaveBtn');

    if (localBtn) {
        localBtn.addEventListener('click', () => {
            alert(translations.localSaveComingSoon || 'Local saving coming soon');
        });
    }

    if (cloudBtn) {
        cloudBtn.addEventListener('click', () => {
            alert(translations.cloudSaveComingSoon || 'Cloud saving coming soon');
        });
    }
}
