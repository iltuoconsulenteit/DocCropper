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
  const resp = await fetch('/license/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token })
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
