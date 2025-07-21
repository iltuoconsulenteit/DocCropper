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
- 🗂️ Persistent user settings
- 🧭 Touchscreen-friendly interface
- 🌐 Works offline or over LAN (no internet required)
- 👤 Multi-user environment support (optional)

---

## 🔧 Frontend

This project uses [Interact.JS](https://github.com/taye/interact.js) for managing draggable corner points.

The frontend allows the user to:
- Upload one or more images (on mobile devices the file picker lets you choose existing photos or take a new picture)
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

Logos and branding can be customized via `static/logos/`, `settings.json`, and `brand_html`. The footer displays the current Git commit hash.

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

Run `install/install_DocCropper.bat` (Windows) or `install/install_DocCropper.sh` (Linux/macOS). These scripts:
- Clone the repo
- Offer a numbered menu to choose `main` or the developer branch (default `codex/move-version-number-to-bottom-right`)
- Set up the environment
- Ask for an optional license key
- Write a log file named `install.log` in the installation folder (falling back to `%TEMP%` on Windows or `/tmp` on Linux/macOS)
- Launch the server via the tray icon when finished (the tray runs `start_DocCropper.bat` for you)
You can override the branches with `DOCROPPER_DEV_BRANCH` for the developer
branch or `DOCROPPER_BRANCH` to force a specific branch.

You can pre-populate `settings.json` or override values using `.env` files in the `env/` folder.

---

## ▶️ Running DocCropper

Use the included start scripts from the `scripts/` directory. They handle virtualenv creation and dependency install.

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
- OCR module and network folder support (in development)
- Authenticated LAN access

To activate:
- Use a valid license key in `settings.json` or `.env`
- Developer keys unlock full functionality for testing

For inquiries: **doccropper@iltuoconsulenteit.it**


## Credits

This project is originally based on [varna9000/image-perspective-crop](https://github.com/varna9000/image-perspective-crop). Significant modifications and new features were added for broader usability.

