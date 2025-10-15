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

function normalizePath(path) {
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

function apiUrl(path) {
  return normalizePath(path);
}

function apiFetch(resource, init) {
  if (typeof resource === 'string') {
    return fetch(apiUrl(resource), init);
  }
  if (resource instanceof Request) {
    const url = apiUrl(resource.url);
    if (url === resource.url) {
      return fetch(resource, init);
    }
    const cloned = new Request(url, resource);
    return fetch(cloned, init);
  }
  return fetch(resource, init);
}

const helper = { apiFetch, apiUrl, API_BASE };

if (typeof window !== 'undefined') {
  window.DC_API_HELPER = helper;
}

export { apiFetch, apiUrl, API_BASE };
