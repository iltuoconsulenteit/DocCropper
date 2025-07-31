FROM python:3.11-slim

WORKDIR /opt/doccropper

# Install system dependencies used by optional features
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr libglib2.0-0 libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8765

CMD ["python", "main.py"]
