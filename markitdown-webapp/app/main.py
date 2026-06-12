import os
import re
import tempfile
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from markitdown import MarkItDown

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", tempfile.gettempdir())) / "markitdown_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff",
    ".docx", ".pptx", ".xlsx", ".html", ".htm", ".csv", ".json", ".xml", ".txt", ".zip", ".epub"
}

app = FastAPI(title="MarkItDown Web Converter")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def safe_stem(filename: str) -> str:
    stem = Path(filename).stem or "converted"
    stem = re.sub(r"[^a-zA-Z0-9._-]+", "-", stem).strip("-._")
    return stem[:80] or "converted"


def validate_filename(filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/convert")
async def convert_file(file: UploadFile = File(...)):
    validate_filename(file.filename or "")

    suffix = Path(file.filename).suffix.lower()
    base_name = safe_stem(file.filename or "converted")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum allowed size is {MAX_FILE_SIZE_MB} MB.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(content)
        temp_path = Path(temp_file.name)

    try:
        converter = MarkItDown(enable_plugins=False)
        result = converter.convert(str(temp_path))
        markdown = result.text_content or ""
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {exc}") from exc
    finally:
        temp_path.unlink(missing_ok=True)

    output_name = f"{base_name}.md"
    output_path = OUTPUT_DIR / output_name
    counter = 1
    while output_path.exists():
        output_name = f"{base_name}-{counter}.md"
        output_path = OUTPUT_DIR / output_name
        counter += 1

    output_path.write_text(markdown, encoding="utf-8")

    return JSONResponse({
        "filename": file.filename,
        "markdown_filename": output_name,
        "download_url": f"/api/download/{output_name}",
        "markdown": markdown,
    })


@app.get("/api/download/{filename}")
def download_markdown(filename: str):
    safe_name = Path(filename).name
    path = OUTPUT_DIR / safe_name
    if not path.exists() or path.suffix.lower() != ".md":
        raise HTTPException(status_code=404, detail="Markdown file not found.")
    return FileResponse(path, media_type="text/markdown", filename=safe_name)
