# Change History

## 2026-04-10 — Web UI, CLI Refactor & Fence Attribute Fix

### New Features

1. **Web UI for Markdown ➜ PDF conversion**
   - Run `python md2pdf.py --webui` to start a Flask-based upload page.
   - Single page with file upload form; converted PDF is streamed back as
     a download.
   - Errors (missing file, wrong extension, conversion failure) are shown
     as a red banner on the same page **and** logged to stderr.
   - 16 MB upload size cap (`MAX_CONTENT_LENGTH`).

2. **`-p` / `--port` option**
   - Choose the Web UI port (default `5000`).
   - Example: `python md2pdf.py --webui -p 8080`.

3. **`exit` console command**
   - While the Web UI is running, a daemon thread watches stdin.
   - Typing `exit` (followed by Enter) on the console terminates the app
     cleanly via `os._exit(0)`.

4. **CLI rewritten with `argparse`**
   - New options: `--webui`, `-p/--port`, `--font`.
   - Existing positional usage (`python md2pdf.py input.md [output.pdf]`)
     still works unchanged.
   - New `main(argv=None)` entry point makes the CLI testable.

### Fence Attribute Fix

- `convert_md_to_pdf()` now strips unsupported `name=foo.yml` attributes
  from fenced-code info strings before handing the text to
  python-markdown. Without this, fences with extra attributes were not
  recognised as code blocks and the surrounding headings/text were
  misparsed (sections after such fences would silently disappear).

### Changes

#### `md2pdf.py`
- Added `create_app()` Flask factory with `GET /` and `POST /convert` routes.
- Added `run_webui(port, host)` entry point.
- Added `_stdin_exit_monitor()` daemon thread for the `exit` console command.
- Added `_build_arg_parser()` and `main(argv)` for testable CLI dispatch.
- PDF response uses an in-memory `BytesIO` so the temporary directory can
  be cleaned up before Flask streams the file.
- Fence-attribute regex stripping (see above).

#### `test_md2pdf.py`
- Added `TestArgParser` (5 tests): positional input, `--webui -p`,
  `--webui --port`, no-args help, `main()` dispatching to `run_webui`.
- Added `TestWebUI` (5 tests) using Flask's `test_client`:
  - GET `/` renders the form.
  - POST `/convert` with mocked `convert_md_to_pdf` returns PDF bytes
    with `Content-Disposition: attachment; filename=…pdf`.
  - POST with non-`.md` filename → 400 + Korean error banner.
  - POST with no file field → 400 + "업로드" error.
  - POST where `convert_md_to_pdf` raises `RuntimeError` → 500 +
    "변환 실패" banner containing the underlying error message.
- Added `TestFenceAttributeStripping` (3 tests) for the regex preprocessing.
- Total: **29 tests, all passing**.

#### `README.md`
- New "Web UI" section documenting `--webui`, `-p/--port`, and the `exit`
  console command.

### Verification

- `python -m unittest test_md2pdf.py -v` → 29 passed.
- Live smoke test: `python md2pdf.py --webui -p 5099` + `curl /` returned
  HTTP 200 with the upload form HTML.

---

## 2026-04-09 — Korean Font Fix & Test Suite

### Problems Fixed

1. **weasyprint import error** — `ModuleNotFoundError: No module named 'tinycss2.color5'`  
   Fixed by upgrading `tinycss2` from 1.4.0 to 1.5.1:
   ```bash
   pip install --upgrade tinycss2
   ```

2. **Korean font not bundled** — The original script hardcoded `NanumGothic-Regular.ttf`
   in the current working directory with no download mechanism, causing immediate failure
   on any fresh clone.

3. **Font path relative to cwd** — Font was looked up relative to wherever the user ran
   the command, not relative to the script. This caused failures when running from a
   different directory.

4. **No error propagation** — Errors were silently printed and the function returned
   `None`, making it impossible to test or handle errors programmatically.

### Changes

#### `md2pdf.py`
- Added `ensure_font(fonts_dir)` — auto-downloads `NanumGothic-Regular.ttf` from
  Google Fonts GitHub on first use into `<script_dir>/fonts/`
- Added SHA256 integrity verification of the downloaded font
- Font path now defaults to `<script_dir>/fonts/NanumGothic-Regular.ttf` (relative
  to script, not cwd)
- `convert_md_to_pdf()` now raises `FileNotFoundError` for missing inputs instead of
  printing and returning `None`
- `convert_md_to_pdf()` now raises `RuntimeError` on PDF generation failure
- `convert_md_to_pdf()` returns `Path(pdf_filepath)` on success
- Improved CSS: added `word-break: keep-all`, `overflow-wrap: break-word`, page margins,
  blockquote styling, and better heading styles for Korean readability
- Added `toc` extension to markdown for table-of-contents support
- `font_path` parameter added to `convert_md_to_pdf()` for custom font override

#### `test_md2pdf.py` (new)
- 13 unit/integration tests across 5 test classes:
  - `TestKoreanMarkdown` — verifies Korean text survives markdown-to-HTML conversion
  - `TestEnsureFont` — tests download, cache hit, SHA256 failure, network failure
  - `TestConvertMdToPdf` — tests error cases and mocked successful conversion
  - `TestSha256Verify` — tests the hash helper directly
  - `TestIntegration` — real PDF rendering tests (skipped if font not present)

#### `fonts/.gitkeep` (new)
- Tracks the `fonts/` directory in git without committing font binaries

#### `.gitignore` (new)
- Ignores `fonts/*.ttf`, `fonts/*.otf`, `*.pyc`, `*.pdf`, `__pycache__/`

#### `README.md` (new)
- Usage instructions, requirements, offline font setup, custom font API, test instructions

### Font
**NanumGothic Regular** — SIL Open Font License 1.1  
Downloaded from: https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf  
SHA256: `76f45ef4a6bcff344c837c95a7dcc26e017e38b5846d5ae0cdcb5b86be2e2d31`
