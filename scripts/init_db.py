#!/usr/bin/env python
"""Initialize the DocCropper database."""

import asyncio
import sys
from pathlib import Path

# Ensure repository root is on the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.auth.database import init_db


def main() -> None:
    asyncio.run(init_db())


if __name__ == "__main__":
    main()
