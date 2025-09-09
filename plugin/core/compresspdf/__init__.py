import logging
from typing import Any

__all__ = ["register"]

logger = logging.getLogger(__name__)

def register(app, utils: dict[str, Any]):
    def compress_pdf(pdf_bytes: bytes, level: str = "medium", jpeg_quality: int = 75) -> bytes:
        try:
            import fitz
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            lvl = (level or "").lower()
            # default quality and garbage collection
            q = 95
            garbage = 0
            if lvl == "low":
                q = 90
            elif lvl == "medium":
                garbage = 2
                q = 60
            elif lvl == "extreme":
                garbage = 4
                q = max(10, min(95, int(jpeg_quality)))

            save_args = {
                "garbage": garbage,
                "deflate": True,
                "deflate_images": True,
                "deflate_fonts": True,
                "image_compression": "jpeg",
                "jpeg_quality": q,
                "clean": True,
            }
            pdf_bytes = doc.tobytes(**save_args)
            doc.close()
            return pdf_bytes
        except Exception:
            logger.exception("PDF compression failed")
            return pdf_bytes
    utils["compress_pdf"] = compress_pdf
