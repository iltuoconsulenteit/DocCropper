#!/usr/bin/env python3
"""Print the machine fingerprint used to bind license files."""

import hashlib
import uuid


def main() -> None:
    node = uuid.getnode()
    print(hashlib.sha256(str(node).encode()).hexdigest())


if __name__ == "__main__":
    main()
