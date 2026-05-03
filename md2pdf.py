import argparse
import hashlib
import io
import markdown
import os
import re
import sys
import tempfile
import threading
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

    # Strip unsupported attributes (e.g. `name=foo.yml`) from fenced code
    # fence info strings.  Python-Markdown's fenced_code extension only
    # recognises a single language token; extra key=value pairs cause the
    # fence NOT to be treated as a code block, which then misparses the
    # surrounding headings and text.
    md_text = re.sub(r"^([ \t]*(?:```|~~~)\w+)[ \t]+\S.*$", r"\1", md_text, flags=re.MULTILINE)

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
        <button class="submit" type="submit">PDF로 변환</button>
      </form>
      <footer>콘솔에서 <code>exit</code> 입력 시 서버가 종료됩니다.</footer>
    </div>
  </main>

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
    })();
  </script>
</body>
</html>
"""


def create_app():
    """Flask app factory for the md2pdf web UI."""
    from flask import Flask, render_template_string, request, send_file
    from werkzeug.utils import secure_filename

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

        name = secure_filename(f.filename) or "upload.md"
        if not name.lower().endswith((".md", ".markdown")):
            msg = f"Markdown 파일(.md)만 업로드할 수 있습니다: {f.filename}"
            print(f"[webui] {msg}", file=sys.stderr)
            return render_template_string(FORM_TEMPLATE, error=msg), 400

        with tempfile.TemporaryDirectory() as tmpdir:
            md_path = Path(tmpdir) / name
            pdf_path = md_path.with_suffix(".pdf")
            f.save(md_path)
            try:
                convert_md_to_pdf(str(md_path), str(pdf_path))
            except FileNotFoundError as e:
                msg = f"파일을 찾을 수 없습니다: {e}"
                print(f"[webui] {msg}", file=sys.stderr)
                return render_template_string(FORM_TEMPLATE, error=msg), 400
            except Exception as e:
                msg = f"변환 실패: {e}"
                print(f"[webui] {msg}", file=sys.stderr)
                return render_template_string(FORM_TEMPLATE, error=msg), 500

            pdf_bytes = pdf_path.read_bytes()

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=pdf_path.name,
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
        result = convert_md_to_pdf(args.input, output_file, font_path=args.font)
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
