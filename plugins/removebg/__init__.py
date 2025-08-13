import base64
import io
import logging
from typing import Any

from fastapi import UploadFile, File, Query
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
    async def remove_background(
        image_file: UploadFile = File(...),
        threshold: int = Query(50, ge=0, le=100),
    ):
        try:
            contents = await image_file.read()
            input_image = Image.open(io.BytesIO(contents))
            t = max(0, min(100, threshold))
            output = remove(
                input_image,
                alpha_matting=True,
                alpha_matting_foreground_threshold=int(t * 255 / 100),
            )
            buf = io.BytesIO()
            output.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            return {"image": b64}
        except Exception:
            logger.exception("Background removal failed")
            return JSONResponse(status_code=500, content={"message": "Background removal failed"})
