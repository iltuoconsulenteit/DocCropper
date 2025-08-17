# Configuration Reference

DocCropper uses a JSON file (`settings.json`) and several environment files located in the `env/` directory.  This document summarises the available options and how they interact.

## Environment files
Copy the `*.env.example` files in `env/` to `*.env` and adjust the values.  All `.env` files in this folder are loaded at startup so variables are available to both the backend and the tray helper.

### `license.env`
| Variable | Description |
| --- | --- |
| `DOCROPPER_LICENSE_KEY` | License key for the installation |
| `DOCROPPER_LICENSE_NAME` | Name shown in the interface |
| `DOCROPPER_DEV_LICENSE` | Developer license that unlocks dev‑only plugins |
| `DOCROPPER_DEV_PASSWORD` | Default developer password, change on first access |
| `DOCROPPER_LICENSE_LEVEL` | Feature tier (`free`, `pro`, `full`) |
| `LICENSE_CHECK` | Enable remote license validation |
| `LICENSE_CHECK_URL` | Fabrik list URL used for license checks |
| `DOCROPPER_DEV_WATERMARK` | Overlay DEMO watermark in developer builds |
| `DOCROPPER_TUNNEL` | Enable HTTP tunnelling |
| `DOCROPPER_ENABLE_SIGN` | Turn on local PDF signing plugin |
| `DOCROPPER_ENABLE_MOBILESIGN` | Enable mobile signing plugin |
| `DOCROPPER_ENABLE_REMOTESIGN` | Enable remote signing via external command |
| `DOCROPPER_ENABLE_DOCUSEAL` | Enable DocuSeal signing plugin |
| `DOCROPPER_ENABLE_DOWNLOADPNG` | Enable per-thumbnail PNG download plugin |
| `DOCROPPER_ENABLE_PAGESELECT` | Enable per-page selection for PDF export |
| `DOCROPPER_SIGN_DEV_ONLY` | Restrict local signing to developer licenses |
| `DOCROPPER_MOBILESIGN_DEV_ONLY` | Restrict mobile signing to developer licenses |
| `DOCROPPER_REMOTESIGN_DEV_ONLY` | Restrict remote signing to developer licenses |
| `DOCROPPER_DOCUSEAL_DEV_ONLY` | Restrict DocuSeal signing to developer licenses |
| `DOCROPPER_DOWNLOADPNG_DEV_ONLY` | Restrict PNG download plugin to developer licenses |
| `DOCROPPER_PAGESELECT_DEV_ONLY` | Restrict page-selection plugin to developer licenses |
| `DOCROPPER_REMOVEBG_DEV_ONLY` | Restrict background removal to developer licenses |
| `DOCROPPER_COMPRESSPDF_DEV_ONLY` | Restrict PDF compression to developer licenses |
| `DOCROPPER_WATERMARK_DEV_ONLY` | Restrict watermark plugin to developer licenses |
| `DOCROPPER_CROP_DEV_ONLY` | Restrict cropping plugin to developer licenses |
| `DOCROPPER_SPONSORFRAME_DEV_ONLY` | Restrict sponsor frame plugin to developer licenses |
| `DOCROPPER_LAN_USER_LIMIT` | Maximum concurrent LAN users (0 = unlimited) |
| `DOCROPPER_PUBLIC_URL` | Public base URL when running behind proxies |
| `DOCROPPER_MAX_UPLOAD_MB` | Maximum upload size per file in megabytes |

### `auth.env`
| Variable | Description |
| --- | --- |
| `SECRET_KEY` | JWT secret for the authentication service |
| `DATABASE_URL` | Database connection string |
| `DOCROPPER_ADMIN_EMAIL` | Initial admin account email |
| `DOCROPPER_ADMIN_PASSWORD` | Initial admin account password |

### `docuseal.env`
| Variable | Description |
| --- | --- |
| `DOCUSEAL_API_URL` | Endpoint for DocuSeal remote signing |
| `DOCUSEAL_API_KEY` | API key for DocuSeal |

### `google.env`
| Variable | Description |
| --- | --- |
| `DOCROPPER_GOOGLE_CLIENT_ID` | Google OAuth client ID |

### `signing.env`
| Variable | Description |
| --- | --- |
| `DOCROPPER_SIGN_CERT` | Path to local signing certificate |
| `DOCROPPER_SIGN_PASSWORD` | Password for the certificate |
| `DOCROPPER_REMOTE_SIGN_CMD` | External command used for remote signing |

### `stripe.env`
| Variable | Description |
| --- | --- |
| `STRIPE_SECRET_KEY` | Stripe secret key |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key |
| `STRIPE_PRICE_PRO` | Stripe price ID for the Pro tier |
| `STRIPE_PRICE_FULL` | Stripe price ID for the Full tier |
| `STRIPE_SUCCESS_URL` | Redirect URL after a successful payment |
| `STRIPE_CANCEL_URL` | Redirect URL when payment is cancelled |

## `settings.json`
`settings.json` defines default values for the application.  Many of these values can be overridden by the environment variables above (e.g. `DOCROPPER_MAX_UPLOAD_MB` overrides `max_upload_mb`).

### General
- `language` – default interface language (`it` or `en`)
- `template` – UI template (`expressive` or `classic`)
- `layout`, `orientation`, `arrangement`, `scale_mode`, `scale_percent`
- `port` – HTTP port for the main server

### Branding and sponsor
- `brand_html` – HTML snippet shown in the header
- `client_logo`, `sponsor_logo` – logo filenames under `static/logos/`
- `client_url`, `sponsor_url` – links applied to the logos
- `sponsor_banner` – image file displayed above the gallery
- `sponsor_plugin` – `facebook`, `instagram`, `landing`, `banner`, `slide`, or blank
- `sponsor_frame` – URL used when the plugin mode is `landing`
- `sponsor_frame_width`, `sponsor_frame_height` – iframe dimensions
- `sponsor_thumb_width`, `sponsor_thumb_height` – thumbnail size in the gallery
- `sponsor_slides` – list of rotating images for the sponsor slot
- `sponsor_facebook_page`, `sponsor_instagram_profile` – profiles used for social plugins
- `banner_images` – array of header slide filenames, `{{lang}}` is replaced with the current language
- `banner_interval` – rotation interval for banner images (milliseconds)

### Upload and processing limits
- `max_upload_files` – maximum files per upload batch
- `max_upload_mb` – maximum size per file
- `blank_threshold` – percentage used to detect blank pages
- `skip_blank` – remove blank pages on import

### License and plugin flags
- `license_level` – installation tier (`free`, `pro`, `full`)
- `license_check` – enable remote license validation
- `enable_sign`, `enable_mobilesign`, `enable_removebg`, `enable_compresspdf`, `enable_watermark`, `enable_pageselect`
- `crop_dev_only`, `sign_dev_only`, `mobilesign_dev_only`, `removebg_dev_only`, `compresspdf_dev_only`, `watermark_dev_only`, `pageselect_dev_only`, `sponsorframe_dev_only`, `login_dev_only`
- Plugin-specific flags like `enable_remotesign`, `remotesign_dev_only`, `enable_docuseal`, and `docuseal_dev_only` are stored in the respective `plugins/<name>/settings.json` files
- `lan_user_limit` – cap for LAN user plugin

### Updates
- `update_pin` – PIN required to run updates from the UI
- `update_interval` – interval between automatic update checks (milliseconds)

User preferences are stored per account in the `users/` folder.  If a setting is defined in both the environment and `settings.json`, the environment variable takes precedence.
