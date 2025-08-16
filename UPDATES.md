# Updates

## 2025-08-18
- Exposed project updates in-app via a `/updates` endpoint and showed the latest entry on the home screen.

## 2025-08-17
- Added an "Apply & Add" option after cropping in camera mode to quickly capture another photo.

## 2025-08-16
- Removed the `multiple` attribute from the hidden camera input so cropped photos from mobile devices import correctly.

## 2025-08-15
- Expressive template loads banner slide names from the `banner_images` list in `settings.json`.
- Slide rotation is skipped when no slides are configured.
- Default `banner_images` list includes all provided slides.

## 2025-08-14
- Added per-page watermark tool with draggable overlays and a watermark button in the Expressive template.
- Introduced PDF/A export plugin and camera margin controls.
- Added legal disclaimers to signing and watermark tools.
- Fixed watermark application, centering, and export sidebar layout.

## 2025-08-12
- Released Expressive UI template with Tailwind, selectable templates, and improved previews.
- Restored perspective cropping with auto corner detection, draggable handles, and brightness/contrast controls.
- Integrated mobile signing plugin and exposed sign modal hook.
- Routed sign commands through the adapter and used prebuilt Tailwind CSS.

## 2025-08-07
- Made sponsor video optional.
- Allowed PDF export without license check.

## 2025-07-31
- Added LAN user limit plugin and created a default admin via FastAPI Users.
- Improved Docker setup and environment examples.

## 2025-07-30
- Implemented remote license verification and admin interface.
- Added Docker deployment files and refined branding layout.

## 2025-07-29
- Enhanced signing interface, banner layout, and legal disclaimers.

