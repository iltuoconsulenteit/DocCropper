# Updates

## 2024-09-06
- Removed empty sponsor tier list, added placeholder pricing row, and positioned the contact button below the table.

## 2024-09-05
- Polished the Sponsor page with medal icons, a pricing row, and a highlighted menu link, removing placeholder text and ensuring the contact button sits below the table.
- Clarified documentation that internet access is needed only to activate and renew the license.

## 2024-09-04
- Installer launches the tray helper only after an explicit yes, preventing auto-starts during setup.
- Start and stop scripts terminate running instances via PID files to avoid plugin warnings during shutdown.

## 2024-09-03
- Added a benefits table to the Sponsor page to preview perks for Bronze, Silver, and Gold tiers.

## 2024-09-01
- Integrated the Sponsor page into the main templates with in-app cards for Bronze, Silver, and Gold tiers.

## 2024-09-02
- Defaulted the Linux tray helper to `:0` when `$DISPLAY` is missing so the tray icon starts even when launched via `sudo`.
- Replaced the update PIN prompt with a styled in-app panel/modal for a consistent look across templates.

## 2024-08-31
- Debounced Linux tray clicks to stop repeated browser launches and ensure the tray icon appears.
- Added network timeouts and a one-time retry for update checks so offline installs start quickly.
- Moved the update bell to the far right of the UI for clearer visibility.

## 2024-08-30
- Added update notification bell that checks for new versions on a schedule and lets licensed users trigger upgrades with a PIN.

## 2024-08-29
- Added Sponsor menu and page listing Fabrik-based sponsorship tiers.

## 2024-08-28
- Homepage now shows an optional sponsor banner and client/sponsor logos link to URLs supplied by license settings.

## 2024-08-27
- Login module only activates when license checking is enabled, preventing unprotected enterprise use.

## 2024-08-26
- Linux tray icon now shows its command menu by handling icon clicks through the run loop.

## 2024-08-25
- Export sidebar now leaves room for the footer so client logos remain visible.

## 2024-08-24
- Fixed mobile crop Apply button throwing a MutationObserver error after removing camera input's `multiple` attribute.

## 2024-08-23
- Replaced deprecated startup event with FastAPI lifespan manager to eliminate console warnings.
- Stop script now uses non-interactive `sudo -n` so tray-driven shutdowns don't hang on password prompts.

## 2024-08-22
- Linux tray icon now responds on Linux with left and right clicks and tries `xdg-open` if the default browser fails.
- Stop script attempts to use `sudo` so the tray's Stop command works when elevated privileges are required.

## 2024-08-21
- Linux tray icon now triggers menu commands and left-click opens the app just like on Windows.

## 2024-08-20
- Captured photos now drop directly into the gallery and the interface switches back to the classic upload view.
- Added an **Add/Import** button alongside page cleanup tools to quickly bring in more images.

## 2024-08-19
- Reverted the "Apply & Add" camera workflow; mobile devices now use the standard Import button to add additional photos.

## 2024-08-18
- Exposed project updates in-app via a `/updates` endpoint and showed the latest entry on the home screen.

## 2024-08-17
- Added an "Apply & Add" option after cropping in camera mode to quickly capture another photo.

## 2024-08-16
- Removed the `multiple` attribute from the hidden camera input so cropped photos from mobile devices import correctly.
- Added full Docker compose with Node OAuth service for enterprise deployments.

## 2024-08-15
- Expressive template loads banner slide names from the `banner_images` list in `settings.json`.
- Slide rotation is skipped when no slides are configured.
- Default `banner_images` list includes all provided slides.

## 2024-08-14
- Added per-page watermark tool with draggable overlays and a watermark button in the Expressive template.
- Introduced PDF/A export plugin and camera margin controls.
- Added legal disclaimers to signing and watermark tools.
- Fixed watermark application, centering, and export sidebar layout.

## 2024-08-12
- Released Expressive UI template with Tailwind, selectable templates, and improved previews.
- Restored perspective cropping with auto corner detection, draggable handles, and brightness/contrast controls.
- Integrated mobile signing plugin and exposed sign modal hook.
- Routed sign commands through the adapter and used prebuilt Tailwind CSS.

## 2024-08-07
- Made sponsor video optional.
- Allowed PDF export without license check.

## 2024-08-08
- Deferred heavy libraries like OpenCV and PyMuPDF until needed, trimming memory use and speeding startup.
- Skipped redundant `pip install` runs and launched the tray after dependencies load, restoring the Linux tray icon.

## 2024-08-09
- Added medal icons and color‑coded cards to the Sponsor page and replaced the old support row with marketing and license benefits.
- Moved the sponsorship disclaimer below the contact button so it no longer hides behind the link.

## 2024-07-31
- Added LAN user limit plugin and created a default admin via FastAPI Users.
- Improved Docker setup and environment examples.

## 2024-07-30
- Implemented remote license verification and admin interface.
- Added Docker deployment files and refined branding layout.

## 2024-07-29
- Enhanced signing interface, banner layout, and legal disclaimers.

