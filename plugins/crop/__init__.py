import base64
import json
import logging
import os
import uuid
from typing import Any

import cv2
import numpy as np
from fastapi import Body, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse

__all__ = ["register"]

logger = logging.getLogger(__name__)


def register(app, utils: dict[str, Any]):
    get_session_dir = utils["get_session_dir"]
    encrypt_bytes = utils["encrypt_bytes"]
    ENC_SUFFIX = utils["ENC_SUFFIX"]
    MAX_UPLOAD_BYTES = utils.get("MAX_UPLOAD_BYTES", 5 * 1024 * 1024)

    def order_points(pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

    def detect_document_corners(img):
        h, w = img.shape[:2]
        scale = 1.0
        max_dim = max(w, h)
        if max_dim > 1000:
            scale = 1000.0 / max_dim
            img = cv2.resize(
                img,
                (int(w * scale), int(h * scale)),
                interpolation=cv2.INTER_AREA,
            )
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(gray, 50, 200)
        cnts, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:
                pts = order_points(approx.reshape(4, 2))
                return pts / scale
        return None

    @app.post("/detect-corners/")
    async def detect_corners(request: Request, image_file: UploadFile = File(...)):
        try:
            contents = await image_file.read()
            if len(contents) > MAX_UPLOAD_BYTES:
                return JSONResponse(status_code=413, content={"message": "File too large"})

            session_id = request.cookies.get("session_id")
            session_dir = get_session_dir(session_id)
            if session_dir:
                try:
                    fname = os.path.join(
                        session_dir,
                        f"{uuid.uuid4().hex}{os.path.splitext(image_file.filename)[1]}{ENC_SUFFIX}",
                    )
                    enc = encrypt_bytes(session_id, contents)
                    with open(fname, "wb") as fh:
                        fh.write(enc)
                except Exception:
                    logger.exception("Failed to save uploaded image")

            nparr = np.frombuffer(contents, np.uint8)
            img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img_cv is None:
                return JSONResponse(status_code=400, content={"message": "Invalid image"})
            corners = detect_document_corners(img_cv)
            if corners is None:
                return JSONResponse(status_code=400, content={"message": "Edges not found"})
            pts = corners.reshape(8).tolist()
            return {"points": pts}
        except Exception:
            logger.exception("Corner detection failed")
            return JSONResponse(status_code=500, content={"message": "Detection error"})

    @app.post("/process-image/")
    async def process_image(
        request: Request,
        image_file: UploadFile = File(...),
        points: str = Form(...),
        original_width: int = Form(...),
        original_height: int = Form(...),
        brightness: int = Form(100),
        contrast: int = Form(100),
    ):
        logger.info(
            "Received image: %s, original_width: %s, original_height: %s",
            image_file.filename,
            original_width,
            original_height,
        )
        logger.info("Received points string (raw form data): %s", points)
        session_id = request.cookies.get("session_id")
        session_dir = get_session_dir(session_id)
        try:
            contents = await image_file.read()
            if len(contents) > MAX_UPLOAD_BYTES:
                return JSONResponse(status_code=413, content={"message": "File too large"})

            if session_dir:
                try:
                    orig_fname = os.path.join(
                        session_dir,
                        f"{uuid.uuid4().hex}{os.path.splitext(image_file.filename)[1]}{ENC_SUFFIX}",
                    )
                    enc_orig = encrypt_bytes(session_id, contents)
                    with open(orig_fname, "wb") as fh:
                        fh.write(enc_orig)
                except Exception:
                    logger.exception("Failed to save uploaded image")

            nparr = np.frombuffer(contents, np.uint8)
            img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img_cv is None:
                logger.error("Failed to decode image.")
                return JSONResponse(status_code=400, content={"message": "Invalid image file"})

            logger.info("Image decoded successfully. Shape: %s", img_cv.shape)
            try:
                scaled_points_flat = json.loads(points)
            except json.JSONDecodeError:
                logger.error("Failed to parse points JSON: %s", points)
                return JSONResponse(status_code=400, content={"message": "Invalid points JSON format."})
            if not isinstance(scaled_points_flat, list) or len(scaled_points_flat) != 8:
                logger.error("Invalid number of points or format: %s", len(scaled_points_flat))
                return JSONResponse(status_code=400, content={"message": "Requires an array of 8 coordinates for 4 points."})

            src_pts = np.array(scaled_points_flat, dtype=np.float32).reshape((4, 2))
            logger.info("Source points for perspective transform: %s", src_pts)

            tl, tr, br, bl = src_pts
            width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
            width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
            max_width = max(int(width_a), int(width_b))

            height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
            height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
            max_height = max(int(height_a), int(height_b))

            logger.info("Max width from selection: %s", max_width)
            logger.info("Max height from selection: %s", max_height)

            if max_width <= 0 or max_height <= 0:
                logger.error(
                    "Calculated max_width or max_height is invalid. Width: %s, Height: %s", max_width, max_height
                )
                return JSONResponse(
                    status_code=400,
                    content={"message": "Invalid points leading to zero/negative output dimensions."},
                )

            dst_pts = np.array(
                [
                    [0, 0],
                    [max_width - 1, 0],
                    [max_width - 1, max_height - 1],
                    [0, max_height - 1],
                ],
                dtype=np.float32,
            )

            matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
            if matrix is None:
                logger.error("Failed to compute perspective transform matrix. Points might be collinear or invalid.")
                return JSONResponse(
                    status_code=400,
                    content={"message": "Could not compute perspective transform. Check point alignment."},
                )

            warped_image = cv2.warpPerspective(
                img_cv,
                matrix,
                (max_width, max_height),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REPLICATE,
            )
            b_factor = max(0, brightness) / 100.0
            c_factor = max(0, contrast) / 100.0
            adjusted = cv2.convertScaleAbs(
                warped_image, alpha=c_factor, beta=int((b_factor - 1) * 255)
            )

            success, img_encoded_buffer = cv2.imencode(".png", adjusted)
            if not success:
                logger.error("Failed to encode processed image to PNG.")
                return JSONResponse(status_code=500, content={"message": "Failed to encode processed image."})

            img_base64 = base64.b64encode(img_encoded_buffer).decode("utf-8")
            if session_dir:
                try:
                    fname = os.path.join(session_dir, f"{uuid.uuid4().hex}.png{ENC_SUFFIX}")
                    enc = encrypt_bytes(session_id, img_encoded_buffer)
                    with open(fname, "wb") as fh:
                        fh.write(enc)
                except Exception:
                    logger.exception("Failed to save processed image to session dir")

            return JSONResponse(
                content={
                    "message": "Image processed successfully",
                    "processed_image": "data:image/png;base64," + img_base64,
                }
            )
        except json.JSONDecodeError as e:
            logger.exception("JSON parsing error: %s", e)
            return JSONResponse(status_code=400, content={"message": f"Invalid points format: {e}"})
        except Exception as e:
            logger.exception("An error occurred during image processing.")
            return JSONResponse(status_code=500, content={"message": f"An internal error occurred: {str(e)}"})
