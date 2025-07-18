# 📄 DocCropper

**DocCropper** is a web-based application for document image perspective correction, cropping, and PDF export. It is designed to work both locally and in LAN environments, including touchscreen or kiosk-style workstations.

This project is **inspired by [image-perspective-crop](https://github.com/varna9000/image-perspective-crop)**, but has been **significantly rewritten and extended**, with major architectural changes, a redesigned user interface, batch features, user preferences, and many additional capabilities.

---

## ✨ Key Features

- ✅ Multi-image upload and batch processing
- 🔄 Automatic or manual perspective correction
- 🖼️ Interactive cropping and preview
- 📄 One-click PDF export
- 🗂️ Persistent user settings
- 🧭 Touchscreen-friendly interface
- 🌐 Works offline or over LAN (no internet required)
- 👤 Multi-user environment support (optional)

---

## 🔧 Frontend

This project uses [Interact.JS](https://github.com/taye/interact.js) for managing draggable corner points.

The frontend allows the user to:
- Upload one or more images (on mobile devices the file picker can use the camera directly)
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

Logos and branding can be customized via `static/logos/`, `settings.json`, and the
`brand_html` field which populates a client branding box in the header. The
footer displays the current Git commit hash.

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
- Set up the environment
- Automatically install Git if needed (using winget or by downloading the
  official installer). If Git is installed but not in `PATH`, the Windows
  installer searches the standard `Program Files` directories before
  attempting a reinstall
- Ask for optional license key
- Let you choose the branch to install (type `1` for `main` or `2` for the developer branch)
- You can override the developer branch by setting the `DOCROPPER_DEV_BRANCH` environment variable
- Start the tray icon which launches the server
- Write a log to `install.log` in the install folder while still showing prompts
- On Windows they install to a `DocCropper` directory beside the installer

You can pre-populate `settings.json` or override values using `.env` files in the `env/` folder.

---

## ▶️ Running DocCropper

Use the included start scripts from the `scripts/` directory. They handle virtualenv creation and dependency install.
Keep these scripts inside the DocCropper installation folder or create a shortcut to them.
If you want to run a script from anywhere, set the environment variable `DOCROPPER_HOME` to the installation path.

To stop the server, run the matching stop script or send a POST to `/shutdown/`.

You may also launch `doccropper_tray.py` (or `.pyw`) to manage the server with a system tray icon.

### Tray icon usage

The tray helper works on Windows, macOS and most Linux desktops. If no graphical
environment is available, run it with the `--no-tray` option to start the server
without showing an icon:

```bash
python doccropper_tray.py --no-tray
```
If the tray cannot be shown, the script automatically launches the server
without it.
You can use the `--auto-start` flag to start the server immediately and still
show the tray icon.

### Google Sign-In

To enable optional Google authentication, set `google_client_id` in
`settings.json` or provide it via the environment variable
`DOCROPPER_GOOGLE_CLIENT_ID`. When configured, a sign-in button will appear in
the web interface and tokens will be verified by the backend. The current
implementation only identifies the user and is not tied to license activation.
You can implement alternative login methods by extending the
`renderLogin` function in `static/app.js`.

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


## 🔄 Updating DocCropper

To update an existing installation to the latest code on the `main` branch,
re-run the installer script for your platform:

- **Windows**: `install/install_DocCropper.bat`
- **Linux/macOS**: `bash install/install_DocCropper.sh`

The installer will pull the most recent changes and preserve your
configuration. To update from a different branch, set the environment variable
`DOCROPPER_BRANCH` before running the installer:

```bash
set DOCROPPER_BRANCH=my-feature-branch && install\install_DocCropper.bat  # Windows
export DOCROPPER_BRANCH=my-feature-branch && bash install/install_DocCropper.sh  # Linux/macOS
```

You can also trigger "Update from main" or "Update from branch" from the system
tray icon.

For inquiries: **doccropper@iltuoconsulenteit.it**

## \uD83D\uDCD6 Usage Instructions

More extensive documentation is available in the project Wiki, stored in the
`wiki/` folder of this repository. Start reading from
[`wiki/Home.md`](wiki/Home.md) or browse the online version at:
<https://github.com/iltuoconsulenteit/DocCropper/wiki>


## Credits

This project is originally based on [varna9000/image-perspective-crop](https://github.com/varna9000/image-perspective-crop). Significant modifications and new features were added for broader usability.

