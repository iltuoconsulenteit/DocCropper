# License Scripts

This folder contains utilities for creating license files used by DocCropper.

## `generate_license_file.py`

Generate a JSON license file containing the license key and a token bound to a
machine fingerprint.

### Usage

```bash
python generate_license_file.py --key ABC123 --output license.json [--fingerprint MACHINE_ID]
```

- `--key`: license key to embed in the file.
- `--output`: destination path for the JSON license file.
- `--fingerprint`: optional identifier of the machine. When omitted the
  produced token is valid on **any** machine.

### Risks

Omitting the fingerprint makes the token reusable on multiple machines. This is
useful for demo or evaluation licenses but increases the risk of unauthorized
redistribution. Use this option only when the wider validity is desired and
consider the security implications.

