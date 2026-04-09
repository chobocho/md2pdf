# Change History

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
