# MarkItDown Web Converter

A simple drag-and-drop website that converts uploaded files into Markdown using Microsoft's MarkItDown.

## Features

- Drag-and-drop upload UI
- Converts PDF, images, DOCX, PPTX, XLSX, HTML, CSV, JSON, XML, TXT, ZIP, EPUB, and more supported by MarkItDown
- Markdown preview in the browser
- Download generated `.md` file
- Basic file-type allowlist and file-size limit

## Requirements

- Python 3.10+

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Configuration

Optional environment variables:

```bash
export MAX_FILE_SIZE_MB=50
export OUTPUT_DIR=/tmp
```

## Security Notes

MarkItDown processes files with the permissions of the running application. For production use:

- Run this app in an isolated container.
- Add authentication if files may contain private data.
- Add virus/malware scanning before conversion.
- Keep a strict file-size limit.
- Store converted files in private object storage, not a public folder.
- Delete temporary and converted files after a defined retention period.

## Docker

```bash
docker build -t markitdown-webapp .
docker run -p 8000:8000 markitdown-webapp
```
