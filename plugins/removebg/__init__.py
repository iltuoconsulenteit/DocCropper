import base64
import io
import logging
from typing import Any

from fastapi import UploadFile, File, Query
from fastapi.responses import JSONResponse
from PIL import Image

try:  # Prefer the rembg library when available
    from rembg import remove  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    remove = None

__all__ = ["register"]

logger = logging.getLogger(__name__)


def _fallback_remove(img: Image.Image, threshold: int) -> Image.Image:
    """Basic background removal when rembg isn't installed.

    It converts the image to grayscale and uses the threshold value to build an
    alpha mask.  This is obviously much simpler than rembg but avoids 404 errors
    when the optional dependency is missing.
    """

    import numpy as np  # lazy import
    import cv2

    rgba = img.convert("RGBA")
    np_img = np.array(rgba)
    gray = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2GRAY)
    _, mask = cv2.threshold(gray, int(threshold * 255 / 100), 255, cv2.THRESH_BINARY)
    np_img[..., 3] = 255 - mask
    return Image.fromarray(np_img)


def register(app, utils: dict[str, Any]):
    if remove is None:
        logger.warning("rembg not installed; using simple threshold background removal")

    @app.post("/remove-background/")
    async def remove_background(
        image_file: UploadFile = File(...),
        threshold: int = Query(50, ge=0, le=100),
    ):
        try:
            contents = await image_file.read()
            input_image = Image.open(io.BytesIO(contents))
            t = max(0, min(100, threshold))
            if remove is not None:
                output = remove(
                    input_image,
                    alpha_matting=True,
                    alpha_matting_foreground_threshold=int(t * 255 / 100),
                )
            else:
                output = _fallback_remove(input_image, t)

            buf = io.BytesIO()
            output.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            return {"image": b64}
        except Exception:
            logger.exception("Background removal failed")
            return JSONResponse(
                status_code=500, content={"message": "Background removal failed"}
            )
