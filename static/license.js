const API_BASE = window.DC_API_BASE || '/api';
const ABSOLUTE_URL_RE = /^[a-zA-Z][a-zA-Z0-9+.-]*:/;
const SKIP_PREFIXES = [
  '/static/',
  '/wiki/',
  '/index.php',
  '/admin/',
  '/docs',
  '/openapi',
];

function normalizeApiPath(path) {
  if (typeof path !== 'string' || !path) {
    return path;
  }
  if (ABSOLUTE_URL_RE.test(path)) {
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

function createApiFetch() {
  const hasRequest = typeof Request !== 'undefined';
  return (resource, init) => {
    if (typeof resource === 'string') {
      return fetch(normalizeApiPath(resource), init);
    }
    if (hasRequest && resource instanceof Request) {
      const url = normalizeApiPath(resource.url);
      if (url === resource.url) {
        return fetch(resource, init);
      }
      const cloned = new Request(url, resource);
      return fetch(cloned, init);
    }
    return fetch(resource, init);
  };
}

const apiFetch = (window.DC_API_HELPER && typeof window.DC_API_HELPER.apiFetch === 'function')
  ? window.DC_API_HELPER.apiFetch
  : createApiFetch();

export async function verifyTokenLocally(token, secret) {
  try {
    const [headerB64, payloadB64, signatureB64] = token.split('.');
    if (!signatureB64) {
      return { valid: false, reason: 'format' };
    }
    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
      'raw',
      encoder.encode(secret),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['sign']
    );
    const data = encoder.encode(`${headerB64}.${payloadB64}`);
    const signature = await crypto.subtle.sign('HMAC', key, data);
    const expected = btoa(String.fromCharCode(...new Uint8Array(signature)))
      .replace(/=/g, '')
      .replace(/\+/g, '-')
      .replace(/\//g, '_');
    if (expected !== signatureB64) {
      return { valid: false, reason: 'signature' };
    }
    const payload = JSON.parse(atob(payloadB64));
    const now = Math.floor(Date.now() / 1000);
    if (payload.expires_at && payload.expires_at < now) {
      return { valid: false, expired: true, payload };
    }
    return { valid: true, payload };
  } catch (e) {
    return { valid: false, reason: 'error' };
  }
}

export async function verifyTokenRemotely(token) {
  const resp = await apiFetch('/license/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, domain: location.hostname })
  });
  return resp.json();
}

export async function validateLicenseToken(token, secret) {
  const local = await verifyTokenLocally(token, secret);
  if (local.valid) return local;
  if (local.expired) {
    try {
      return await verifyTokenRemotely(token);
    } catch (e) {
      return { valid: false, reason: 'network' };
    }
  }
  return local;
}
