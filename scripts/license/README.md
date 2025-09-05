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
  --fingerprint <machine-fingerprint> \
  --out license.dcl
```

Upload the generated file from **Licenses → Import** in the DocCropper interface. The server verifies the signature and stores the token in `env/license.env`.

To obtain the `machine-fingerprint` value on a target system, run:

```bash
python get_fingerprint.py
```

The output is a hash tied to the current machine; including it when generating a license ensures the resulting file only activates on that system.

## Seed test licenses
`seed_licenses.py` populates the database with sample licenses for development or automated tests.
