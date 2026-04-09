import hashlib
import markdown
import os
import sys
import urllib.request
from pathlib import Path
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

FONT_URL = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
FONT_SHA256 = "76f45ef4a6bcff344c837c95a7dcc26e017e38b5846d5ae0cdcb5b86be2e2d31"
FONT_FILENAME = "NanumGothic-Regular.ttf"


def _verify_sha256(filepath: Path, expected: str) -> bool:
    h = hashlib.sha256(filepath.read_bytes()).hexdigest()
    return h == expected


def ensure_font(fonts_dir: Path = None) -> Path:
    """
    Return path to NanumGothic-Regular.ttf, downloading it if necessary.
    fonts_dir defaults to <script_dir>/fonts/.
    """
    if fonts_dir is None:
        fonts_dir = Path(__file__).parent / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)

    dest = fonts_dir / FONT_FILENAME
    if dest.exists():
        return dest

    print(f"Downloading font: {FONT_FILENAME} ...")
    try:
        urllib.request.urlretrieve(FONT_URL, dest)
    except Exception as e:
        if dest.exists():
            dest.unlink()
        raise RuntimeError(f"Font download failed: {e}") from e

    if not _verify_sha256(dest, FONT_SHA256):
        dest.unlink()
        raise RuntimeError(
            "Font integrity check failed (SHA256 mismatch). "
            "Delete fonts/ and retry, or set FONT_SHA256 to the new value."
        )

    print(f"Font saved to: {dest}")
    return dest


def convert_md_to_pdf(md_filepath, pdf_filepath, font_path=None):
    """
    Convert a Markdown file to PDF with Korean font support.

    Args:
        md_filepath: Path to input .md file.
        pdf_filepath: Path for output .pdf file.
        font_path: Optional explicit path to a .ttf font file.
                   If None, NanumGothic-Regular.ttf is auto-downloaded.

    Returns:
        Path to the generated PDF.

    Raises:
        FileNotFoundError: If md_filepath or explicit font_path does not exist.
        RuntimeError: If PDF conversion fails.
    """
    if not os.path.exists(md_filepath):
        raise FileNotFoundError(f"Markdown file not found: {md_filepath}")

    if font_path is None:
        font_path = ensure_font()
    else:
        font_path = Path(font_path)
        if not font_path.exists():
            raise FileNotFoundError(f"Font file not found: {font_path}")

    font_uri = Path(os.path.abspath(font_path)).as_uri()

    with open(md_filepath, "r", encoding="utf-8") as f:
        md_text = f.read()

    html_content = markdown.markdown(md_text, extensions=["extra", "toc"])

    css_string = f"""
    @font-face {{
        font-family: 'NanumGothic';
        src: url('{font_uri}') format('truetype');
        font-weight: normal;
        font-style: normal;
    }}

    * {{
        font-family: 'NanumGothic', sans-serif;
    }}

    body {{
        line-height: 1.8;
        padding: 40px;
        color: #333;
        word-break: keep-all;
        overflow-wrap: break-word;
    }}

    h1, h2, h3, h4, h5, h6 {{
        margin-top: 1.5em;
        margin-bottom: 0.5em;
        color: #111;
    }}

    pre, code {{
        background-color: #f4f4f4;
        padding: 5px 8px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.9em;
    }}

    pre code {{
        padding: 0;
        background: none;
    }}

    blockquote {{
        border-left: 4px solid #ccc;
        margin: 0;
        padding-left: 16px;
        color: #666;
    }}

    table {{
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 20px;
    }}

    th, td {{
        border: 1px solid #ddd;
        padding: 8px 12px;
        text-align: left;
    }}

    th {{
        background-color: #f2f2f2;
        font-weight: bold;
    }}

    a {{
        color: #0066cc;
    }}

    hr {{
        border: none;
        border-top: 1px solid #ddd;
        margin: 24px 0;
    }}

    @page {{
        margin: 2cm;
    }}
    """

    final_html = (
        "<html><head><meta charset='utf-8'></head>"
        f"<body>{html_content}</body></html>"
    )

    font_config = FontConfiguration()
    try:
        HTML(string=final_html).write_pdf(
            pdf_filepath,
            stylesheets=[CSS(string=css_string, font_config=font_config)],
            font_config=font_config,
        )
    except Exception as e:
        raise RuntimeError(f"PDF conversion failed: {e}") from e

    return Path(pdf_filepath)


def print_help():
    print("Usage: python md2pdf.py <input.md> [output.pdf]")
    print("       Automatically downloads NanumGothic font on first run.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    input_file = sys.argv[1]
    output_file = (
        sys.argv[2] if len(sys.argv) >= 3 else input_file.replace(".md", ".pdf")
    )

    try:
        result = convert_md_to_pdf(input_file, output_file)
        print(f"PDF saved: {result}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
