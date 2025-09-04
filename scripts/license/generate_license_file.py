import argparse
import hashlib
import json
from pathlib import Path


def generate_token(key: str, fingerprint: str | None) -> str:
    """Create a deterministic token for the given key and fingerprint.

    When no fingerprint is provided, the returned token is valid on
    any machine because it does not include any machine specific data.
    """
    base = f"{key}:{fingerprint}" if fingerprint else f"{key}:ANY"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a license file")
    parser.add_argument("--key", required=True, help="License key")
    parser.add_argument(
        "--output",
        required=True,
        help="Destination path for the generated license file",
    )
    parser.add_argument(
        "--fingerprint",
        help="Machine fingerprint. If omitted the token will be valid on any machine.",
    )
    args = parser.parse_args()

    token = generate_token(args.key, args.fingerprint)
    license_data = {
        "license_key": args.key,
        "token": token,
        "fingerprint": args.fingerprint,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(license_data, fh)
    print(f"License file generated at {output_path}")

    if args.fingerprint is None:
        print(
            "Warning: no fingerprint provided; generated token is valid on any machine.",
        )


if __name__ == "__main__":
    main()
