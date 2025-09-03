export function initCloudSavePlugin(translations, enabled = true) {
    if (!enabled) {
        return;
    }

    const exportOptions = document.getElementById('exportOptions');
    if (!exportOptions) return;

    function makeBtn(id, text, handler, extraClasses = '') {
        const btn = document.createElement('button');
        btn.id = id;
        btn.textContent = text;
        btn.className = 'w-full px-2 py-1 rounded text-sm text-white ' + extraClasses;
        btn.addEventListener('click', handler);
        return btn;
    }

    const localBtn = makeBtn(
        'localSaveBtn',
        translations.localSave || 'Save locally',
        () => {
            alert(translations.localSaveComingSoon || 'Local saving coming soon');
        },
        'bg-gray-500'
    );

    const cloudBtn = makeBtn(
        'cloudSaveBtn',
        translations.cloudSave || 'Save to cloud',
        () => {
            alert(translations.cloudSaveComingSoon || 'Cloud saving coming soon');
        },
        'bg-purple-500 mt-2'
    );

    exportOptions.appendChild(localBtn);
    exportOptions.appendChild(cloudBtn);
}
