# 📄 DocCropper

**DocCropper** is a web-based application for document image perspective correction, cropping, and PDF export. It is designed to work both locally and in LAN environments, including touchscreen or kiosk-style workstations.

This project is **inspired by [image-perspective-crop](https://github.com/varna9000/image-perspective-crop)**, but has been **significantly rewritten and extended**, with major architectural changes, a redesigned user interface, batch features, user preferences, and many additional capabilities.

---

## ✨ Key Features

- ✅ Multi-image upload and batch processing
- 🔄 Automatic or manual perspective correction
- 🖼️ Interactive cropping and preview
- 🎚️ Adjust brightness and contrast with live preview
- 📄 One-click PDF export
- 🔏 Optional digital signature on exported PDFs
- 📝 Extract text via OCR (future Pro feature)
- 🗂️ Persistent user settings
- 🧭 Touchscreen-friendly interface
- 🌐 Works offline or over LAN (no internet required)
- 👤 Multi-user environment support (optional)

---

## 🔧 Frontend

This project uses [Interact.JS](https://github.com/taye/interact.js) for managing draggable corner points.

The frontend allows the user to:
- Upload images with the file picker. Mobile devices can capture multiple photos or choose from the gallery, while desktop users may also drag and drop files
- Add more images later without losing previously processed ones
- Manually adjust the four corners of each image
- Submit data (image, coordinates, size) to the backend
- Export all processed images to PDF
- Choose how many processed images appear on each PDF page
- Select portrait or landscape orientation for the PDF
- Choose whether images are arranged horizontally, vertically or in a grid and preview the layout before exporting
- Control how images are scaled on each page: fill the cell, keep original size or apply a custom percentage
- A small margin is applied around each image so nothing touches the page edges
- Change the interface language (Italian translation included)
- The layout is responsive so DocCropper works well on smartphones and tablets

JavaScript logic is contained in `static/app.js`.

**Data sent to backend:**
- `original_height`, `original_width`: dimensions of the image
- `points`: coordinates of the 4 corners (TL, TR, BR, BL)
- `image_file`: the uploaded file

Images are processed and displayed as thumbnails with **Rotate**, **Edit**, and **Delete** buttons. Preview and layout configuration options are also provided before export.

Logos and branding can be customized via `static/logos/`, `settings.json`, and `brand_html`. The header shows a language-specific slogan image (e.g. `DocCropper_slogan_en.png`), and the footer displays the current Git commit hash.

User preferences are stored in the `users/` folder based on their email address. Anonymous users fallback to global settings in `settings.json`. The system supports optional Google sign-in and a configurable payment box (donation or subscription). Developer keys allow full access and can be defined in `settings.json` or `.env`.

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
- Set up the environment
- Ask for an optional license key
- Write a log file named `install.log` in the installation folder (falling back to `%TEMP%` on Windows or `/tmp` on Linux/macOS)
You can override the branches with `DOCROPPER_DEV_BRANCH` for the developer
branch or `DOCROPPER_BRANCH` to force a specific branch.

You can pre-populate `settings.json` or override values using `.env` files in the `env/` folder.

---

## ▶️ Running DocCropper

Use the included start scripts from the `scripts/` directory. They handle virtualenv creation and dependency install. On Windows, `start_DocCropper.bat` writes details to `%TEMP%\DocCropper_start.log` so you can troubleshoot launch problems. The script stops any running instance first and pauses before closing so errors remain visible. DocCropper stores its PID file in the system temp folder so it can be managed without admin rights.

To stop the server, run the matching stop script or send a POST to `/shutdown/`.

You may also launch `doccropper_tray.py` (or `.pyw`) to manage the server with a system tray icon.

### Tray icon usage

The tray helper works on Windows, macOS and most Linux desktops. It loads the
application logo and shows a green or red dot indicating whether the server is
running. Use the menu to start, stop or update DocCropper, or open the site in
your browser. If no graphical environment is available, run it with the
`--no-tray` option to start the server without showing an icon:

```bash
python doccropper_tray.py --no-tray
```
Use the `--auto-start` flag to start the server automatically when launching the
tray helper.
If the tray cannot be shown, the script automatically launches the server
without it.

### Built-in Wiki

An offline copy of the documentation is included under the `/wiki` path. The
web interface displays this wiki in a sidebar on the right. You can also open it
in a new tab at [http://localhost:8765/wiki/](http://localhost:8765/wiki/) or
view the online version on GitHub.

### Google Sign-In

To enable optional Google authentication, set `google_client_id` in
`settings.json` or provide it via the environment variable
`DOCROPPER_GOOGLE_CLIENT_ID`. When configured, a sign-in button will appear in
the web interface and tokens will be verified by the backend. Google login is
only used to identify users and is not tied to licensing.

---

## 🔓 Licensing and PRO Features

DocCropper is released under the [MIT](LICENSE.txt) license. Without a license key, the app runs in **DEMO mode** (watermark after first PDF page).

**PRO Features:**
- Removal of watermark
- Network folder support (in development)
- Authenticated LAN access

To activate:
- Use a valid license key in `settings.json` or `.env`
- Developer keys unlock full functionality for testing

For inquiries: **doccropper@iltuoconsulenteit.it**

### Optional PDF Signing

Set `DOCROPPER_SIGN_CERT` to the path of a PKCS#12 certificate and `DOCROPPER_SIGN_PASSWORD` to sign exported PDFs. If no certificate is provided, PDFs are left unsigned.

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

