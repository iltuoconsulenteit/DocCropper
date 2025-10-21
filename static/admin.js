const helper = window.DC_API_HELPER || null;
const API_BASE = (window.DC_API_BASE || '/api');
const ABSOLUTE_RE = /^[a-zA-Z][a-zA-Z0-9+.-]*:/;
const SKIP_PREFIXES = ['/static/', '/wiki/', '/index.php', '/admin/', '/docs', '/openapi'];

function normalizeApiPath(path) {
    if (typeof path !== 'string' || !path) {
        return path;
    }
    if (ABSOLUTE_RE.test(path)) {
        return path;
    }
    if (path.startsWith(API_BASE)) {
        return path;
    }
    for (const prefix of SKIP_PREFIXES) {
        if (path.startsWith(prefix)) {
            return path;
        }
    }
    if (!path.startsWith('/')) {
        path = `/${path}`;
    }
    return `${API_BASE}${path}`;
}

const apiFetch = helper && typeof helper.apiFetch === 'function'
    ? helper.apiFetch
    : (resource, init) => {
        if (typeof resource === 'string') {
            return fetch(normalizeApiPath(resource), init);
        }
        return fetch(resource, init);
    };

async function loadSettings() {
    const res = await apiFetch('/settings/');
    if (!res.ok) return;
    const data = await res.json();
    document.getElementById('licenseSelect').value = data.license_level || 'free';
    document.getElementById('brandHtml').value = data.brand_html || '';
}

async function saveSettings(event) {
    event.preventDefault();
    const payload = {
        license_level: document.getElementById('licenseSelect').value,
        brand_html: document.getElementById('brandHtml').value
    };
    await apiFetch('/settings/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    alert('Settings saved');
}

async function loadUsers() {
    const res = await apiFetch('/users/');
    if (!res.ok) return;
    const list = await res.json();
    const tbody = document.querySelector('#userTable tbody');
    tbody.innerHTML = '';
    list.forEach(u => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${u.email}</td><td>${u.license_type}</td>` +
            `<td><button data-id="${u.id}">Delete</button></td>`;
        tbody.appendChild(tr);
    });
    tbody.querySelectorAll('button').forEach(btn => btn.addEventListener('click', async () => {
        await apiFetch('/users/' + btn.dataset.id, {method: 'DELETE'});
        loadUsers();
    }));
}

async function createUser(event) {
    event.preventDefault();
    const email = document.getElementById('userEmail').value;
    const password = document.getElementById('userPassword').value;
    const license = document.getElementById('userLicense').value;
    const res = await apiFetch('/auth/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password})
    });
    if (res.ok) {
        const data = await res.json();
        await apiFetch('/users/' + data.id, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({license_type: license})
        });
        loadUsers();
        document.getElementById('createUserForm').reset();
    } else {
        alert('User creation failed');
    }
}

document.getElementById('settingsForm').addEventListener('submit', saveSettings);
document.getElementById('createUserForm').addEventListener('submit', createUser);

loadSettings();
loadUsers();
