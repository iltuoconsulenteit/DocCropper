#!/usr/bin/env python3
"""Generate a signed DocCropper license token file.

Usage:
  python scripts/generate_license_file.py --type developer --name "Your Name" --out license.dcl

The script reads the LICENSE_SECRET environment variable to sign the token.
"""

import argparse
import json
import os
import time
from jose import jwt


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a signed license file")
    parser.add_argument("--type", dest="license_type", required=True,
                        help="License type, e.g. demo-full, developer")
    parser.add_argument("--name", dest="license_name", default="Manual License",
                        help="Name of the license holder")
    parser.add_argument("--expires", type=int, default=int(time.time()) + 365*24*3600,
                        help="Expiration time as UNIX timestamp (default: one year)")
    parser.add_argument("--plugins", default="",
                        help="Comma-separated list of enabled plugins")
    parser.add_argument("--domains", default="",
                        help="Comma-separated list of allowed domains")
    parser.add_argument("--out", default="license.dcl",
                        help="Output file path")
    args = parser.parse_args()

    secret = os.environ.get("LICENSE_SECRET", "change-me")
    payload = {
        "license_type": args.license_type,
        "license_name": args.license_name,
        "expires_at": args.expires,
        "plugins": [p for p in args.plugins.split(',') if p],
    }
    if args.domains:
        payload["allowed_domains"] = [d.strip() for d in args.domains.split(',') if d.strip()]

    token = jwt.encode(payload, secret, algorithm="HS256")
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(token)
    print(f"License written to {args.out}")


if __name__ == "__main__":
    main()
