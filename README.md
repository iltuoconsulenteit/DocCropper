# 📄 DocCropper

**DocCropper** is a web-based app for batch document perspective correction, multi-image cropping, mobile signing, and PDF export.

This project is **inspired by [image-perspective-crop](https://github.com/varna9000/image-perspective-crop)**, but has been **significantly rewritten and extended**, with major architectural changes, a redesigned user interface, batch features, user preferences, and many additional capabilities.

---

## ✨ Key Features

- ✅ Multi-image upload and batch processing
- 📥 Import PDF files and place each page directly in the gallery for later editing (Pro)
- 🔄 Automatic or manual perspective correction
- 🖼️ Interactive cropping and preview
- 🖱️ Double click or tap to auto-detect page edges
- 🎚️ Adjust brightness and contrast with live preview
- 🖌️ Convert images to grayscale or black & white to reduce PDF size (Pro)
- 🎨 Restore color later with a dedicated button
 - 🧹 Skip blank pages when importing PDFs using a configurable threshold (Pro)
- 📄 Create PDFs ready for download or sharing
- 🔏 Optional digital signature on exported PDFs. Drag and add multiple stamps per page before export (Free - watermark applied)
- ✍️ Sign from your phone via QR code and save the drawing for later use (Pro)
- 📤 Share PDFs via WhatsApp Web or Email, attaching files via the Web Share API when possible (Pro)
- 🗂️ Drag thumbnails to reorder images before exporting (Pro)
- 🖼️ Closable banner can rotate multiple promotional images
- 📝 Extract text via OCR (future Pro feature)
- 🗂️ Persistent user settings
- 🧭 Touchscreen-friendly interface
- 🎨 Material design look with Roboto fonts and raised buttons
- 🌐 Works offline or over LAN (no internet required)
- 👤 Multi-user environment support (optional)
- 🔒 Uploaded files are encrypted and wiped after your session
- 📏 Uploads larger than 20&nbsp;MB are rejected (adjust with `DOCROPPER_MAX_UPLOAD_MB`)
- 🚀 Cache busting (`?v=<commit>`) ensures browsers fetch updated files

---

## 🔧 Frontend

This project uses [Interact.JS](https://github.com/taye/interact.js) for managing draggable corner points.

The frontend allows the user to:
 - Upload images with the file picker. On mobile devices the file picker is shown by default but you can switch to the camera mode and choose which camera to use. Desktop users may also drag and drop files
 - Import PDF documents which are converted to images and added to the gallery without immediate cropping (Pro)
- Add more images later without losing previously processed ones
- Manually adjust the four corners of each image
- Double click/tap an image to auto-detect its edges
- Submit data (image, coordinates, size) to the backend
- Export all processed images to PDF
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

Logos and branding can be customized via `static/logos/`, `settings.json`, and `brand_html`. A dedicated area in the header can show a client logo (`client_logo`), a rotating slogan banner and an optional sponsor logo (`sponsor_logo`). Logo height and spacing can be tuned with `brand_height` and `brand_gap`. The `sponsor_scale` and `sponsor_bottom` settings control the video banner size and position. The header also shows a language-specific slogan image (e.g. `DocCropper_slogan_en.png`), and the footer displays the current Git commit hash. Licensed users can also convert images to grayscale or black & white using buttons below each thumbnail, and a global color mode option applies to all images before PDF export.
Blank pages can be skipped during PDF import. Enable **Skip blank pages** in the layout controls and adjust the `blank_threshold` percentage (95% by default).
Pages over this threshold are discarded in the Pro edition.

User preferences are stored in the `users/` folder based on their email address. Anonymous users fallback to global settings in `settings.json`. The system supports optional Google sign-in and a configurable purchase panel (donation or subscription) opened from the **Purchase** button next to the Help button. Payment links can be supplied via `settings.json` or through Stripe credentials in `env/stripe.env.example`. Developer keys allow full access when the configured `license_key` matches the value of the `DOCROPPER_DEV_LICENSE` environment variable.

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
pip install -r requirements.txt
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

### Required environment variables

Create a `.env` file (or multiple `.env` files inside the `env/` directory)
with at least the authentication variables and your license check URL:

```bash
SECRET_KEY=change-me
DATABASE_URL=sqlite+aiosqlite:///./db.sqlite3
LICENSE_CHECK_URL=https://tuodominio.it/index.php?option=com_fabrik&view=list&listid=XXX&format=raw
```

---

## ▶️ Running DocCropper

Activate your virtual environment and run the server with `uvicorn main:app --host 0.0.0.0 --port 8765` (or simply `python main.py`). The default port is **8765** but can be changed in `settings.json` or via `--port`.

Send a POST to `/shutdown/` to stop the server. The helper script `doccropper_tray.py` may also be used to manage the server via a system tray icon.

### Tray icon usage

The tray helper works on Windows and most Linux desktops. macOS support is
experimental and not yet thoroughly tested. It loads the
application logo and shows a green or red dot indicating whether the server is
running. Use the menu to start, stop or update DocCropper, or open the site in
your browser. On Linux you may need the `python3-gi` and `libappindicator3`
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

### Built-in Wiki

An offline copy of the documentation is included under the `/wiki` path. The
web interface displays this wiki in a sidebar on the right beneath the Help
button. A language-specific page is loaded based on your selection. You can
also open it in a new tab at `http://<host>:<port>/wiki/<lang>/` (by default
`http://localhost:8765/wiki/<lang>/`) or view the online version on GitHub.

### Google Sign-In

To enable optional Google authentication, set `google_client_id` in
`settings.json` or provide it via the environment variable
`DOCROPPER_GOOGLE_CLIENT_ID`. When configured, a sign-in button will appear in
the web interface and tokens will be verified by the backend. Google login is
only used to identify users and is not tied to licensing.
When the hidden Demo Full license is active the login button is hidden even if
`google_client_id` is set.

---

## 🔓 Licensing

DocCropper ships with three editions. A **Licenses** button in the header opens a panel where you can review the editions and enter your license key. Free users may paste a key here at any time to unlock Pro or Full features.

- **Free** – Watermark applied, up to five images per project, LAN access disabled
- **Pro** – No watermark and unlimited images, but still restricted to local access
- **Lan** – Same as Pro but enabled for LAN usage only
- **Full** – Unlocks all features including LAN and any optional plugins
- *Demo Full* is a hidden license that behaves like the Full edition but keeps
  the watermark, enables mobile signing, and shows a demo notice.
  When this license is active the **Purchase** button turns into a PayPal
  donation link.

DocCropper itself is released under the [MIT](LICENSE.txt) license. See [Terms of Use](TERMS_OF_USE.md) for additional conditions.

To activate Pro or Full editions:
- Provide a valid license key in `settings.json`, `.env`, or the Licenses panel
  - Developer keys unlock all features when `DOCROPPER_DEV_LICENSE` matches your `license_key`
    or the key ends with `-DEV`. Saving such a key through the Licenses panel now
     automatically sets the edition to **Full** and enables mobile signing. When a
     developer key is active the tray menu includes an **Update Branch** option.
- Mobile signing is enabled automatically when a developer key is used
- Set `LICENSE_CHECK=true` in your `.env` to verify the key with a remote server. With `LICENSE_CHECK=false` (default) the app trusts the provided key.
If the server response includes a `plugins` map, DocCropper will automatically enable or disable the corresponding `enable_<plugin>` settings.

### Verifica licenze tramite Joomla + Fabrik con token utente

Per abilitare il controllo licenze remoto, è possibile collegare DocCropper a un sito Joomla con Fabrik configurato. Ogni licenza deve possedere un token segreto per una verifica più sicura.

**Requisiti lato Joomla:**

- Estensione Fabrik installata
- Creare una tabella Fabrik chiamata *licenze* con i campi `email`, `license`, `valida` e `token`

**Configurazioni Fabrik:**

- Abilitare filtro da querystring su `email`, `license` e `token`
- Abilitare la vista RAW della lista
- Creare un override del template nella directory:

  `templates/tuotemplate/html/com_fabrik/list/licenze/default_raw.php`

  con questo codice:

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
The endpoint may also return a `plugins` object to toggle optional components, e.g. `{"plugins": {"mobilesign": true}}`.

```

Configura nel file `.env` di DocCropper:

```
LICENSE_CHECK_URL=https://tuodominio.it/index.php?option=com_fabrik&view=list&listid=XXX&format=raw
```

(Sostituisci `XXX` con l'ID reale della tabella Fabrik delle licenze. Il token verrà aggiunto automaticamente alle richieste.)

Esempio di URL completo con token:

```
https://tuodominio.it/index.php?option=com_fabrik&view=list&listid=5&format=raw&email=user@example.com&license=pro&token=ABC123DEF456
```

For inquiries: **doccropper@iltuoconsulenteit.it**

## 💖 Supporta DocCropper

Se trovi utile DocCropper, puoi supportarne lo sviluppo con una donazione:

[![Donate](https://www.paypalobjects.com/it_IT/IT/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate/?hosted_button_id=XGKVRL2YQBPDY)

### Optional PDF Signing

Simple image or drawn signatures are available in all editions, but the Free edition keeps the watermark on exported PDFs.

Signature functionality is split into three plugins under `plugins/` and each
may be enabled individually using the `DOCROPPER_ENABLE_*` variables or the
matching keys in `settings.json`:
`sign` for local page stamping, `mobilesign` for signing from a smartphone and
`remotesign` for Docuseal or other external services. The Free edition only
allows stamping one page with the `sign` plugin, while Pro removes this limit.
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
3. **Remote Digital Signing** – Configure `DOCUSEAL_API_URL` and `DOCUSEAL_API_KEY` to upload the exported PDF to a Docuseal instance. Press **Digital Sign** to receive a link where the document can be signed online. You may still set `DOCROPPER_REMOTE_SIGN_CMD` to run a custom script instead.

   - GET `/start-sign/` returns `{token, url, qr}` with a QR code for the LAN link
   - Visit `/sign/<token>` to draw the signature
   - POST `/submit-signature/<token>` with `{image: "data:image/png;base64,..."}` to save it
   - POST `/docuseal-sign/` uploads the last exported PDF to Docuseal and returns `{url}`

Alternatively, you may set `DOCROPPER_SIGN_CERT` and `DOCROPPER_SIGN_PASSWORD` to automatically apply a local PKCS#12 certificate.

When `DOCROPPER_TUNNEL=true` and `cloudflared` is installed, the start scripts
launch a temporary Cloudflare Tunnel so the signing link works from outside your
LAN. The public URL is written to the log.

Set `DOCROPPER_OPEN_URL` if you want the start scripts and tray helper to open a
custom address (for example your Cloudflare tunnel) instead of
`http://localhost:PORT`.
You may configure the public domain used for mobile signing either through the
Settings panel or by setting `DOCROPPER_PUBLIC_URL`. When the demo license is
active the default domain is `https://doccropper.iltuoconsulenteit.it`.
The server also accepts cross-origin requests when you set
`DOCROPPER_CORS_ORIGINS` to a comma-separated list of allowed origins or `*` to
permit any origin.
Uploads larger than the configured `DOCROPPER_MAX_UPLOAD_MB` (20&nbsp;MB by default) will be rejected to avoid excessive disk usage.

### Pro OCR (coming soon)

OCR capabilities will be offered in a future licensed edition. The current release hides the **Extract Text** button.


## Credits

This project is originally based on [varna9000/image-perspective-crop](https://github.com/varna9000/image-perspective-crop). Significant modifications and new features were added for broader usability.


### Node OAuth Example

For a minimal demonstration using **express-session** and Passport, run the Node server:

```bash
npm install
npm start
```

Create a `.env` file based on `.env.example` with your Google `CLIENT_ID`, `CLIENT_SECRET` and `REDIRECT_URI` (e.g. `http://localhost:8765/auth/google/callback`).
You may also copy any of the sample files under `env/` if you wish to test
additional features such as Docuseal or local signing.

Visit [http://localhost:8765](http://localhost:8765) and click **Login with Google**. After authenticating you'll be redirected to `/dashboard` which shows your name and email.

