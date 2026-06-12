# MD Converter

A FastAPI web app that converts uploaded files into Markdown using Microsoft's MarkItDown.

## Render settings

- Language: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Root Directory: leave empty

## Important fix

This version removes `MarkItDown(enable_plugins=False)` because the installed MarkItDown version on Render does not support the `enable_plugins` argument. It now uses:

```python
converter = MarkItDown()
```

## Local run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
