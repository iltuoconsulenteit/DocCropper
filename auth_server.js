const express = require('express');
const session = require('express-session');
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const path = require('path');
require('dotenv').config();
const jwt = require('jsonwebtoken');
const rateLimit = require('express-rate-limit');

const app = express();

app.use(express.json());
app.set('trust proxy', 1);

const LICENSE_SECRET = process.env.LICENSE_SECRET || 'change-me';
const ALLOWED_DOMAINS = (process.env.ALLOWED_DOMAINS || '')
  .split(',')
  .map(d => d.trim())
  .filter(Boolean);

function requireHttps(req, res, next) {
  if (req.secure || req.headers['x-forwarded-proto'] === 'https') {
    return next();
  }
  res.status(400).json({ error: 'HTTPS required' });
}

function checkDomain(req, res, next) {
  if (!ALLOWED_DOMAINS.length) return next();
  const origin = req.get('origin') || req.hostname;
  const host = origin.replace(/^https?:\/\//, '').split(':')[0];
  if (ALLOWED_DOMAINS.includes(host)) return next();
  res.status(403).json({ error: 'Domain not allowed' });
}

const verifyLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 5,
  standardHeaders: true,
  legacyHeaders: false,
  skipSuccessfulRequests: true,
  handler: (req, res) => {
    console.warn(`Rate limit exceeded for IP ${req.ip}`);
    res.status(429).json({ error: 'Too many verification attempts' });
  }
});

app.use(session({
  secret: 'doccropper-secret',
  resave: false,
  saveUninitialized: false
}));

app.use(passport.initialize());
app.use(passport.session());

passport.use(new GoogleStrategy({
  clientID: process.env.CLIENT_ID,
  clientSecret: process.env.CLIENT_SECRET,
  callbackURL: process.env.REDIRECT_URI || 'http://localhost:8765/auth/google/callback'
}, (accessToken, refreshToken, profile, done) => {
  return done(null, profile);
}));

passport.serializeUser((user, done) => done(null, user));
passport.deserializeUser((obj, done) => done(null, obj));

app.get('/auth/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

app.get('/auth/google/callback', passport.authenticate('google', {
  failureRedirect: '/'
}), (req, res) => {
  res.redirect('/dashboard');
});

app.get('/dashboard', (req, res) => {
  if (!req.isAuthenticated()) {
    return res.redirect('/');
  }
  const user = req.user;
  const name = user.displayName;
  const email = user.emails && user.emails[0] ? user.emails[0].value : '';
  res.send(`<h1>Dashboard</h1><p>Name: ${name}</p><p>Email: ${email}</p><a href="/logout">Logout</a>`);
});

app.get('/logout', (req, res, next) => {
  req.logout(err => {
    if (err) { return next(err); }
    req.session.destroy(() => {
      res.redirect('/');
    });
  });
});

app.post('/license/token', requireHttps, checkDomain, (req, res) => {
  const { license_type, expires_at, plugins, allowed_domains } = req.body;
  const payload = { license_type, expires_at, plugins };
  if (Array.isArray(allowed_domains) && allowed_domains.length) {
    payload.allowed_domains = allowed_domains;
  }
  const token = jwt.sign(payload, LICENSE_SECRET);
  res.json({ token });
});

app.post('/license/verify', requireHttps, checkDomain, verifyLimiter, (req, res) => {
  const { token, domain } = req.body;
  try {
    const payload = jwt.verify(token, LICENSE_SECRET);
    const now = Math.floor(Date.now() / 1000);
    if (payload.expires_at && payload.expires_at < now) {
      return res.status(401).json({ valid: false, expired: true, payload });
    }
    if (
      domain &&
      Array.isArray(payload.allowed_domains) &&
      payload.allowed_domains.length &&
      !payload.allowed_domains.includes(domain)
    ) {
      return res.status(403).json({ valid: false, error: 'domain not allowed', payload });
    }
    res.json({ valid: true, payload });
  } catch (err) {
    console.warn(`Token verification failed for ${req.ip}: ${err.message}`);
    if (err.name === 'TokenExpiredError') {
      const payload = jwt.verify(token, LICENSE_SECRET, { ignoreExpiration: true });
      return res.status(401).json({ valid: false, expired: true, payload });
    }
    res.status(401).json({ valid: false, error: 'invalid token' });
  }
});

app.use(express.static(path.join(__dirname, 'static')));

const PORT = process.env.PORT || 8765;
app.listen(PORT, () => {
  console.log(`Auth server running on http://localhost:${PORT}`);
});
