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
- 🌐 Works offline or over LAN (no internet required)
- 👤 Multi-user environment support (optional)

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
- Choose whether images are arranged horizontally, vertically or in a grid and preview the layout before exporting
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

Logos and branding can be customized via `static/logos/`, `settings.json`, and `brand_html`. A dedicated area in the header can show a client logo (`client_logo`) and an optional sponsor banner (`sponsor_logo`). The `sponsor_scale` and `sponsor_bottom` settings control the banner size and position. The header also shows a language-specific slogan image (e.g. `DocCropper_slogan_en.png`), and the footer displays the current Git commit hash. Licensed users can also convert images to grayscale or black & white using buttons below each thumbnail, and a global color mode option applies to all images before PDF export.
Blank pages can be skipped during PDF import. Enable **Skip blank pages** in the layout controls and adjust the `blank_threshold` percentage (95% by default).
Pages over this threshold are discarded in the Pro edition.

User preferences are stored in the `users/` folder based on their email address. Anonymous users fallback to global settings in `settings.json`. The system supports optional Google sign-in and a configurable purchase panel (donation or subscription) opened from the **Purchase** button next to the Help button. Developer keys allow full access when the configured `license_key` matches the value of the `DOCROPPER_DEV_LICENSE` environment variable.

---

## 🐍 Backend

Built with **FastAPI + Uvicorn**, the backend:
- Applies a perspective transformation and cropping
- Optionally sharpens the image
- Compiles all processed images into a PDF with layout control
- Handles per-session temporary folders

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

### 🛠 Installer Scripts

- Clone the repo
- Offer a numbered menu to choose `main` or the developer branch (default `codex/remove-shortcut-installation-and-scanner-capture`)
- Set up the environment and install Python dependencies in a virtualenv
- Ask for an optional license key
- Write a log file named `install.log` in the installation folder (falling back to `%TEMP%` on Windows or `/tmp` on Linux/macOS)
- On Linux the installer now requests administrative privileges via `sudo` and installs under `/opt/DocCropper` by default. On macOS the script will similarly relaunch with `sudo` if installing to `/Applications`. If the directory cannot be created, the script exits with a permissions error. The script uses `tee` to create the initial `settings.json` so root permissions are required when installing to system locations. Existing `settings.json` files are backed up to `settings.local.json.bak` and merged back after updating so your license and other custom values are preserved.
- Matching `uninstall_DocCropper` scripts are provided to remove the application later.
You can override the branches with `DOCROPPER_DEV_BRANCH` for the developer branch or `DOCROPPER_BRANCH` to force a specific branch.

You can pre-populate `settings.json` or override values using `.env` files in the `env/` folder.
The `.env` files may also define `LICENSE_CHECK=true` to enforce license validation via a remote server.
To quickly create an environment file for testing you can run one of the
`scripts/setup_license` helpers. The script for your platform (`.bat`, `.sh` or
`.command`) asks for your license key and name then writes `env/developer.env`
with `DOCROPPER_LICENSE_KEY`, `DOCROPPER_LICENSE_NAME` and
`DOCROPPER_DEV_LICENSE` so all features are unlocked. Set
`DOCROPPER_DEV_WATERMARK=true` if you want to keep the watermark while
testing with a developer key.
If you see **Access denied** when running the script, launch it with administrator
privileges ("Run as Administrator" on Windows). After writing the
`env/developer.env` file, restart DocCropper so the new license is applied.

---

## ▶️ Running DocCropper

Use the included start scripts from the `scripts/` directory. They handle virtualenv creation and dependency install. On Windows, `start_DocCropper.bat` writes details to `%TEMP%\DocCropper_start.log` so you can troubleshoot launch problems. The script stops any running instance first and pauses before closing so errors remain visible. DocCropper stores its PID file in the system temp folder so it can be managed without admin rights. By default the server listens on **port 8765** unless you override it in `settings.json` or with `--port`.

To stop the server, run the matching stop script or send a POST to `/shutdown/`.

### ❌ Uninstalling

Run the appropriate `uninstall_DocCropper` script from the `install/` folder to completely remove DocCropper. The script stops any running instance and then deletes the installation directory. On Windows it will request administrator privileges if required.

You may also launch `doccropper_tray.py` (or `.pyw`) to manage the server with a system tray icon.

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
tray helper.
If the tray cannot be shown, the script automatically launches the server
without it.

### Built-in Wiki

An offline copy of the documentation is included under the `/wiki` path. The
web interface displays this wiki in a sidebar on the right beneath the Help
button. A language-specific page is loaded based on your selection. You can
also open it in a new tab at `http://localhost:8765/wiki/&lt;lang&gt;/` or view
the online version on GitHub.

### Google Sign-In

To enable optional Google authentication, set `google_client_id` in
`settings.json` or provide it via the environment variable
`DOCROPPER_GOOGLE_CLIENT_ID`. When configured, a sign-in button will appear in
the web interface and tokens will be verified by the backend. Google login is
only used to identify users and is not tied to licensing.

---

## 🔓 Licensing

DocCropper ships with three editions. A new **Licenses** button in the header opens a panel explaining these options.

- **Free** – Watermark applied, up to five images per project, LAN access disabled
- **Pro** – No watermark and unlimited images, but still restricted to local access
- **Full** – Unlocks LAN access so DocCropper can run on an office server

DocCropper itself is released under the [MIT](LICENSE.txt) license. See [Terms of Use](TERMS_OF_USE.md) for additional conditions.

To activate Pro or Full editions:
- Provide a valid license key in `settings.json` or `.env`
- Developer keys unlock all features for testing when `DOCROPPER_DEV_LICENSE` matches your `license_key`
- You can generate a suitable `.env` by running `scripts/setup_license.bat` (or
  `.sh` / `.command`) and entering your details
- Set `LICENSE_CHECK=true` to verify the key with a remote server. With `LICENSE_CHECK=false` (default) the app trusts the provided key.

For inquiries: **doccropper@iltuoconsulenteit.it**

### Optional PDF Signing

Simple image or drawn signatures are available in all editions, but the Free edition keeps the watermark on exported PDFs.

DocCropper can apply a personal signature in several ways:

1. **Image Stamp** – Use the action menu below each processed page and choose `Sign`
   to upload a signature image. White backgrounds are automatically removed.
   Alternatively, press **Draw signature** to handwrite your signature with a mouse or
   touch device. A dashed border shows where to draw. Clear and reuse the drawing until
   satisfied.
   Drag the previewed stamp on the page canvas, adjust its scale, then press **Add**
   to queue it for that page. Use **Save** to embed the placed stamps or **Discard**
   to cancel. You may add multiple signatures to any page before exporting the final PDF.
   Each new stamp is offset slightly so it doesn’t hide the previous one by default.
2. **Remote Digital Signing** – Set `DOCROPPER_REMOTE_SIGN_CMD` to an external signing command (e.g. an Aruba Sign script). After creating the PDF, press **Remote Sign** to apply the digital signature to the entire document.
3. **Touch Signature** – Press **Remote Sign** and DocCropper generates a one-time token and LAN link. Scan the QR code with your phone or tablet and sign on the provided page. The drawing is saved under `signatures/signature_<token>.png`.

   - GET `/start-sign/` returns `{token, url, qr}` with a QR code for the LAN link
   - Visit `/sign/<token>` to draw the signature
   - POST `/submit-signature/<token>` with `{image: "data:image/png;base64,..."}` to save it

Alternatively, you may set `DOCROPPER_SIGN_CERT` and `DOCROPPER_SIGN_PASSWORD` to automatically apply a local PKCS#12 certificate.

When `DOCROPPER_TUNNEL=true` and `cloudflared` is installed, the start scripts
launch a temporary Cloudflare Tunnel so the signing link works from outside your
LAN. The public URL is written to the log.

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

Create a `.env` file based on `.env.example` with your Google `CLIENT_ID`, `CLIENT_SECRET` and `REDIRECT_URI` (e.g. `http://localhost:8000/auth/google/callback`). Optionally set `DOCROPPER_SIGN_CERT` and `DOCROPPER_SIGN_PASSWORD` to sign PDFs automatically.

Visit [http://localhost:8000](http://localhost:8000) and click **Login with Google**. After authenticating you'll be redirected to `/dashboard` which shows your name and email.

