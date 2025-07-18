# Installation

DocCropper can run on Windows, macOS, and Linux. The recommended approach is to use the provided installer scripts which will clone the repository, set up the Python environment, and optionally configure your license key. If Git is not installed, the scripts attempt to install it using your system package manager (winget, apt, yum or brew).

## Windows

Run:

```cmd
install\install_DocCropper.bat
```

## Linux/macOS

Run:

```bash
bash install/install_DocCropper.sh
```

The installer logs its progress to a file in your temporary folder so you can inspect it later.

### Scanner Support

To use the optional scanning feature you need a working scanner driver.
On Windows DocCropper relies on WIA, while on Linux/macOS it uses SANE.
Make sure your device is configured properly before launching the application.

