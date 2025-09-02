export function initFormFieldsPlugin(translations, enabled = true) {
    if (!enabled) {
        window.addFormField = () => {};
        return;
    }

    const fields = {};

    function addFormField(page, type = 'text') {
        const container = document.querySelector(`.thumbContainer[data-index="${page}"]`);
        if (!container) return;
        container.style.position = 'relative';
        const overlay = document.createElement('div');
        overlay.className = 'formFieldOverlay';
        Object.assign(overlay.style, {
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            cursor: 'crosshair',
            zIndex: 5
        });
        container.appendChild(overlay);
        let startX, startY, box;

        function start(e) {
            e.preventDefault();
            const rect = overlay.getBoundingClientRect();
            startX = e.clientX - rect.left;
            startY = e.clientY - rect.top;
            box = document.createElement('div');
            box.className = 'formFieldBox';
            Object.assign(box.style, {
                position: 'absolute',
                border: '1px dashed #2563eb',
                left: startX + 'px',
                top: startY + 'px'
            });
            overlay.appendChild(box);
            overlay.addEventListener('mousemove', move);
            window.addEventListener('mouseup', end);
        }

        function move(e) {
            const rect = overlay.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const w = x - startX;
            const h = y - startY;
            box.style.width = Math.abs(w) + 'px';
            box.style.height = Math.abs(h) + 'px';
            box.style.left = (w < 0 ? x : startX) + 'px';
            box.style.top = (h < 0 ? y : startY) + 'px';
        }

        function end() {
            overlay.removeEventListener('mousedown', start);
            overlay.removeEventListener('mousemove', move);
            window.removeEventListener('mouseup', end);
            const rect = box.getBoundingClientRect();
            const contRect = container.getBoundingClientRect();
            const x = (rect.left - contRect.left) / contRect.width;
            const y = (rect.top - contRect.top) / contRect.height;
            const w = rect.width / contRect.width;
            const h = rect.height / contRect.height;
            overlay.remove();
            box.remove();
            let field;
            if (type === 'checkbox') {
                field = document.createElement('input');
                field.type = 'checkbox';
            } else if (type === 'select') {
                field = document.createElement('select');
                field.innerHTML = '<option></option>';
            } else {
                field = document.createElement('textarea');
            }
            field.className = 'formField';
            field.title = translations.fieldRemove || 'Double-click to remove';
            field.addEventListener('dblclick', () => field.remove());
            Object.assign(field.style, {
                position: 'absolute',
                left: (x * 100) + '%',
                top: (y * 100) + '%',
                width: (w * 100) + '%',
                height: (h * 100) + '%'
            });
            container.appendChild(field);
            fields[page] = fields[page] || [];
            fields[page].push({ type, x, y, w, h });
        }

        overlay.addEventListener('mousedown', start, { once: true });
    }

    window.addFormField = addFormField;
}
