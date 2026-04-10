# md2pdf

Convert Markdown files to PDF with Korean language support using [WeasyPrint](https://weasyprint.org/) and [NanumGothic](https://fonts.google.com/specimen/Nanum+Gothic) (SIL Open Font License).

## Requirements

- Python 3.10+
- weasyprint
- markdown
- flask (only required for the Web UI)

```bash
pip install weasyprint markdown flask
```

> **Note (Termux / Android):** If weasyprint fails to import, upgrade tinycss2:
> ```bash
> pip install --upgrade tinycss2
> ```

## Quick Start

```bash
python md2pdf.py input.md
# Output: input.pdf
```

```bash
python md2pdf.py input.md output.pdf
```

On the **first run**, `NanumGothic-Regular.ttf` is automatically downloaded from Google Fonts into the `fonts/` directory. Subsequent runs use the cached file.

## Web UI

Launch a browser-based upload page that converts uploaded Markdown files to PDF:

```bash
python md2pdf.py --webui
# default: http://0.0.0.0:5000
```

Pick a custom port with `-p` (or `--port`):

```bash
python md2pdf.py --webui -p 8080
```

Open the printed URL in a browser, choose a `.md` file, and click **PDF로 변환** — the converted PDF is streamed back as a download. Errors (wrong file type, missing file, conversion failure) are shown as a red banner on the same page **and** logged to stderr.

While the Web UI is running, type `exit` in the console (followed by Enter) to terminate the server cleanly.

## Offline Use

To use without an internet connection, place `NanumGothic-Regular.ttf` in the `fonts/` directory next to the script before running:

```
md2pdf/
  fonts/
    NanumGothic-Regular.ttf   ← put it here
  md2pdf.py
```

You can download the font manually from:  
https://fonts.google.com/specimen/Nanum+Gothic

## Custom Font

Pass a font path explicitly via the Python API:

```python
from md2pdf import convert_md_to_pdf
convert_md_to_pdf("input.md", "output.pdf", font_path="/path/to/your/font.ttf")
```

## Running Tests

```bash
python -m unittest test_md2pdf.py -v
```

Unit tests run without requiring the font file. Integration tests (which render a real PDF) are automatically skipped if the font is not present.

## Font

**NanumGothic Regular** — designed by Sandoll, distributed by Google Fonts.  
License: [SIL Open Font License 1.1](https://scripts.sil.org/OFL)

## Platform Notes

Tested on Android/Termux (Linux arm64) and standard Linux (x86_64).
