# License Utilities

This folder collects helper scripts for creating and installing DocCropper licenses.

## Generate a signed license file
Use `generate_license_file.py` to create a signed token (default extension `.dcl`) that can be imported from the web UI:

```bash
python generate_license_file.py \
  --type developer \
  --name "Your Name" \
  --expires 1735689600 \
  --plugins scan \
  --domains example.com \
  --out license.dcl
```

Upload the generated file from **Licenses → Import** in the DocCropper interface. The server verifies the signature and stores the token in `env/license.env`.

## Configure a manual license
Run the platform script `setup_license` (`.sh`, `.bat`, or `.command`) to interactively supply a key and licensee name:

```bash
./setup_license.sh
```

The script writes the values to `env/license.env`, updates `settings.json`, and disables remote checks so the license becomes active on restart.

## Seed test licenses
`seed_licenses.py` populates the database with sample licenses for development or automated tests.
