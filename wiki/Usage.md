# Usage

After installation, start DocCropper using the tray helper or the start script.

## Tray Helper

Launch `doccropper_tray.py` (or use the shortcut created by the installer). The tray icon indicates whether the server is running:

- **Green** dot: DocCropper is active
- **Red** dot: DocCropper is stopped

Right-click the icon to start, stop, or update the application.

## Manual Start

You can also run the start scripts in the `scripts/` folder directly.

Open a web browser and navigate to `http://localhost:8000` by default. Upload your document images, adjust the corners, and export the final PDF.
Use the **Brightness** and **Contrast** sliders to improve the image before pressing **Process Image**.

## Scanning

Click **Scan Document** in the interface to acquire an image from a connected scanner.
This uses `pyinsane2` with WIA on Windows or SANE on Linux/macOS, so ensure your
scanner drivers are installed.
