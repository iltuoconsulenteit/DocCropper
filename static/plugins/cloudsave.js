export function initCloudSavePlugin(translations, enabled = true) {
    if (!enabled) {
        return;
    }

    const cloudBtn = document.getElementById('cloudSaveBtn');

    if (cloudBtn) {
        cloudBtn.addEventListener('click', () => {
            alert(translations.cloudSaveComingSoon || 'Cloud saving coming soon');
        });
    }
}
