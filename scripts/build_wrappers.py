import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Legacy wrapper compilation has been retired. This helper now "
            "only logs the skip so older scripts return success without "
            "attempting to build DocCropper.exe launchers."
        )
    )
    parser.add_argument(
        "python_dir",
        nargs="?",
        help="Ignored legacy argument retained for backwards compatibility.",
    )
    parser.parse_args(argv)
    print("Wrapper compilation disabled; skipping DocCropper.exe build.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
