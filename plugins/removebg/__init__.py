import base64
import io
import logging
from typing import Any

from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image

try:
    from rembg import remove
except Exception:  # pragma: no cover
    remove = None

__all__ = ["register"]

logger = logging.getLogger(__name__)


def register(app, utils: dict[str, Any]):
    if remove is None:
        logger.warning("rembg not installed; remove background endpoint disabled")
        return

    @app.post("/remove-background/")
    async def remove_background(image_file: UploadFile = File(...)):
        try:
            contents = await image_file.read()
            input_image = Image.open(io.BytesIO(contents))
            output = remove(input_image)
            buf = io.BytesIO()
            output.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            return {"image": b64}
        except Exception:
            logger.exception("Background removal failed")
            return JSONResponse(status_code=500, content={"message": "Background removal failed"})
