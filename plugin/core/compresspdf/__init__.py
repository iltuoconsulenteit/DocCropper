import io
import logging
from typing import Any

__all__ = ["register"]

logger = logging.getLogger(__name__)

def register(app, utils: dict[str, Any]):
    def compress_pdf(pdf_bytes: bytes, level: str = "medium", jpeg_quality: int = 75) -> bytes:
        try:
            import fitz
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            save_args = {
                "deflate": True,
                "deflate_images": True,
                "deflate_fonts": True,
                "clean": True,
                "recompress": True,
                "jpeg_quality": 75,
            }
            lvl = (level or "").lower()
            if lvl == "low":
                save_args["garbage"] = 1
                save_args["jpeg_quality"] = 85
            elif lvl == "medium":
                save_args["garbage"] = 2
                save_args["jpeg_quality"] = 60
            elif lvl == "extreme":
                save_args["garbage"] = 4
                save_args["jpeg_quality"] = max(10, min(95, int(jpeg_quality)))
            out = io.BytesIO()
            doc.save(out, **save_args)
            return out.getvalue()
        except Exception:
            logger.exception("PDF compression failed")
            return pdf_bytes
    utils["compress_pdf"] = compress_pdf
