"""Local scanner helper exposing HTTP endpoints for DocCropper.

This small FastAPI application runs on the client machine and bridges
DocCropper with USB or network scanners available to the operating
system.  The frontend queries this service to list devices and to start
acquisitions.

Run with:

    python scripts/scanner_helper.py

The service listens on http://127.0.0.1:28672 by default and uses the
`pyinsane2` library to access scanners via the SANE (Linux/macOS) or WIA
(Windows) backends.
"""

from __future__ import annotations

import io
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

try:
    import pyinsane2
except Exception:  # pragma: no cover - library missing on CI
    pyinsane2 = None  # type: ignore


app = FastAPI(title="DocCropper Scanner Helper")


def _ensure_pyinsane():
    if pyinsane2 is None:
        raise RuntimeError("pyinsane2 is not installed")


@app.get("/scanners")
def list_scanners() -> dict[str, List[str]]:
    """Return available scanner names."""
    _ensure_pyinsane()
    devices = pyinsane2.get_devices()  # type: ignore[attr-defined]
    names = [d.name for d in devices]
    return {"scanners": names}


@app.post("/scan")
def scan(device: str, resolution: int = 300, mode: str = "Color"):
    """Acquire a single page from *device*.

    The resulting image is returned as PNG bytes.
    """

    _ensure_pyinsane()
    devices = {d.name: d for d in pyinsane2.get_devices()}  # type: ignore
    if device not in devices:
        raise HTTPException(status_code=404, detail="Scanner not found")
    dev = devices[device]
    dev.options["resolution"].value = resolution
    if "mode" in dev.options:
        dev.options["mode"].value = mode

    scan_session = dev.scan(multiple=False)
    try:
        while True:
            scan_session.scan.read()
    except EOFError:
        pass

    image = scan_session.images[0]
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("scripts.scanner_helper:app", host="127.0.0.1", port=28672)

