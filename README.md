# 📄 DocCropper

**DocCropper** is a web-based app for batch document perspective correction, multi-image cropping, mobile signing, and PDF export.

This project is **inspired by [image-perspective-crop](https://github.com/varna9000/image-perspective-crop)**, but has been **significantly rewritten and extended**, with major architectural changes, a redesigned user interface, batch features, user preferences, and many additional capabilities.

All project changes are documented in [UPDATES.md](UPDATES.md). Run `python scripts/generate_updates.py` to rebuild this file from the Git commit history so dates stay in sync with actual commits. The in-app **Updates** menu loads this file so users can review past changes, and the most recent entry appears on the home screen when no documents are loaded.

Configuration variables, environment files, and the `settings.json` options are detailed in [CONFIGURATION.md](CONFIGURATION.md).

---

## ✨ Key Features

- ✅ Multi-image upload and batch processing (configurable limit, 10 by default)
- 📥 Import PDF files and place each page directly in the gallery for later editing (Pro)
- 🔄 Automatic or manual perspective correction
- 🖼️ Interactive cropping and preview
- 🖱️ Double click or tap to auto-detect page edges
- 🎚️ Adjust brightness and contrast with live preview
- 🖌️ Convert images to grayscale or black & white to reduce PDF size (Pro)
- 🎨 Restore color later with a dedicated button
- 🪄 Remove backgrounds with an adjustable threshold and restore originals when needed (Pro)
- 🔁 Flip pages horizontally or invert upside-down scans
- 🖍️ Add text or image watermarks with custom size, angle, color, font and optional propagation to all pages
- 🎨 Experimental image editor with saturation and sharpness controls (Developer)
- 🧹 Skip blank pages when importing PDFs using a configurable threshold (Pro)
- 📄 Create PDFs ready for download or sharing
- 📦 Compress PDFs with Low, Medium or Extreme settings and optional JPEG quality tuning (Pro)
- 📚 Export as PDF/A for archival and legal compliance, selecting versions 1–4
- 🔏 Optional digital signature on exported PDFs. Drag and add multiple stamps per page before export (Free - watermark applied)
- ✍️ Sign from your phone via QR code and save the drawing for later use (Pro)
- 📤 Share PDFs via WhatsApp Web or Email, attaching files via the Web Share API when possible (Pro)
- 🗂️ Drag thumbnails to reorder images before exporting (Pro)
- 🔘 Select individual thumbnails for partial PDF export, automatically selecting all when none are chosen (Pro)
- 🖼️ Closable banner can rotate multiple promotional images
- 🤝 Sponsor page shows Bronze, Silver, and Gold cards with medal icons and a benefits table covering marketing exposure and included licenses
- 📝 Extract text via OCR (future Pro feature)
- 🗂️ Persistent user settings
- 🧭 Touchscreen-friendly interface
- 🎨 Material design look with Roboto fonts and raised buttons
- 🌐 Works offline or over LAN (internet required only for license activation/renewal and to display sponsored frames)
- 👤 Multi-user environment support (optional)
- 🔒 Uploaded files are encrypted and wiped after your session
- 📏 Uploads larger than 5&nbsp;MB are rejected (adjust with `max_upload_mb` or `DOCROPPER_MAX_UPLOAD_MB`)
- 📁 Limit simultaneous uploads with the `max_upload_files` setting (10 by default)
- 🚀 Cache busting (`?v=<commit>`) ensures browsers fetch updated files
- 🔔 Notification bell checks for updates and lets licensed users trigger upgrades with a PIN
- ⏪ Rollback command restores the previous version if an update causes issues
- ⬇️ Optional plugin adds a per-thumbnail PNG download button

---

## 🔧 Frontend

This project uses [Interact.JS](https://github.com/taye/interact.js) for managing draggable corner points.

The frontend allows the user to:
 - Upload images with the file picker. On mobile devices the file picker opens the camera or gallery; after each capture the app returns to the gallery where you can tap **+** (Add/Import) to add another photo. Desktop users may also drag and drop files. Up to `max_upload_files` images can be imported at once (10 by default)
 - Import PDF documents which are converted to images and added to the gallery without immediate cropping (Pro)
- Add more images later without losing previously processed ones
- Manually adjust the four corners of each image
- Double click/tap an image to auto-detect its edges
- Flip or invert images if they were scanned mirrored or upside-down
- Remove backgrounds with a dedicated button and fine‑tune the threshold via the settings panel
- Overlay watermarks using text or images, choosing size, angle, color and font, and optionally apply to all pages
- Submit data (image, coordinates, size) to the backend
- Export all processed images to PDF
- Choose a PDF compression level (Low, Medium, Extreme) and customize JPEG quality when needed
- Choose how many processed images appear on each PDF page
- Select portrait or landscape orientation for the PDF
- Choose whether images are arranged horizontally, vertically or in a grid and preview the layout only when needed
- Control how images are scaled on each page: fill the cell, keep original size or apply a custom percentage
- A small margin is applied around each image so nothing touches the page edges
- Change the interface language (Italian translation included)
- The layout is responsive so DocCropper works well on smartphones and tablets
- Mobile view keeps the Help and Purchase buttons on one line and centers the
  footer branding

JavaScript logic is contained in `static/app.js`.

**Data sent to backend:**
- `original_height`, `original_width`: dimensions of the image
- `points`: coordinates of the 4 corners (TL, TR, BR, BL)
- `image_file`: the uploaded file

Images are processed and displayed as thumbnails with **Rotate**, **Edit**, and **Delete** buttons. Preview and layout configuration options are also provided before export.

Logos and branding can be customized via `static/logos/`, `static/slide/`, `settings.json`, and `brand_html`. A dedicated area in the header can show a client logo (`client_logo`), a rotating slogan banner and an optional sponsor logo (`sponsor_logo`). Logo height and spacing can be tuned with `brand_height` and `brand_gap`. The `sponsor_scale` and `sponsor_bottom` settings control the video banner size and position. Client and sponsor logos can link to external sites through `client_url` and `sponsor_url`, and a plugin-driven sponsor slot can display a `sponsor_banner` image, a rotating `sponsor_slides` carousel, or an embedded `sponsor_frame` depending on the `sponsor_plugin` mode. Supported modes include `facebook`, `instagram`, `landing` (generic URL), `banner`/`image`, and `slide`; leaving `sponsor_plugin` blank disables sponsor content. When a frame is configured it renders as a thumbnail-like preview that shifts to the end of the gallery as files are added and is skipped during export. Frame dimensions and preview size can be customized with `sponsor_frame_width`, `sponsor_frame_height`, `sponsor_thumb_width`, and `sponsor_thumb_height`. Demo and developer builds automatically embed the latest post from <a href="https://www.facebook.com/iltuoconsulenteit">iltuoconsulenteit</a>, while other installations can supply a custom URL or other plugin type. The header also shows a language-specific slogan image stored in `static/slide/` following the naming pattern `DocCropper_slogan_[plugin]_[lang].png` (e.g. `static/slide/DocCropper_slogan_main_en.png`), and the footer displays the current Git commit hash. Licensed users can also convert images to grayscale or black & white using buttons below each thumbnail, and a global color mode option applies to all images before PDF export.
The images used for the rotating banner are defined in the `banner_images` setting. Each entry may include the `{{lang}}` placeholder to load the appropriate language version. Multiple images cycle automatically every `banner_interval` milliseconds.
Blank pages can be skipped during PDF import. Enable **Skip blank pages** in the layout controls and adjust the `blank_threshold` percentage (95% by default).
Pages over this threshold are discarded in the Pro edition.

User preferences are stored in the `users/` folder based on their email address. Anonymous users fallback to global settings in `settings.json`. The system supports optional Google sign-in and a configurable purchase panel (donation or subscription) opened from the **Purchase** button next to the Help button. Payment links can be supplied via `settings.json` or through Stripe credentials in `env/stripe.env.example`. Donation links open in a new browser tab for compatibility with PayPal. Developer keys allow full access when the configured `license_key` matches the value of the `DOCROPPER_DEV_LICENSE` environment variable.

---

## 🐍 Backend

Built with **FastAPI + Uvicorn**, the backend:
- Applies a perspective transformation and cropping
- Optionally sharpens the image
- Compiles all processed images into a PDF with layout control
- Handles per-session temporary folders
- Uploaded files are encrypted on disk and sessions are automatically removed after a short time

---

## 🚀 Setup Instructions

### 🧱 Create virtual environment

```bash
cd doccropper
python -m venv venv
venv\Scripts\activate        # On Windows
# OR
source venv/bin/activate     # On Linux/macOS

pip install --upgrade pip
pip install -r requirements.txt  # includes aiosqlite for the SQLite backend
```

### 🛠 Developer setup

Clone this repository and install the Python dependencies inside the virtual environment. Example:

```bash
git clone https://github.com/yourname/DocCropper.git
cd DocCropper
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install --upgrade pip
pip install -r requirements.txt
```

Copy the sample environment files under `env/` and adjust any settings you need.
Authentication variables live in `env/auth.env.example` while license-related
settings are in `env/license.env.example`.
Optional templates are provided for Google sign-in (`env/google.env.example`), Stripe payments (`env/stripe.env.example`), local and command-based signing (`env/signing.env.example`) and Docuseal signing (`env/docuseal.env.example`).
When a license is validated remotely, DocCropper writes forced configuration values to `license_overrides.json`.
These settings override the normal `settings.json` values and should not be edited manually.

The developer settings are protected by `DOCROPPER_DEV_PASSWORD`, which defaults to `87654321`. Change it immediately by POSTing to `/developer-password/` with a JSON body such as:

```
{"old":"87654321","new":"your-strong-password"}
```

Once changed, authenticate with `/developer-login/` by sending `{ "password": "your-strong-password" }`. Logging in while the default password is active returns an error until the password is replaced.

The general settings panel is similarly secured with `DOCROPPER_SETTINGS_PASSWORD` (default `12345678`). Change it via `/settings-password/` and unlock with `/settings-login/` before editing settings.
In developer installations a Settings button in the header opens this panel and requests the default password.

### Required environment variables

Create a `.env` file (or multiple `.env` files inside the `env/` directory)
with at least the authentication variables and your license check URL:

```bash
SECRET_KEY=change-me
DATABASE_URL=sqlite+aiosqlite:///./db.sqlite3
LICENSE_CHECK_URL=https://tuodominio.it/index.php?option=com_fabrik&view=list&listid=XXX&format=raw
DOCROPPER_LAN_USER_LIMIT=0
DOCROPPER_ADMIN_EMAIL=admin@example.com
DOCROPPER_ADMIN_PASSWORD=changeme
DOCROPPER_DEV_PASSWORD=87654321
DOCROPPER_SETTINGS_PASSWORD=12345678
```

The SQLite file (`db.sqlite3`) stores authentication data and is ignored by Git.
Install scripts remove this file during updates to avoid merge conflicts; if you
need to preserve accounts, back up the database before running an update.

### Backup e migrazioni del database

Per salvare una copia di sicurezza è sufficiente duplicare il file SQLite:

```bash
cp db.sqlite3 db.sqlite3.bak
# oppure con l'utilità integrata di SQLite
sqlite3 db.sqlite3 ".backup 'db.sqlite3.bak'"
```

Se i modelli cambiano, le tabelle possono essere aggiornate con uno strumento
di migrazione come [Alembic](https://alembic.sqlalchemy.org/):

```bash
alembic revision --autogenerate -m "messaggio"
alembic upgrade head
```

Per modifiche minori è possibile eliminare `db.sqlite3` e lasciare che le
tabelle vengano ricreate automaticamente all'avvio dell'applicazione.

---

## ▶️ Running DocCropper

Activate your virtual environment and run the server with `uvicorn main:app --host 0.0.0.0 --port 8765` (or simply `python main.py`). The default port is **8765** but can be changed in `settings.json` or via `--port`.

Send a POST to `/shutdown/` to stop the server. The helper script `doccropper_tray.py` may also be used to manage the server via a system tray icon.

### Tray icon usage

The tray helper works on Windows and most Linux desktops. macOS support is
experimental and not yet thoroughly tested. It loads the
application logo and shows a green or red dot indicating whether the server is
running. Use the menu to start, stop or update DocCropper, or open the site in
your browser. On Linux the icon now responds to left clicks by launching the
default **Open App** action so you can access commands just like on Windows.
You may need the `python3-gi` and `libappindicator3`
packages so the tray menu can display correctly. If no graphical environment is
available, run it with the `--no-tray` option to start the server without
showing an icon:

```bash
python doccropper_tray.py --no-tray
```
Use the `--auto-start` flag to start the server automatically when launching the
tray helper manually.
If the tray cannot be shown, the script automatically launches the server
without it.

### Docker

A sample Dockerfile and compose file are provided under `docker/`. The Docker
image installs Tesseract OCR and the runtime libraries required by OpenCV so all
features work out of the box. Build and launch the container from the repository
root with:

```bash
docker compose -f docker/docker-compose.yml up --build
```

The compose file mounts the `env/` and `users/` folders so you can customise
settings and keep user data persistent between rebuilds. Copy the example files
from `env/` and adjust them before running the container.

Additional packages can be added by extending `docker/Dockerfile` if your
deployment requires them.

For the full enterprise build that includes the optional Google OAuth helper,
use the provided multi-service compose file:

```bash
docker compose -f docker/docker-compose.full.yml up --build
```

Set `CLIENT_ID`, `CLIENT_SECRET` and `REDIRECT_URI` in your environment before
launching. The auth service listens on port `8766` by default and proxies login
requests for the main app.


### Built-in Wiki

An offline copy of the documentation is included under the `/wiki` path. The
web interface displays this wiki in a sidebar on the right beneath the Help
button. A language-specific page is loaded based on your selection. You can
also open it in a new tab at `http://<host>:<port>/wiki/<lang>/` (by default
`http://localhost:8765/wiki/<lang>/`) or view the online version on GitHub.

### Admin Page

Developers can manage global settings and user accounts from a dedicated admin
interface available at `/admin`. Access to this page requires authentication as a
superuser using the `/auth/jwt/login` endpoint. Once logged in, the page exposes
the same options found in the settings panel and lists all registered users with
the ability to create or remove them. It relies on the REST endpoints under
`/settings/`, `/auth/` and `/users/`.

### Google Sign-In

To enable optional Google authentication, set `google_client_id` in
`settings.json` or provide it via the environment variable
`DOCROPPER_GOOGLE_CLIENT_ID`. The login module is active only when
`license_check` is enabled; otherwise the sign-in button remains hidden even if
a client ID is provided. The module is implemented as a plugin and currently
flagged developer-only (`DOCROPPER_LOGIN_DEV_ONLY` / `login_dev_only`), so it
loads only for developer licenses until finished. When configured, the web
interface displays the button and tokens are verified by the backend. When the
hidden Demo Full license is active the login button is hidden even if
`google_client_id` is set.

---

## 🔓 Licensing

DocCropper ships with three editions. A **Licenses** button in the header opens a panel where you can review the editions and enter your license key. Free users may paste a key here at any time to unlock Pro or Full features.

- **Free** – Watermark applied and up to five images per project
- **Pro** – No watermark and unlimited images. A LAN plugin can add network
  access for a limited number of users in steps of five (5, 10, 15...).
- **Full** – All features unlocked including unrestricted LAN access and any
  optional plugins
- *Demo Full* is a hidden license that behaves like the Full edition but keeps
  the watermark, enables mobile signing, and shows a demo notice.
  When this license is active the **Purchase** button turns into a PayPal
  donation link that opens in a new tab.

When the LAN plugin is active the `lan_user_limit` setting controls how many
accounts may use DocCropper over the network. Licenses are typically sold in
blocks of five users (5, 10, 15 and so on).

Both Pro and Full can run offline on Windows, macOS or Linux after activation. An internet connection is only needed to activate and renew the license; sponsored licenses also require connectivity to fetch the default Facebook post.

DocCropper itself is released under the [MIT](LICENSE.txt) license. See [Terms of Use](TERMS_OF_USE.md) for additional conditions.

To activate Pro or Full editions:
- Provide a valid license key in `settings.json`, `.env`, or the Licenses panel
  - Developer keys unlock all features when `DOCROPPER_DEV_LICENSE` matches your `license_key`
    or the key ends with `-DEV`. Saving such a key through the Licenses panel now
     automatically sets the edition to **Full** and enables mobile signing. When a
     developer key is active the tray menu includes an **Update Branch** option.
- Mobile signing is enabled automatically when a developer key is used
- Set `LICENSE_CHECK=true` in your `.env` to verify the key with a remote server. With `LICENSE_CHECK=false` (default) the app trusts the provided key.
If the server response includes an `active_plugins` list, DocCropper automatically shows buttons for those modules and hides tools for any plugins that are disabled or unlicensed. Developer builds therefore see in-progress plugins while production installations do not.

### License verification via Joomla + Fabrik with a user token

You can verify licenses remotely by linking DocCropper to a Joomla site that uses the Fabrik extension. Each license entry must contain a unique token which will be compared with the one stored for the user.

**Joomla requirements:**

- Fabrik extension installed
- Create a Fabrik list called *licenze* with the columns `email`, `license`, `valida` and `token`

**Fabrik configuration:**

- Enable querystring filtering on `email`, `license` and `token`
- Enable the RAW view of the list
- Create a template override at:

  `templates/tuotemplate/html/com_fabrik/list/licenze/default_raw.php`

  with this code:

```php
<?php
defined('_JEXEC') or die();
header('Content-Type: application/json');

$rows = $this->rows;
$valid = false;

if (count($rows) > 0) {
  $row = $rows[0];
  $valid = ($row->valida == '1' || strtolower($row->valida) == 'sì');
  echo json_encode([
    "email" => $row->email,
    "license" => $row->license,
    "valid" => $valid
  ]);
} else {
  echo json_encode([
    "valid" => false,
    "reason" => "not found or invalid token"
  ]);
}

The endpoint may also return:

- a `plugins` object to toggle optional components, e.g. `{"plugins": {"mobilesign": true}}`.
- a `settings` object with values that must be enforced on the client.
  Any key provided here overrides the local configuration and is stored in
  `license_overrides.json` so users cannot modify it without a new license.

```

Add the following line to DocCropper's `.env` file:

```
LICENSE_CHECK_URL=https://yourdomain.tld/index.php?option=com_fabrik&view=list&listid=XXX&format=raw
```

(Replace `XXX` with the ID of your Fabrik license list. The token is appended automatically when DocCropper performs the request.)

Example URL with token:

```
https://yourdomain.tld/index.php?option=com_fabrik&view=list&listid=5&format=raw&email=user@example.com&license=pro&token=ABC123DEF456
```

For inquiries: **doccropper@iltuoconsulenteit.it**

## 💖 Supporta DocCropper

Se trovi utile DocCropper, puoi supportarne lo sviluppo con una donazione:

[![Donate](https://www.paypalobjects.com/it_IT/IT/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate/?hosted_button_id=XGKVRL2YQBPDY)

### Optional PDF Signing

Simple image or drawn signatures are available in all editions, but the Free edition keeps the watermark on exported PDFs.

Signature functionality is split into three plugins under `plugins/` and each
may be enabled individually using the `DOCROPPER_ENABLE_*` variables or the
matching keys in `settings.json`. Every plugin also supports a
`DOCROPPER_<NAME>_DEV_ONLY` flag (or `<name>_dev_only` setting) so unfinished
features remain visible only to developer licenses until promoted.
Development builds ship with all plugins enabled, letting developer licenses test new modules without manual configuration.

Plugins include:
`sign` for local page stamping, `mobilesign` for signing from a smartphone,
`docuseal` for uploading PDFs to a Docuseal instance, and `remotesign` for
external command based signing. The Free edition only allows stamping one page
with the `sign` plugin, while Pro removes this limit.
`mobilesign` is an add-on for Pro users and included in the Full edition. The
mobile signing page includes a disclaimer that DocCropper and its authors accept
no liability for illegal use. After scanning the QR code the phone fetches all
pages so you can choose any page from the dropdown. Press **Finish** to lock the
signatures. Contract-signing workflows may be provided as a Full edition
feature.
DocCropper can apply a personal signature in several ways:

1. **Image Stamp** – Click the **Sign Page** button to open the signing panel,
   then select the page to sign from the dropdown and upload a signature image.
   White backgrounds are automatically removed.
   Alternatively, press **Draw signature** to handwrite your signature with a mouse or
   touch device. A dashed border shows where to draw. Clear and reuse the drawing until
   satisfied.
   Double-click the page preview to set where the signature should appear, then
   drag if needed and press **Add** to queue it for that page. Use **Save** to
   embed the placed stamps or **Discard** to cancel. You may add multiple
   signatures to any page before exporting the final PDF.
   Each new stamp is offset slightly so it doesn’t hide the previous one by default.
2. **Mobile Sign** – Before creating the QR code you may mark where each remote signer should place their signature. Open the signature panel, double-click the preview and press **Add** without loading a signature image to drop a red cross marker. Then use the **Mobile Sign** button (in the panel or export menu) to generate a one-time token and QR code. Scan it with your phone or tablet and draw your signature on the indicated pages. The drawing is saved under `signatures/signature_<token>.png` and added to the PDF.
3. **Remote Digital Signing** – Configure the Docuseal plugin with `DOCUSEAL_API_URL` and `DOCUSEAL_API_KEY` to upload the exported PDF to a Docuseal instance. Press **Digital Sign** to receive a link where the document can be signed online. You may still enable the `remotesign` plugin and set `DOCROPPER_REMOTE_SIGN_CMD` to run a custom signing script instead.

   - GET `/start-sign/` returns `{token, url, qr}` with a QR code for the LAN link
   - Visit `/sign/<token>` to draw the signature
   - POST `/submit-signature/<token>` with `{image: "data:image/png;base64,..."}` to save it
   - POST `/docuseal-sign/` uploads the last exported PDF to Docuseal and returns `{url}`
   - POST `/remote-sign/` runs the external signing command and returns the signed PDF

Alternatively, you may set `DOCROPPER_SIGN_CERT` and `DOCROPPER_SIGN_PASSWORD` to automatically apply a local PKCS#12 certificate.

When `DOCROPPER_TUNNEL=true` and `cloudflared` is installed, DocCropper can
launch a temporary Cloudflare Tunnel so the signing link works from outside your
LAN. The public URL is written to the log.

Set `DOCROPPER_OPEN_URL` if you want DocCropper or the tray helper to open a
custom address (for example your Cloudflare tunnel) instead of
`http://localhost:PORT`.
You may configure the public domain used for mobile signing either through the
Settings panel or by setting `DOCROPPER_PUBLIC_URL`. When the demo license is
active the default domain is `https://doccropper.iltuoconsulenteit.it`.
The server also accepts cross-origin requests when you set
`DOCROPPER_CORS_ORIGINS` to a comma-separated list of allowed origins or `*` to
permit any origin.
Uploads larger than the configured `max_upload_mb` (5&nbsp;MB by default) will be rejected to avoid excessive disk usage.

### Pro OCR (coming soon)

OCR capabilities will be offered in a future licensed edition. The current release hides the **Extract Text** button.


## Disclaimer

DocCropper and its authors accept no liability for illegal use.

## Credits

This project is originally based on [varna9000/image-perspective-crop](https://github.com/varna9000/image-perspective-crop). Significant modifications and new features were added for broader usability.


### Node OAuth Example

For a minimal demonstration using **express-session** and Passport, run the Node server:

```bash
npm install
npm start
```

Create a `.env` file based on `env/google.env.example` with your Google `CLIENT_ID`, `CLIENT_SECRET` and `REDIRECT_URI` (e.g. `http://localhost:8765/auth/google/callback`).
You may also copy any of the sample files under `env/` if you wish to test
additional features such as Docuseal or local signing.

Visit [http://localhost:8765](http://localhost:8765) and click **Login with Google**. After authenticating you'll be redirected to `/dashboard` which shows your name and email.

