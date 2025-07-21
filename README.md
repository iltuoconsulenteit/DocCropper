# 📄 DocCropper

**DocCropper** is a web-based application for document image perspective correction, cropping, and PDF export. It is designed to work both locally and in LAN environments, including touchscreen or kiosk-style workstations.

This project is **inspired by [image-perspective-crop](https://github.com/varna9000/image-perspective-crop)**, but has been **significantly rewritten and extended**, with major architectural changes, a redesigned user interface, batch features, user preferences, and many additional capabilities.

---

## ✨ Key Features

- ✅ Multi-image upload and batch processing
- 🔄 Automatic or manual perspective correction
- 🖼️ Interactive cropping and preview
- 🌞 Adjust brightness and contrast before processing
- 📄 One-click PDF export
- 🗂️ Persistent user settings
- 🧭 Touchscreen-friendly interface
- 🌐 Works offline or over LAN (no internet required)
- 👤 Multi-user environment support (optional)
- 📠 Optional scanning support to acquire images directly from a connected scanner

---

## 🔧 Frontend

This project uses [Interact.JS](https://github.com/taye/interact.js) for managing draggable corner points.

The frontend allows the user to:
- Upload one or more images (on mobile devices the file picker can use the camera directly)
- Manually adjust the four corners of each image
- Use brightness and contrast sliders to enhance the document
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
- The default developer branch is `codex/move-version-number-to-bottom-right` but you can override it with the `DOCROPPER_DEV_BRANCH` environment variable
- Start the tray icon which launches the server
- Installer output is saved to `install.log` in the installation directory
- Prompt to launch DocCropper immediately at the end of installation
- Place small wrapper scripts (start and stop) in the installation folder
  which call the real scripts under `scripts/`
- When updating an existing installation the repository is reset to the chosen
  branch and untracked files are removed so missing scripts are restored and
  obsolete files cleaned up
- On Windows the installer requires administrator rights to install under
  `%ProgramFiles%`. If not run as admin it will re-launch itself requesting
  elevation.
- By default they install to `%ProgramFiles%\DocCropper` on Windows,
  `/opt/DocCropper` on Linux and `/Applications/DocCropper` on macOS. If the
  Windows installer cannot create the default directory (for example when not
  running as Administrator) it falls back to a `DocCropper` folder next to the
  batch script. When the chosen directory already contains files you can let the installer remove them or choose a new location.
- If the clone step fails, verify your network connection. If the directory already exists you can let the installer wipe it or choose another location.

If the installation resides under `%ProgramFiles%`, updating also requires administrator rights. Run `install\install_DocCropper.bat` as Administrator again, or install to a folder you can write to such as `%LOCALAPPDATA%\DocCropper`.

You can pre-populate `settings.json` or override values using `.env` files in the `env/` folder.

---

## ▶️ Running DocCropper

Use the start scripts located in the installation folder. They are small wrappers which invoke the real scripts under `scripts/`. When launched, the scripts create a virtual environment if needed and install Python packages before starting DocCropper. The commands show the installation progress so that errors are visible.
If some packages fail to install, the scripts continue so the basic features remain usable. Output from the server is written to `doccropper.log` in the installation folder so you can diagnose issues later.
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

While DocCropper is running the tray icon displays a small green dot that
turns red when the server is stopped. Use the **Open DocCropper** menu item
to launch your browser to the configured address.

### Optional scanning support

DocCropper can acquire images directly from a connected scanner using
[`pyinsane2`](https://github.com/openpaperwork/pyinsane2). Because this package
requires additional system dependencies, it is **not installed by default**.
Run `install/install_scanning_addon.bat` on Windows or
`install/install_scanning_addon.sh` on Linux/macOS to enable scanning. The
front-end automatically hides the *Scan Document* button when scanning support
is missing.

If a compatible scanner is connected after installing the add-on, press the
**Scan Document** button in the web interface to acquire an image directly.
DocCropper relies on WIA on Windows and SANE on Linux/macOS, so ensure the
appropriate drivers are installed for your device.

On Windows the `pyinsane2` installation may fail with a message like
`Microsoft Visual C++ 14.0 or greater is required`. In that case download the
[Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
and install the **Desktop development with C++** workload, then rerun the
installer. A helper script is provided at
`install\install_scanner_tools.bat` which automates this installation on
Windows. After installing the build tools, run the scanning add-on installer
again.

If `pyinsane2` fails to build, you can still use DocCropper without scanning.
The start scripts continue and you may rerun the add-on installer later.

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

The installer resets the installation to match the selected branch,
restoring missing files and cleaning up old ones while preserving your
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

