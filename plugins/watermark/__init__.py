import base64
import io
import logging
from typing import Any

from fastapi import UploadFile, File, Form
from fastapi.responses import JSONResponse
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

__all__ = ["register"]


def register(app, utils: dict[str, Any]):
    @app.post("/watermark/")
    async def apply_watermark(
        image_file: UploadFile = File(...),
        text: str | None = Form(None),
        font_size: int = Form(20),
        color: str = Form("#000000"),
        angle: float = Form(0.0),
        font_name: str = Form("arial.ttf"),
        scale: float = Form(1.0),
        watermark_image: UploadFile | None = File(None),
    ):
        try:
            contents = await image_file.read()
            base_img = Image.open(io.BytesIO(contents)).convert("RGBA")

            if watermark_image is not None:
                wm_bytes = await watermark_image.read()
                wm = Image.open(io.BytesIO(wm_bytes)).convert("RGBA")
                if scale != 1.0:
                    w, h = wm.size
                    wm = wm.resize((int(w * scale), int(h * scale)))
                if angle:
                    wm = wm.rotate(angle, expand=True)
                pos = (base_img.width - wm.width - 10, base_img.height - wm.height - 10)
                base_img.alpha_composite(wm, dest=pos)
            elif text:
                try:
                    font = ImageFont.truetype(font_name, font_size)
                except Exception:
                    font = ImageFont.load_default()
                txt_layer = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(txt_layer)
                w, h = draw.textsize(text, font=font)
                tmp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                draw_tmp = ImageDraw.Draw(tmp)
                draw_tmp.text((0, 0), text, fill=color, font=font)
                if angle:
                    tmp = tmp.rotate(angle, expand=True)
                pos = (base_img.width - tmp.width - 10, base_img.height - tmp.height - 10)
                txt_layer.alpha_composite(tmp, dest=pos)
                base_img = Image.alpha_composite(base_img, txt_layer)
            buf = io.BytesIO()
            base_img.convert("RGB").save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            return {"image": b64}
        except Exception:
            logger.exception("Watermark failed")
            return JSONResponse(status_code=500, content={"message": "Watermark failed"})
