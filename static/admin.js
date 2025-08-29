async function loadSettings() {
    const res = await fetch('/settings/');
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
    await fetch('/settings/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    alert('Settings saved');
}

async function loadUsers() {
    const res = await fetch('/users/');
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
        await fetch('/users/' + btn.dataset.id, {method: 'DELETE'});
        loadUsers();
    }));
}

async function createUser(event) {
    event.preventDefault();
    const email = document.getElementById('userEmail').value;
    const password = document.getElementById('userPassword').value;
    const license = document.getElementById('userLicense').value;
    const res = await fetch('/auth/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password})
    });
    if (res.ok) {
        const data = await res.json();
        await fetch('/users/' + data.id, {
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
