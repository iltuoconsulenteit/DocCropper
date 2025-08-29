const express = require('express');
const session = require('express-session');
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const path = require('path');
require('dotenv').config();

const app = express();

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

app.use(express.static(path.join(__dirname, 'static')));

const PORT = process.env.PORT || 8765;
app.listen(PORT, () => {
  console.log(`Auth server running on http://localhost:${PORT}`);
});
