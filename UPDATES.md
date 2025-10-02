# Updates

## 2025-09-15
- Route mobile signing endpoints through FastAPI so shared links no longer 404
- Route `/wiki` requests to the FastAPI app so built-in help pages load correctly
- Skip unnecessary Windows dependency reinstalls by tracking `requirements.txt` hash
- Embed wiki documentation inside the app via an iframe and serve it from absolute paths to avoid 500 errors
- Forward `/settings` requests to FastAPI so the settings panel accepts the correct password
- Serve wiki pages via a dedicated `StaticFiles` mount to prevent internal server errors
- Ask whether to reinstall Python dependencies or skip existing packages during startup
- Remove unsupported header call in `NoCacheStaticFiles` that caused wiki 500 errors
- Permit `/settings-login/` to accept the default password when no hash is set
- Redirect `/sign` URLs through Django to FastAPI so mobile signing links resolve correctly

## 2025-09-09
- Precompile Windows launcher wrappers during installation so first start doesn't fall back to PowerShell `Add-Type`
- Capture tray icon launch output in installer logs to help diagnose startup failures
- Append tray helper logs to installer log when startup fails
- Record detected Python interpreter paths in `env/python_path.env` and have start/stop scripts use them to launch the app and tray reliably
- Warn when local repository differs from origin and log any leftover files after updates
- Prevent duplicate tray launches and split PowerShell output/error logs so the Windows installer can start the tray helper only once without redirection conflicts
- When launching immediately after installation, read persisted Python paths so the tray icon starts even if in-memory variables are cleared
- Standardize installer prompts to English with default confirmations
- Clean unused objects when compressing PDFs so selected levels produce distinct file sizes
- Append the chosen compression level to downloaded PDF filenames
- Return suggested PDF filename with compression suffix so downloads match selected quality
- Compile Windows wrappers with `csc.exe` to avoid PowerShell quoting issues
- Stop script now also terminates `DocCropper.exe` and `DocCropperTray.exe` processes during upgrades
- Fix PDF compression plugin to use supported save options so chosen levels and filenames take effect
- Recompress PDF images based on the selected level for clearer file size differences
- Adapter downloads now honor the suggested filename so compression suffixes appear in saved PDFs
- Enable PDF compression in the Free edition and enforce watermark overlays for Free licenses
- Build Windows wrappers via a Python helper that invokes `csc.exe`, removing reliance on PowerShell `Add-Type`

## 2025-09-08
- Fix Windows installer halting after Python version check by consolidating runtime detection into a dedicated function
- Correct Python path detection when reusing an existing interpreter so `pywin32` post-installation runs and the tray icon launches
- Windows installer now downloads and installs Python if missing, defaults to developer branch, and auto-confirms updates and tray launch, and detects the installed Python path for virtual environment creation
- When no system Python is found, the Windows installer bootstraps the embeddable Python runtime and pip automatically
- Move purchase, bug, and support links from the header to the sidebar navigation
- Replace sidebar command menu with home-screen buttons for export and mobile signing
- Licenses can be activated by uploading a signed token file from the web UI
- Added `scripts/license/generate_license_file.py` helper to create signed license files with `LICENSE_SECRET`
- Uninstall scripts now back up `settings.json` and `env/license.env` to a `DocCropperBackup` folder under the current user before removing the installation
- Installers restore these files on setup so licenses and preferences persist across clean reinstallations
- Enable moving any form field type, including on touch devices
- Add signature modal with double-click placement and preview integration
- Guard against future dates in this log with an automated test
- Fix Windows installer exit during cleanup by running PowerShell cache removal on a single line
- Installer reads `env/python.env` to choose the Python version to download
- Fix embeddable Python download path to ensure installer retrieves runtime even when the TEMP folder is missing
- Skip `pyinsane2` on Windows to avoid build-tool errors; scanning requires manual setup
- Preserve existing embeddable Python runtime across updates and skip download when the required version is already installed
- Always fetch repository updates so incomplete installations don't skip new commits
- Install `pywin32` on Windows and put the bundled Python directory on `PATH` so the tray icon and server start reliably
- Run `pywin32_postinstall.py` and add the `Scripts` directory to `PATH` so the tray helper can load Win32 modules

## 2025-09-07
- On Windows, compile lightweight wrappers so Task Manager lists `DocCropper.exe` and `DocCropperTray.exe` instead of generic Python names
- Fix PDF compression levels by applying JPEG quality settings so file size reflects chosen compression

## 2025-09-06
- Add client-side scanner helper with FastAPI and wire the scan plugin to enumerate devices and trigger acquisitions through `http://127.0.0.1:28672`
- Restore watermark overlay on exported PDFs for Free and Demo editions

## 2025-09-05
- Licenses panel can now persist manual keys to `env/license.env` and refresh the server so the frontend reflects the new license immediately
- Convert images to JPEG during PDF compression so selected levels actually reduce file size

## 2025-09-04
- Add cross-platform uninstallation scripts that stop running instances and remove the installation directory even when files are locked
- Allow purchasing licenses directly from the license panel with a Stripe checkout flow

## 2025-08-19
- Enable DocuSeal and remote signing plugins by default so developer licenses reveal them immediately
- Add a Settings button for developer builds and wire it into the Expressive template

## 2025-08-18
- Expose `active_plugins` in settings so the frontend shows developer-only tools when licensed and hides disabled plugins automatically

## 2025-02-14
- Downscale large images before corner detection for faster cropping

## 2025-08-22
- Optimize perspective crop responsiveness by preloading OpenCV and using a lighter interpolation mode

## 2025-08-21
- Secure general settings behind `DOCROPPER_SETTINGS_PASSWORD` (default `12345678`) and expose a developer settings menu requiring the developer password; developer licenses now always load in-progress plugins

## 2025-08-20
- Treat "developer" license level as dev key so in-progress plugins like page select are visible to dev installs
- Center layout toggle icon and equalize action button heights across the gallery controls
- Replace watermark emoji with stamp icon and move watermark settings into a dedicated plugin config
- Adjust thumbnail checkbox so developer builds show the selection dot
- Add experimental image editor plugin with saturation and sharpness controls

## 2025-08-19
- Allow selecting individual thumbnails for partial PDF export, automatically choosing all pages when none are selected

## 2025-08-18
- Convert Google login into a plugin guarded by `login_dev_only` so authentication is available only on developer builds

## 2025-08-17
- Move Add/Import button to the start of the controls, show a + icon with tooltip, and fix its import action on mobile and desktop
- Default sponsor frame embeds latest Facebook post and sponsored licenses require internet connectivity

## 2025-08-16
- Show sponsor frame as persistent gallery preview that trails user images and is skipped during export
- Add script to generate updates log from git history
- Serve UPDATES.md, gate login behind license check, add update bell, optimize startup, restore Linux tray icon, polish Sponsor page, and add rollback option

## 2025-08-15
- Add slide slogan
- chore: mark PNG slides as binary

## 2025-08-14
- feat: load slides from dedicated folder and align language with path
- Fix watermark application and centering
- feat: draggable watermark overlays
- Add legal disclaimers to signing and watermark tools
- fix: offset export sidebar below header
- Add watermark button to Expressive template
- feat: add per-page watermark tool
- Refactor export panel into collapsible sidebar
- Fix sidebar hiding on desktop
- Add PDF/A export plugin
- Improve corner detection and allow multiple camera shots
- Add camera margin controls and PDF/A export option

## 2025-08-12
- Use prebuilt Tailwind CSS
- Route sign command through adapter
- feat: expose sign modal hook
- Integrate mobile sign plugin with expressive template
- chore: add debug logs for double-click events
- fix: connect sign flow and prompt upload
- fix: adjust sidebar and preview controls
- refactor sign modal layout and enlarge preview controls
- fix: adjust crop and sign UI
- style: reorganize thumbnail controls and enlarge previews
- feat: add signature bg removal and fix placement
- feat: add draggable multi-signature modal
- feat: improve crop quality and signing
- fix: expand crop handles and compact controls
- fix: show all crop handles and live filter
- feat: add brightness and contrast controls
- fix: ensure draggable corner handles for perspective crop
- refactor: move crop endpoints to plugin
- feat: auto-detect crop corners
- fix: restore four-point crop handles
- feat: display license details in expressive template

## 2025-08-11
- encrypt uploaded files
- feat: restore perspective cropping
- fix: show version info in expressive template
- fix: load images as data URLs for perspective crop
- feat: add perspective crop and image preview
- feat: arrange preview controls and enable sorting
- feat: enhance expressive template previews
- feat: preview imported pages and hide slides
- refactor: improve adapter event handling
- feat: preview imports and reposition pin icon
- feat: wire adapter commands to legacy UI
- feat: make drawer toggleable and reorder commands
- refactor: tune expressive template
- feat: enhance expressive template with branding and i18n
- feat: extend adapter and expressive template
- fix: make expressive drawer collapsible and improve adapter
- feat: add logos and menu-based commands
- fix: restore expressive template and improve fetch script
- chore: add script to fetch template
- fix: honor template setting with fallback
- feat: make expressive template selectable
- feat: add Tailwind expressive template
- style: use material dashboard layout
- refactor: remove joomla module and add template
- feat: add expressive UI and adapter

## 2025-08-07
- fix: allow PDF export without license check
- feat: make sponsor video optional

## 2025-08-01
- Reset file input after add and add mobile layout

## 2025-07-31
- Improve branding layout and clarify dev install
- Fix PayPal link and adjust sponsor banner
- Show donation modal
- Fix database access with async session
- Fix FastAPI Users registration
- Fix FastAPI Users setup and create default admin
- Fix User model primary key
- Fix Windows start script dependency install and set user table name
- Add aiosqlite dependency
- Lock settings via license
- Add LAN user limit plugin and clarify license tiers
- Improve Docker setup
- Refine env examples and docs
- Improve Docker setup
- Translate Fabrik license section
- Protect admin page

## 2025-07-30
- Add admin page for settings and user management
- Add Docker deployment files
- Ensure auth env copied on install and start
- Refine licensing check and env setup
- Add license token validation
- Add FastAPI Users auth and remote license middleware
- Add remote license verification
- Align brand logos and update README
- Adjust banner logos
- Refine brand banner layout
- Set default client and sponsor logos
- Move banner and logos below header
- Fix header logo margin
- Load signature info page from template
- Add signature info page to signed PDFs
- Restore angled orientation for sign button
- Fix header layout for branding
- style: add top margin to header logo

## 2025-07-29
- fix mobile signature double tap
- Fix mobile sign double tap and dropdown
- Improve mobile sign double-tap
- Fix double-tap signing and page menu
- Add detailed legal notice for Mobile Sign
- Enable double-tap signing
- Add signature info page and fix PDF font
- Style fixes for sign details modal
- Fix sign button style and use link-based sharing
- Add legal log and email options for MobileSign
- Add consent info to PDF and improve signed PDF sharing
- Fix signed PDF link and client sharing
- Add server link for signed PDF and fix modal
- Add modal for mobile sign details
- Add PDF return and contact defaults
- Handle WhatsApp share and log page
- Add consent fields to mobile signing
- Add Slogan, client and sponsor logo
- Add signature scale targeting and tweak banner
- Refine signing UI and banner layout
- Add legal disclaimer display
- Improve demo notice spacing and pen button
- Tweak header and footer visuals
- Move demo notice into header and add page sign button
- Add material shadow, reduce banner size and adjust thumbnails
- Restore button colors and adjust layout controls
- Hide Google login in demo mode and apply Material styling
- Reposition edit buttons and add blank-page controls
- Fix layout preview and space thumbnails
- Refine thumbnail buttons layout
- docs: update instructions and layout preview
- Improve thumbnail controls
- Fix image cropping workflow
- Show thumbnails for uploaded images

## 2025-07-28
- Fix image preview reset
- Add GitHub Sponsors configuration
- Fix color restore
- fix image preview not refreshing
- Fix image preview ordering and enhance sponsor modal
- Add cache busting version parameter
- Disable caching for proxy
- Show build date
- Add sponsor video modal and fix image processing UI
- Hide settings in demo mode
- Improve demo messaging and add upload size limit
- Refresh on header click and add footer link
- Remove Fly.io workflow and add mobile sign scaling
- Use app logo as favicon
- Set header logo as webpage icon
- Encrypt uploads and show donate button for demo
- Add donation button for demo full
- Remove duplicate mobile sign buttons
- show loading while generating mobile sign link
- Separate mobile sign UI
- Add public URL setting and demo defaults
- Improve mobile sign base URL handling
- Support tunnels with dynamic URLs and CORS
- Trust proxy headers for QR links
- Use base URL for mobile sign link

## 2025-07-27
- Allow marking signature spots for mobile signing
- Refine desktop signing workflow and enable mobile sign for dev
- Add plugin toggles and standalone mobile sign
- Split signature features into separate plugins
- Ensure mobile signing dropdown lists all pages
- Add global sign button
- Send all pages for mobile signing
- Improve mobile signing page

## 2025-07-26
- Update Windows installer
- Update installer default branch
- Update installer default branch
- Update installers to default to work branch
- Add structured env examples
- Add Stripe checkout integration
- Add license-dependent settings menu
- Add license input form
- Keep preview after finishing mobile signing
- Handle multiple mobile signatures and share QR link
- Fix mobile tap for signature and add desktop dblclick
- Allow multiple mobile signatures with preview
- Fix QR code generation by sharing processedImages
- Improve mobile signing flow
- Improve mobile sign page with logos and consent
- Add Docuseal remote signing
- Style signature and export controls
- Move QR sign display into signature panel
- Move signature endpoints to plugin
- Refactor signature controls and plugin
- Add mobile sign button in signature panel
- Fix PID checks in Windows start script
- Write tray PID and check in start scripts
- Fix tray loop in start scripts
- Update default port and add mobile sign button
- Update default branch in installer scripts
- Log tray auto-start

## 2025-07-22
- Add logo and images
- Make instructions toggleable and add mobile camera fallback
- Improve tray status check
- Make scanner addon optional
- Add input source options for upload, scanner, and camera
- Add OCR feature with language support
- Add optional PDF signing

## 2025-08-16
- Scale sponsor frame and show it on startup without importing files
- Restore loading overlay for the Expressive template so imports show progress

## 2025-08-17
- Embed sponsor frame as a gallery thumbnail and add settings for frame and preview dimensions

## 2025-08-18
- Keep the sponsor preview visible on startup in the Expressive template and restyle gallery controls with colored icons for import, blank-page removal, clearing images, and layout toggling

## 2025-08-19
- Delete session folders immediately after clearing the gallery to remove residual data
- Reduce default upload limit to 5&nbsp;MB per file and make it configurable via `max_upload_mb`
- Remove debug console logs to avoid leaking sensitive information

## 2025-08-20
- Add plugin-based sponsor slot that adapts to license settings (Facebook, Instagram, landing page, banner, slide or image) and can be disabled when no advertising is desired

## 2025-08-21
- Introduce developer-only flags for plugins so new modules stay hidden unless a developer license is used

## 2025-08-22
- Secure developer settings with a default `DOCROPPER_DEV_PASSWORD` (87654321) and add API endpoints to force a password change before use

## 2025-08-23
- Separate Docuseal and remote command signing into individual dev-only plugins and move their settings into `plugins/` directories

## 2025-08-24
- Add dev-only plugin that lets users download individual thumbnails as transparent PNG files


## 2025-08-25
- Group grayscale, black/white, and color thumbnail toggles into a pluggable color-mode module with enable and developer-only flags

## 2025-08-26
- Allow embedded help pages by removing X-Frame-Options from static wiki responses

## 2025-08-27
- Preserve `env/license.env` during repository updates so manual licenses survive upgrades
- Add `/license/status` endpoint and frontend refresh to confirm the active license

## 2025-08-28
- Log PDF downloads with details on applied plugins like compression and PDF/A without exposing sensitive data

## 2025-08-29
- Write DocCropper logs to the system temporary directory for easier troubleshooting

## 2025-08-30
- Log active plugins on startup and note when compression was requested without an available plugin

## 2025-08-31
- Load the standard library's `platform` module by searching `python*.zip` archives so embeddable Windows installs start correctly
- Tray launcher now locates `platform` from zipped stdlib archives, preventing startup failures

## 2025-09-13
- Installer and startup scripts call the Python wrapper builder via absolute paths so Windows launchers compile without PowerShell
- Fallback to the PowerShell wrapper builder when the Python helper is missing, ensuring upgrades from older releases still compile launchers
## 2025-09-13
- Removed legacy PowerShell wrapper builder that used `Add-Type`; Python-based builder now compiles launchers exclusively
## 2025-09-13
- Installer and startup scripts delete leftover PowerShell wrapper builders and force-reinstall Python dependencies to avoid
  partial upgrades
- Startup script now skips wrapper compilation and runs directly with `python.exe`/`pythonw.exe` so Windows launches succeed even without `DocCropper.exe`

## 2025-09-13
- Locate the stdlib `platform` module by temporarily adding any `python*.zip` archives to `sys.path`, ensuring embeddable
  Windows builds import it without error
- Reintroduce a lightweight PowerShell wrapper that delegates to the Python builder so legacy launchers no longer fail with
  `Add-Type` compilation errors

## 2025-09-13
- Added an API endpoint that streams wiki pages as HTML with no-cache headers so help content can be embedded safely inside the UI
- Replaced iframe-based wiki embeds in both interfaces with dynamic loaders that fetch from the new endpoint and handle in-app navigation

## 2025-09-13
- Route `/wiki` through Django to serve bundled help pages without 500 errors when FastAPI is bypassed

## 2025-09-13
- Store the settings panel password in plain text alongside its hash so the default `12345678` works reliably and can be changed without bcrypt issues
- Ask once before installing Windows dependencies, letting admins skip, update missing packages, or force a full reinstall during startup and upgrades
- Fall back to a maintained Python embeddable version when downloads fail and validate the configured version before attempting installation

## 2025-09-14
- Startup and installer scripts now leave matching Python packages untouched so upgrades only reinstall dependencies when explicitly requested
- Windows installer detects the operating system architecture before downloading the embeddable Python runtime, preventing 404 errors on 32-bit or ARM64 hosts
- Store dependency hashes under the user profile (or `%TEMP%`) so Windows upgrades can skip reinstalling packages even when `Program Files` is read-only

## 2025-09-18
- Windows installer skips compiling obsolete launcher wrappers and removes the legacy PowerShell builder, preventing `Add-Type` errors during upgrades
- Stubbed the legacy wrapper scripts so historical start/installer batches simply log the skip instead of invoking `Add-Type`

## 2025-10-02
- Added a dedicated `launch_app.py` helper so the Windows start script spawns DocCropper via Python, appends logs, and records the server PID before reporting success
- Hardened the dependency checker to fall back to a simplified parser when `packaging` is unavailable, preventing unnecessary reinstalls while still catching missing packages
