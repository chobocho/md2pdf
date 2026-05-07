import argparse
import hashlib
import io
import markdown
import os
import re
import sys
import tempfile
import threading
import unicodedata
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
except (ImportError, OSError):
    # WeasyPrint pulls in native libs (pango/harfbuzz/cairo) at import time;
    # let the module still load so unit tests targeting pure-Python helpers
    # (markdown preprocessing, CSS builder, argparse, Flask routes with
    # convert mocked) can run on machines lacking those libraries. Anything
    # that actually renders PDF will hit a clear ImportError below.
    HTML = None
    CSS = None
    FontConfiguration = None

@dataclass(frozen=True)
class FontResource:
    """A bundled font we may need to download. If `archive_member` is set,
    `url` points to a zip archive and the named entry inside is extracted
    to `filename`; otherwise `url` points directly to a .ttf file."""
    filename: str
    url: str
    sha256: str
    archive_member: str = ""


FONT_RESOURCES: dict[str, FontResource] = {
    "regular": FontResource(
        filename="NanumGothic-Regular.ttf",
        url="https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf",
        sha256="76f45ef4a6bcff344c837c95a7dcc26e017e38b5846d5ae0cdcb5b86be2e2d31",
    ),
    "bold": FontResource(
        filename="NanumGothic-Bold.ttf",
        url="https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf",
        sha256="f96298f9fb18e364d2370f4c3ce948ac67a2b61af992d7234bc15c42b033c674",
    ),
    "code": FontResource(
        filename="D2Coding.ttf",
        url="https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip",
        sha256="0f1c9192eac7d56329dddc620f9f1666b707e9c8ed38fe1f988d0ae3e30b24e6",
        archive_member="D2Coding/D2Coding-Ver1.3.2-20180524.ttf",
    ),
    # Hanja (CJK) fallback. NanumGothic-Regular has zero CJK Unified glyph
    # coverage, so any 漢字 in the source renders as a missing-glyph box (□)
    # without this. The Korean SubsetOTF of Noto Sans CJK covers ~8.1k of the
    # 21k CJK Unified Ideographs (every common Korean Hanja) plus 335 of 512
    # CJK Compatibility Ideographs, in a 4.6 MB OTF. Listed last in the body
    # font-family chain so HarfBuzz only falls through for glyphs the
    # NanumGothic faces actually lack — Hangul and Latin are unaffected.
    "hanja": FontResource(
        filename="NotoSansKR-Regular.otf",
        url="https://github.com/notofonts/noto-cjk/raw/refs/tags/Sans2.004/Sans/SubsetOTF/KR/NotoSansKR-Regular.otf",
        sha256="69975a0ac8472717870aefeab0a4d52739308d90856b9955313b2ad5e0148d68",
    ),
}

# Backwards-compat module-level constants.
FONT_FILENAME = FONT_RESOURCES["regular"].filename
FONT_URL = FONT_RESOURCES["regular"].url
FONT_SHA256 = FONT_RESOURCES["regular"].sha256


def _verify_sha256(filepath: Path, expected: str) -> bool:
    h = hashlib.sha256(filepath.read_bytes()).hexdigest()
    return h == expected


def _ensure_font_resource(spec: FontResource, fonts_dir: Path) -> Path:
    """Download (if missing), verify SHA256, and (if needed) extract `spec`
    into `fonts_dir`. Atomic w.r.t. disk: bytes are verified in memory before
    any file is written, so failures never leave a partial file behind."""
    dest = fonts_dir / spec.filename
    if dest.exists():
        return dest

    print(f"Downloading font: {spec.filename} ...")
    try:
        with urllib.request.urlopen(spec.url) as resp:
            data = resp.read()
    except Exception as e:
        raise RuntimeError(f"Font download failed for {spec.filename}: {e}") from e

    actual = hashlib.sha256(data).hexdigest()
    if actual != spec.sha256:
        raise RuntimeError(
            f"Font integrity check failed for {spec.filename} (SHA256 mismatch). "
            f"expected={spec.sha256}, got={actual}. "
            "Delete fonts/ and retry, or update FONT_RESOURCES."
        )

    if not spec.archive_member:
        dest.write_bytes(data)
    else:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            with zf.open(spec.archive_member) as src:
                dest.write_bytes(src.read())

    print(f"Font saved to: {dest}")
    return dest


def ensure_fonts(fonts_dir: Path = None) -> dict[str, Path]:
    """Download and verify every bundled font. Returns role → on-disk path.
    Roles: 'regular', 'bold', 'code' (D2Coding monospace)."""
    if fonts_dir is None:
        fonts_dir = Path(__file__).parent / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    return {
        role: _ensure_font_resource(spec, fonts_dir)
        for role, spec in FONT_RESOURCES.items()
    }


def ensure_font(fonts_dir: Path = None) -> Path:
    """Backwards-compatible: returns the path to NanumGothic-Regular only."""
    if fonts_dir is None:
        fonts_dir = Path(__file__).parent / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    return _ensure_font_resource(FONT_RESOURCES["regular"], fonts_dir)


MARKDOWN_EXTENSIONS = ["extra", "toc", "codehilite"]
MARKDOWN_EXTENSION_CONFIGS = {
    "codehilite": {
        # Avoid mis-classifying plain fences (```\n...\n```) as some random
        # language; only highlight when the user names a real lexer.
        "guess_lang": False,
        "css_class": "codehilite",
        # CSS class names instead of inline style="..." so PDFs stay diff-able.
        "noclasses": False,
        "pygments_style": "default",
    },
}

_PYGMENTS_STYLE = "default"


def _preprocess_markdown(md_text: str) -> str:
    """Text-level transformations applied before passing to python-markdown.

    1. Strip a Pandoc-style YAML metadata block at the very top of the file
       (`---\\n...\\n---\\n` or `---\\n...\\n...\\n`). Without this the
       leading `---` is parsed as a horizontal rule and the metadata leaks
       into the body as a paragraph.
    2. Drop any leading run of blank lines and standalone `\\newpage` /
       `\\pagebreak` commands. Pandoc authors usually put a `\\newpage` right
       after the metadata expecting Pandoc to fill page 1 with a title page
       rendered from the metadata; since we don't render a title page, that
       leading page break would just produce a blank first page.
    3. Convert Pandoc/LaTeX hard page-break commands (`\\newpage`,
       `\\pagebreak`) on a line of their own into `<div class="page"></div>`
       so the existing `.page { page-break-after: always }` CSS fires.
    4. Strip unsupported `name=foo.yml` style attributes from fenced code
       info strings (python-markdown's fenced_code only recognises a single
       language token).
    5. Convert GitHub-flavored task list markers `- [ ]` / `- [x]` into
       a styled `<span class="taskbox">` (checked variants get an extra
       class). We avoid `<input type="checkbox">` because WeasyPrint renders
       the form control with a wide default size that pushes the label
       text onto the next line.
    6. Normalise XHTML self-closing `<div class="page"/>` to HTML5 closing
       form so the page-break CSS actually fires (HTML5 ignores the trailing
       `/` and would otherwise wrap the rest of the document in the div).
    """
    md_text = re.sub(
        r"\A---\r?\n.*?\r?\n(?:---|\.\.\.)\r?\n",
        "",
        md_text,
        count=1,
        flags=re.DOTALL,
    )
    md_text = re.sub(
        r"\A(?:[ \t]*\r?\n|[ \t]*\\(?:newpage|pagebreak)[ \t]*\r?\n)+",
        "",
        md_text,
    )
    md_text = re.sub(
        r"^[ \t]*\\(?:newpage|pagebreak)[ \t]*$",
        '<div class="page"></div>',
        md_text,
        flags=re.MULTILINE,
    )
    md_text = re.sub(
        r'<div\s+class=["\']page["\']\s*/>',
        '<div class="page"></div>',
        md_text,
    )
    md_text = re.sub(
        r"^([ \t]*(?:```|~~~)\w+)[ \t]+\S.*$", r"\1", md_text, flags=re.MULTILINE
    )
    md_text = re.sub(
        r"^([ \t]*[-*+])[ \t]+\[ \][ \t]+",
        r'\1 <span class="taskbox"></span> ',
        md_text, flags=re.MULTILINE,
    )
    md_text = re.sub(
        r"^([ \t]*[-*+])[ \t]+\[[xX]\][ \t]+",
        r'\1 <span class="taskbox checked"></span> ',
        md_text, flags=re.MULTILINE,
    )
    return md_text


_EMOJI_SAFE_SPLIT = re.compile(
    r"(<pre\b[^>]*>.*?</pre>|<code\b[^>]*>.*?</code>)", re.DOTALL
)


def _emojize_html(html: str) -> str:
    """Replace `:shortcode:` with emoji glyphs in HTML body text, leaving
    `<pre>` and `<code>` blocks untouched (so source listings keep their
    literal `:foo:` text). Unknown shortcodes pass through unchanged."""
    import emoji
    parts = _EMOJI_SAFE_SPLIT.split(html)
    return "".join(
        part if part.startswith(("<pre", "<code"))
        else emoji.emojize(part, language="alias")
        for part in parts
    )


def _render_html(md_text: str) -> str:
    """Markdown → HTML using the same preprocessing and extensions used by
    `convert_md_to_pdf`. Exposed so tests don't duplicate the extension list.
    """
    md_text = _preprocess_markdown(md_text)
    html = markdown.markdown(
        md_text,
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs=MARKDOWN_EXTENSION_CONFIGS,
    )
    return _emojize_html(html)


def _pygments_css() -> str:
    """Return Pygments token-color rules scoped to `.codehilite`.

    `HtmlFormatter.get_style_defs()` also emits a few unscoped rules
    (`pre { line-height: 125% }`, `td.linenos { ... }`, `span.linenos { ... }`)
    which would either fight our `pre` styling or apply to features we don't
    use (line numbers). Strip them so the cascade stays predictable.
    """
    from pygments.formatters import HtmlFormatter
    raw = HtmlFormatter(style=_PYGMENTS_STYLE, nobackground=True).get_style_defs(
        ".codehilite"
    )
    cleaned = []
    for line in raw.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(("pre ", "pre{", "td.linenos", "span.linenos")):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def _build_css(font_uris: dict, *, page_numbers: bool = True) -> str:
    """Build the stylesheet used for PDF rendering.

    `font_uris` must contain keys 'regular', 'bold', 'code' — each a `file://`
    URI pointing to a .ttf. Three @font-face rules are emitted: NanumGothic
    Regular, NanumGothic Bold (real glyph weight, not synthetic), and
    D2Coding (Korean-aware fixed-width font for code blocks).

    `page_numbers=True` injects an `@bottom-center` margin box rendering
    `<page> / <total>` on every page; pass False to omit.

    GitHub-flavored markdown look (h1/h2 underline, blockquote bar, zebra
    tables, distinct inline-code vs pre-block) with Korean readability
    settings preserved (`word-break: keep-all`, generous line-height).
    Pygments token rules are placed first so our own `pre`/`code` rules
    win on the cascade for shared properties.
    """
    page_number_rule = ""
    if page_numbers:
        page_number_rule = """
        @bottom-center {
            content: counter(page) " / " counter(pages);
            font-family: 'NanumGothic', sans-serif;
            font-size: 9pt;
            color: #59636e;
        }
        """
    return f"""
    {_pygments_css()}

    @font-face {{
        font-family: 'NanumGothic';
        src: url('{font_uris["regular"]}') format('truetype');
        font-weight: normal;
        font-style: normal;
    }}
    @font-face {{
        font-family: 'NanumGothic';
        src: url('{font_uris["bold"]}') format('truetype');
        font-weight: bold;
        font-style: normal;
    }}
    @font-face {{
        font-family: 'D2Coding';
        src: url('{font_uris["code"]}') format('truetype');
        font-weight: normal;
        font-style: normal;
    }}
    @font-face {{
        font-family: 'Noto Sans KR';
        src: url('{font_uris["hanja"]}') format('opentype');
        font-weight: normal;
        font-style: normal;
    }}

    /* font-family lives on body (not `*`) so that `code`/`pre` overrides
       cascade to descendant spans via inheritance. A `* {{ font-family }}`
       rule wins directly on every span (specificity 0,0,0 vs inherited
       value), forcing Pygments tokens back into the body sans-serif font. */
    * {{
        box-sizing: border-box;
    }}

    body {{
        font-family: 'NanumGothic', 'Noto Sans KR', sans-serif;
        line-height: 1.7;
        padding: 24px 32px;
        margin: 0 auto;
        max-width: 980px;
        color: #1f2328;
        word-break: keep-all;
        overflow-wrap: break-word;
        font-size: 11pt;
    }}

    h1, h2, h3, h4, h5, h6 {{
        margin-top: 1.5em;
        margin-bottom: 0.6em;
        font-weight: 600;
        line-height: 1.3;
        color: #1f2328;
    }}

    h1 {{
        font-size: 2em;
        padding-bottom: 0.3em;
        border-bottom: 1px solid #d1d9e0;
    }}

    h2 {{
        font-size: 1.5em;
        padding-bottom: 0.3em;
        border-bottom: 1px solid #d1d9e0;
    }}

    h3 {{ font-size: 1.25em; }}
    h4 {{ font-size: 1em; }}
    h5 {{ font-size: 0.9em; }}
    h6 {{ font-size: 0.85em; color: #59636e; }}

    p {{
        margin-top: 0;
        margin-bottom: 1em;
    }}

    a {{
        color: #0969da;
        text-decoration: none;
    }}

    code {{
        font-family: 'D2Coding', 'NanumGothic', 'Noto Sans KR', Consolas, Menlo, monospace;
        font-size: 85%;
        padding: 0.2em 0.4em;
        background-color: rgba(175, 184, 193, 0.2);
        border-radius: 6px;
    }}

    pre {{
        font-family: 'D2Coding', 'NanumGothic', 'Noto Sans KR', Consolas, Menlo, monospace;
        background-color: #f6f8fa;
        padding: 16px;
        border-radius: 6px;
        line-height: 1.45;
        font-size: 85%;
        margin-bottom: 16px;
        white-space: pre-wrap;
        word-break: normal;
        overflow-wrap: break-word;
    }}

    pre code {{
        padding: 0;
        background: none;
        border-radius: 0;
        font-size: 100%;
    }}

    blockquote {{
        margin: 0 0 16px 0;
        padding: 0 1em;
        color: #59636e;
        border-left: 4px solid #d1d9e0;
    }}

    table {{
        border-collapse: collapse;
        margin-bottom: 16px;
        width: 100%;
    }}

    th, td {{
        border: 1px solid #d1d9e0;
        padding: 6px 13px;
        text-align: left;
    }}

    th {{
        background-color: #f6f8fa;
        font-weight: 600;
    }}

    tr:nth-child(2n) {{
        background-color: #f6f8fa;
    }}

    hr {{
        border: 0;
        border-top: 2px solid #d1d9e0;
        margin: 24px 0;
    }}

    img {{
        max-width: 100%;
        height: auto;
    }}

    ul, ol {{
        margin-top: 0;
        margin-bottom: 16px;
        padding-left: 2em;
    }}

    li + li {{
        margin-top: 0.25em;
    }}

    .taskbox {{
        display: inline-block;
        width: 0.85em;
        height: 0.85em;
        margin-right: 0.4em;
        vertical-align: -0.05em;
        border: 1.5px solid #59636e;
        border-radius: 3px;
        background: #fff;
        line-height: 1;
        text-align: center;
        font-size: 0.95em;
    }}

    .taskbox.checked {{
        background: #0969da;
        border-color: #0969da;
        color: #fff;
    }}

    .taskbox.checked::before {{
        content: "✓";
        font-weight: bold;
        font-size: 0.85em;
    }}

    sup {{
        font-size: 0.75em;
        vertical-align: super;
        line-height: 0;
    }}

    .footnote {{
        margin-top: 32px;
        padding-top: 12px;
        font-size: 0.85em;
        color: #59636e;
    }}

    .footnote hr {{
        border-top: 1px solid #d1d9e0;
        margin: 0 0 12px 0;
    }}

    .footnote ol {{
        padding-left: 1.4em;
    }}

    a.footnote-ref, a.footnote-backref {{
        color: #0969da;
        text-decoration: none;
    }}

    .page {{
        page-break-after: always;
    }}

    /* Pygments' default style paints Error tokens with a red border, which
       turns symbols like `<`, `>` (and anything the lexer can't classify)
       into random red boxes in the PDF. Disable it. */
    .codehilite .err {{
        border: none;
    }}

    @page {{
        margin: 2cm;
        {page_number_rule}
    }}
    """


def convert_md_to_pdf(md_filepath, pdf_filepath, font_path=None, *, page_numbers: bool = True, custom_css=None):
    """
    Convert a Markdown file to PDF with Korean font support.

    Args:
        md_filepath: Path to input .md file.
        pdf_filepath: Path for output .pdf file.
        font_path: Optional .ttf path used for *all* font roles (regular,
                   bold, code). If None, the bundled NanumGothic Regular,
                   NanumGothic Bold, and D2Coding fonts are auto-downloaded.
        page_numbers: If True (default), render `<n> / <total>` in the
                   page footer. Pass False to omit.
        custom_css: Optional path to an additional .css file. Loaded AFTER
                   the built-in stylesheet so its rules win on the cascade
                   for matching specificities — partial overrides without
                   forking the whole base style.

    Returns:
        Path to the generated PDF.

    Raises:
        FileNotFoundError: If md_filepath, font_path, or custom_css path
                           does not exist.
        RuntimeError: If PDF conversion fails.
    """
    if not os.path.exists(md_filepath):
        raise FileNotFoundError(f"Markdown file not found: {md_filepath}")

    if custom_css is not None and not os.path.exists(custom_css):
        raise FileNotFoundError(f"CSS file not found: {custom_css}")

    if font_path is None:
        font_paths = ensure_fonts()
    else:
        font_path = Path(font_path)
        if not font_path.exists():
            raise FileNotFoundError(f"Font file not found: {font_path}")
        # Single-font override mode: the same file plays all four roles
        # (regular, bold, code, hanja). Users supplying their own font
        # accept its glyph coverage as authoritative — we don't second-guess
        # whether it actually contains Hanja.
        font_paths = {
            "regular": font_path,
            "bold": font_path,
            "code": font_path,
            "hanja": font_path,
        }

    font_uris = {
        role: Path(os.path.abspath(p)).as_uri() for role, p in font_paths.items()
    }

    with open(md_filepath, "r", encoding="utf-8") as f:
        md_text = f.read()

    html_content = _render_html(md_text)

    css_string = _build_css(font_uris, page_numbers=page_numbers)

    final_html = (
        "<html><head><meta charset='utf-8'></head>"
        f"<body>{html_content}</body></html>"
    )

    if HTML is None or FontConfiguration is None:
        raise RuntimeError(
            "WeasyPrint failed to import (missing native libraries: "
            "pango/harfbuzz/cairo). Install them and retry."
        )

    # Use the .md file's directory as base_url so that relative image
    # references (e.g. `![](images/x.png)`) resolve against the document,
    # not the user's current working directory.
    base_url = os.path.dirname(os.path.abspath(md_filepath))

    font_config = FontConfiguration()
    stylesheets = [CSS(string=css_string, font_config=font_config)]
    if custom_css is not None:
        # Loaded AFTER the base; cascade order = source order for equal
        # specificities, so user rules win on overlap.
        stylesheets.append(CSS(filename=str(custom_css), font_config=font_config))

    try:
        HTML(string=final_html, base_url=base_url).write_pdf(
            pdf_filepath,
            stylesheets=stylesheets,
            font_config=font_config,
        )
    except Exception as e:
        raise RuntimeError(f"PDF conversion failed: {e}") from e

    return Path(pdf_filepath)


FORM_TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#5b6cff">
<title>md2pdf — Markdown ➜ PDF</title>
<style>
  :root {
    --accent: #5b6cff;
    --accent-2: #8a5bff;
    --accent-press: #4051e6;
    --bg: #f4f5fb;
    --surface: #ffffff;
    --text: #1a1d29;
    --muted: #6b7280;
    --border: #e5e7ef;
    --error-bg: #fff1f1;
    --error-border: #ffd1d1;
    --error-text: #b3261e;
    --shadow: 0 10px 30px rgba(31, 41, 90, 0.08);
    --radius: 18px;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #0f1115;
      --surface: #181b23;
      --text: #ecedf2;
      --muted: #9aa0ad;
      --border: #2a2e3a;
      --error-bg: #2a1416;
      --error-border: #5a1f23;
      --error-text: #ff8a85;
      --shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
      "Helvetica Neue", "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100dvh;
    padding: env(safe-area-inset-top) env(safe-area-inset-right)
             env(safe-area-inset-bottom) env(safe-area-inset-left);
    -webkit-font-smoothing: antialiased;
    -webkit-tap-highlight-color: transparent;
  }
  .app {
    max-width: 480px;
    margin: 0 auto;
    padding: 24px 18px 40px;
  }
  .hero {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
    color: #fff;
    border-radius: var(--radius);
    padding: 28px 22px;
    box-shadow: var(--shadow);
    margin-bottom: 18px;
  }
  .hero .badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.28);
    border-radius: 999px;
    padding: 4px 10px;
    font-size: 12px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }
  .hero h1 {
    margin: 14px 0 6px;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -0.02em;
  }
  .hero p { margin: 0; opacity: 0.92; font-size: 14px; line-height: 1.5; }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px;
    box-shadow: var(--shadow);
  }

  .error {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    background: var(--error-bg);
    color: var(--error-text);
    border: 1px solid var(--error-border);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 14px;
    font-size: 14px;
    line-height: 1.45;
  }
  .error::before {
    content: "⚠";
    font-size: 16px;
    line-height: 1.2;
  }

  .drop-zone {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    gap: 8px;
    padding: 28px 16px;
    border: 2px dashed var(--border);
    border-radius: 14px;
    background: var(--bg);
    color: var(--muted);
    transition: border-color .15s ease, background .15s ease, transform .15s ease;
    cursor: pointer;
    min-height: 168px;
  }
  .drop-zone:hover { border-color: var(--accent); }
  .drop-zone.dragover {
    border-color: var(--accent);
    background: rgba(91, 108, 255, 0.08);
    transform: scale(1.01);
  }
  .drop-zone .icon {
    width: 44px; height: 44px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    color: #fff;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 22px;
    box-shadow: 0 6px 14px rgba(91,108,255,0.35);
  }
  .drop-zone .primary { color: var(--text); font-weight: 600; }
  .drop-zone .hint { font-size: 13px; }
  .drop-zone input[type=file] {
    position: absolute; inset: 0; opacity: 0; cursor: pointer;
  }

  .file-name {
    margin-top: 12px;
    padding: 10px 12px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    font-size: 14px;
    word-break: break-all;
    display: none;
  }
  .file-name.show { display: block; }

  .option {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 14px;
    font-size: 14px;
    color: var(--text);
    cursor: pointer;
    user-select: none;
  }
  .option input[type=checkbox] {
    width: 18px; height: 18px;
    accent-color: var(--accent);
    cursor: pointer;
  }
  .option.css-input {
    flex-direction: column;
    align-items: stretch;
    gap: 6px;
  }
  .option.css-input .label {
    font-size: 13px;
    color: var(--muted);
  }
  .option.css-input input[type=file] {
    font-size: 13px;
    padding: 6px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--bg);
    color: var(--text);
  }

  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(15, 17, 21, 0.55);
    -webkit-backdrop-filter: blur(3px);
    backdrop-filter: blur(3px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 18px;
    z-index: 1000;
    animation: fade-in 0.15s ease;
  }
  .overlay[hidden] { display: none; }
  .spinner {
    width: 52px; height: 52px;
    border: 4px solid rgba(255,255,255,0.18);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.9s linear infinite;
  }
  .overlay-text {
    color: #fff;
    font-size: 16px;
    font-weight: 500;
    letter-spacing: -0.01em;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  @keyframes fade-in { from { opacity: 0 } to { opacity: 1 } }

  button.submit {
    width: 100%;
    margin-top: 16px;
    min-height: 52px;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    color: #fff;
    border: 0;
    border-radius: 14px;
    font-size: 16px;
    font-weight: 600;
    letter-spacing: -0.01em;
    cursor: pointer;
    box-shadow: 0 8px 18px rgba(91,108,255,0.35);
    transition: transform .08s ease, box-shadow .15s ease, opacity .15s ease;
  }
  button.submit:active {
    transform: translateY(1px);
    background: var(--accent-press);
    box-shadow: 0 4px 10px rgba(91,108,255,0.3);
  }
  button.submit:disabled { opacity: .55; cursor: not-allowed; }

  footer {
    margin-top: 18px;
    text-align: center;
    color: var(--muted);
    font-size: 12px;
  }
  footer code {
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 2px 6px;
    border-radius: 6px;
    font-size: 12px;
  }
</style>
</head>
<body>
  <main class="app">
    <section class="hero">
      <span class="badge">md2pdf</span>
      <h1>Markdown ➜ PDF</h1>
      <p>Markdown(.md) 파일을 업로드하면 한국어 폰트가 적용된 PDF로 변환됩니다.</p>
    </section>

    <div class="card">
      {% if error %}<div class="error"><span><strong>에러:</strong> {{ error }}</span></div>{% endif %}
      <form action="/convert" method="post" enctype="multipart/form-data" id="upload-form">
        <label class="drop-zone" id="drop-zone" for="file-input">
          <span class="icon">⬆</span>
          <span class="primary">파일을 끌어다 놓거나 탭하여 선택</span>
          <span class="hint">.md / .markdown · 최대 16 MB</span>
          <input id="file-input" type="file" name="file"
                 accept=".md,.markdown,text/markdown" required>
        </label>
        <div class="file-name" id="file-name"></div>
        <label class="option">
          <input type="checkbox" name="page_numbers" checked>
          <span>페이지 번호 표시 (예: 3 / 39)</span>
        </label>
        <label class="option css-input">
          <span class="label">커스텀 CSS (선택, .css)</span>
          <input type="file" name="custom_css" accept=".css,text/css">
        </label>
        <button class="submit" type="submit">PDF로 변환</button>
      </form>
      <footer>콘솔에서 <code>exit</code> 입력 시 서버가 종료됩니다.</footer>
    </div>
  </main>

  <div id="overlay" class="overlay" hidden aria-hidden="true">
    <div class="spinner" role="status" aria-label="변환 중"></div>
    <div class="overlay-text">변환 중...</div>
  </div>

  <script>
    (function () {
      var dz = document.getElementById('drop-zone');
      var input = document.getElementById('file-input');
      var label = document.getElementById('file-name');
      if (!dz || !input) return;

      function showName(file) {
        if (!file) { label.classList.remove('show'); label.textContent = ''; return; }
        var kb = (file.size / 1024).toFixed(1);
        label.textContent = file.name + ' · ' + kb + ' KB';
        label.classList.add('show');
      }

      input.addEventListener('change', function () {
        showName(input.files && input.files[0]);
      });

      ['dragenter', 'dragover'].forEach(function (ev) {
        dz.addEventListener(ev, function (e) {
          e.preventDefault(); e.stopPropagation();
          dz.classList.add('dragover');
        });
      });
      ['dragleave', 'drop'].forEach(function (ev) {
        dz.addEventListener(ev, function (e) {
          e.preventDefault(); e.stopPropagation();
          dz.classList.remove('dragover');
        });
      });
      dz.addEventListener('drop', function (e) {
        var dt = e.dataTransfer;
        if (dt && dt.files && dt.files.length) {
          input.files = dt.files;
          showName(dt.files[0]);
        }
      });

      var form = document.getElementById('upload-form');
      var overlay = document.getElementById('overlay');
      var overlayText = overlay && overlay.querySelector('.overlay-text');

      function parseFilename(headerValue) {
        if (!headerValue) return 'output.pdf';
        // RFC 5987 form: filename*=UTF-8''<percent-encoded>
        var star = headerValue.match(/filename\\*=UTF-8''([^;]+)/i);
        if (star) {
          try { return decodeURIComponent(star[1]); } catch (e) {}
        }
        var plain = headerValue.match(/filename="?([^";]+)"?/i);
        return plain ? plain[1].trim() : 'output.pdf';
      }

      if (form && overlay) {
        form.addEventListener('submit', function (e) {
          // Need a file selected; let HTML5 'required' validation handle empty.
          if (!input.files || !input.files.length) return;

          e.preventDefault();
          overlay.hidden = false;
          overlayText.textContent = '변환 중...';

          var fd = new FormData(form);
          fetch('/convert', { method: 'POST', body: fd })
            .then(function (r) {
              if (!r.ok) {
                // Server returned an HTML error page; replace the document.
                return r.text().then(function (html) {
                  document.open();
                  document.write(html);
                  document.close();
                });
              }
              var name = parseFilename(r.headers.get('Content-Disposition'));
              return r.blob().then(function (blob) {
                var url = URL.createObjectURL(blob);
                var a = document.createElement('a');
                a.href = url;
                a.download = name;
                document.body.appendChild(a);
                a.click();
                a.remove();
                setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
                overlayText.textContent = '완료!';
                setTimeout(function () { overlay.hidden = true; }, 500);
              });
            })
            .catch(function (err) {
              overlay.hidden = true;
              alert('변환 실패: ' + (err && err.message ? err.message : err));
            });
        });
      }
    })();
  </script>
</body>
</html>
"""


_UNSAFE_FILENAME_CHARS = set('<>:"|?*\x00/\\')


def _safe_pdf_stem(filename: str) -> str:
    """Derive a filesystem-safe PDF stem from a user-supplied filename,
    preserving Unicode (Korean, CJK, etc.).

    Werkzeug's `secure_filename()` NFKD-strips non-ASCII characters, so a
    Korean stem like '한국어' collapses to '' and the downloaded PDF ends
    up named 'md.pdf' or similar — useless to the user. This helper keeps
    the original characters but still:

      - drops any path prefix (`/`, `\\`),
      - strips one trailing extension (`.md` / `.markdown` / etc.),
      - removes characters illegal in filenames on common OSes
        (`<>:"|?*` and NUL), and
      - removes Unicode control characters.

    Returns 'document' if nothing safe survives.
    """
    if not filename:
        return "document"
    base = filename.replace("\\", "/").rsplit("/", 1)[-1]
    stem = base.rsplit(".", 1)[0] if "." in base else base
    cleaned = "".join(
        ch for ch in stem
        if ch not in _UNSAFE_FILENAME_CHARS
        and unicodedata.category(ch)[0] != "C"
    ).strip().strip(".")
    return cleaned or "document"


def create_app():
    """Flask app factory for the md2pdf web UI."""
    from flask import Flask, render_template_string, request, send_file

    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB upload cap

    @app.route("/", methods=["GET"])
    def index():
        return render_template_string(FORM_TEMPLATE, error=None)

    @app.route("/convert", methods=["POST"])
    def convert():
        f = request.files.get("file")
        if f is None or not f.filename:
            msg = "파일이 업로드되지 않았습니다."
            print(f"[webui] {msg}", file=sys.stderr)
            return render_template_string(FORM_TEMPLATE, error=msg), 400

        original = f.filename
        lower = original.lower()
        if lower.endswith(".markdown"):
            ext = ".markdown"
        elif lower.endswith(".md"):
            ext = ".md"
        else:
            msg = f"Markdown 파일(.md)만 업로드할 수 있습니다: {original}"
            print(f"[webui] {msg}", file=sys.stderr)
            return render_template_string(FORM_TEMPLATE, error=msg), 400

        # Preserve the original (possibly Korean) stem for the download
        # filename. The on-disk tempfile uses an ASCII-safe name since its
        # name doesn't affect the output.
        stem = _safe_pdf_stem(original)

        # Browser submits checked checkboxes only; absence == unchecked
        page_numbers = request.form.get("page_numbers") == "on"

        # Optional user-supplied stylesheet; the FileStorage is empty if
        # no file was selected.
        css_upload = request.files.get("custom_css")

        with tempfile.TemporaryDirectory() as tmpdir:
            md_path = Path(tmpdir) / f"upload{ext}"
            pdf_path = Path(tmpdir) / "output.pdf"
            f.save(md_path)

            custom_css_path = None
            if css_upload is not None and css_upload.filename:
                css_save = Path(tmpdir) / "user.css"
                css_upload.save(css_save)
                custom_css_path = str(css_save)

            try:
                convert_md_to_pdf(
                    str(md_path),
                    str(pdf_path),
                    page_numbers=page_numbers,
                    custom_css=custom_css_path,
                )
            except FileNotFoundError as e:
                msg = f"파일을 찾을 수 없습니다: {e}"
                print(f"[webui] {msg}", file=sys.stderr)
                return render_template_string(FORM_TEMPLATE, error=msg), 400
            except Exception as e:
                msg = f"변환 실패: {e}"
                print(f"[webui] {msg}", file=sys.stderr)
                return render_template_string(FORM_TEMPLATE, error=msg), 500

            pdf_bytes = pdf_path.read_bytes()

        # Flask/werkzeug encodes non-ASCII `download_name` per RFC 5987
        # (`filename*=UTF-8''<percent-encoded>`); the form's JS handler
        # decodes that back into the Korean original.
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{stem}.pdf",
        )

    return app


def _stdin_exit_monitor():
    """Watch stdin for an `exit` line and terminate the process."""
    try:
        for line in sys.stdin:
            if line.strip().lower() == "exit":
                print("[webui] exit requested — shutting down.", flush=True)
                os._exit(0)
    except (EOFError, KeyboardInterrupt):
        pass


def run_webui(port: int = 5000, host: str = "0.0.0.0"):
    """Start the Flask web UI on the given port and watch stdin for `exit`."""
    app = create_app()
    threading.Thread(target=_stdin_exit_monitor, daemon=True).start()
    print(f"[webui] serving on http://{host}:{port}  (type `exit` to quit)", flush=True)
    app.run(host=host, port=port, debug=False, use_reloader=False)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="md2pdf",
        description="Convert Markdown to PDF with Korean font support.",
    )
    parser.add_argument("input", nargs="?", help="Input Markdown file (.md)")
    parser.add_argument("output", nargs="?", help="Output PDF file (default: <input>.pdf)")
    parser.add_argument("--webui", action="store_true", help="Start the web UI server")
    parser.add_argument("-p", "--port", type=int, default=5000, help="Web UI port (default: 5000)")
    parser.add_argument("--font", help="Optional explicit .ttf font path")
    parser.add_argument(
        "--no-page-numbers",
        action="store_false",
        dest="page_numbers",
        help="Disable page numbers in the footer (default: on)",
    )
    parser.set_defaults(page_numbers=True)
    parser.add_argument(
        "--css",
        help="Path to a custom CSS file. Loaded after the built-in stylesheet "
             "so its rules override matching base rules.",
    )
    return parser


def main(argv=None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    if args.webui:
        run_webui(port=args.port)
        return 0

    if not args.input:
        parser.print_help()
        return 0

    output_file = args.output or args.input.replace(".md", ".pdf")
    try:
        result = convert_md_to_pdf(
            args.input,
            output_file,
            font_path=args.font,
            page_numbers=args.page_numbers,
            custom_css=args.css,
        )
        print(f"PDF saved: {result}")
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
