import hashlib
import io
import os
import re
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import markdown


class TestKoreanMarkdown(unittest.TestCase):
    """Test that markdown converts Korean text correctly."""

    def test_korean_text_preserved(self):
        result = markdown.markdown("한국어 테스트", extensions=["extra"])
        self.assertIn("한국어", result)

    def test_korean_bold(self):
        result = markdown.markdown("**한국어 볼드**", extensions=["extra"])
        self.assertIn("한국어", result)
        self.assertIn("<strong>", result)

    def test_korean_heading(self):
        result = markdown.markdown("# 제목\n## 소제목", extensions=["extra"])
        self.assertIn("제목", result)
        self.assertIn("<h1>", result)
        self.assertIn("<h2>", result)


class TestFenceAttributeStripping(unittest.TestCase):
    """Test that name= attributes in code fences don't corrupt surrounding headings."""

    def _convert(self, md_text):
        import re
        import md2pdf
        # Replicate the preprocessing step from convert_md_to_pdf
        cleaned = re.sub(
            r"^([ \t]*(?:```|~~~)\w+)[ \t]+\S.*$", r"\1", md_text, flags=re.MULTILINE
        )
        return markdown.markdown(cleaned, extensions=["extra", "toc"])

    def test_name_attr_does_not_swallow_following_heading(self):
        md = (
            "## 3.1 Section\n\n"
            "```yaml name=example.yml\n"
            "key: value\n"
            "```\n\n"
            "## 3.2 Next Section\n"
        )
        html = self._convert(md)
        self.assertIn("3.2", html, "Section 3.2 must appear in output")
        self.assertIn("<h2", html)

    def test_multiple_named_fences_preserve_all_headings(self):
        md = (
            "## 3.1 First\n\n"
            "```yaml name=a.yml\nk: v\n```\n\n"
            "## 3.2 Second\n\n"
            "## 3.3 Third\n\n"
            "```yaml name=b.yml\nk: v\n```\n\n"
            "## 3.4 Fourth\n"
        )
        html = self._convert(md)
        for section in ("3.2", "3.3", "3.4"):
            self.assertIn(section, html, f"Section {section} must appear in output")

    def test_line_count_unchanged_after_stripping(self):
        import re
        with open(Path(__file__).parent / "sample.md", encoding="utf-8") as f:
            text = f.read()
        fixed = re.sub(
            r"^([ \t]*(?:```|~~~)\w+)[ \t]+\S.*$", r"\1", text, flags=re.MULTILINE
        )
        self.assertEqual(
            len(text.splitlines()),
            len(fixed.splitlines()),
            "Preprocessing must not add or remove lines",
        )


class _FakeResp:
    """Minimal context-manager stand-in for `urllib.request.urlopen()`."""
    def __init__(self, data):
        self._data = data
    def __enter__(self):
        return self
    def __exit__(self, *a):
        pass
    def read(self):
        return self._data


class TestEnsureFont(unittest.TestCase):
    """ensure_font() — backwards-compatible single-font alias for the
    NanumGothic Regular weight."""

    def test_returns_existing_font(self):
        import md2pdf
        with tempfile.TemporaryDirectory() as tmpdir:
            fonts_dir = Path(tmpdir)
            fake_font = fonts_dir / md2pdf.FONT_FILENAME
            fake_font.write_bytes(b"fake font data")

            with mock.patch("urllib.request.urlopen") as mock_open:
                result = md2pdf.ensure_font(fonts_dir=fonts_dir)

            mock_open.assert_not_called()
            self.assertEqual(result, fake_font)

    def test_downloads_when_missing(self):
        import md2pdf
        data = b"font data"
        spec = md2pdf.FontResource(
            filename="reg.ttf", url="https://x/r",
            sha256=hashlib.sha256(data).hexdigest(),
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            fonts_dir = Path(tmpdir)
            with mock.patch.dict(
                md2pdf.FONT_RESOURCES, {"regular": spec}, clear=True
            ), mock.patch("urllib.request.urlopen", return_value=_FakeResp(data)):
                result = md2pdf.ensure_font(fonts_dir=fonts_dir)

            self.assertTrue(result.exists())
            self.assertEqual(result.read_bytes(), data)

    def test_sha256_mismatch_raises_and_does_not_write(self):
        import md2pdf
        spec = md2pdf.FontResource(
            filename="reg.ttf", url="https://x/r",
            sha256="0" * 64,  # intentionally wrong
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            fonts_dir = Path(tmpdir)
            with mock.patch.dict(
                md2pdf.FONT_RESOURCES, {"regular": spec}, clear=True
            ), mock.patch(
                "urllib.request.urlopen", return_value=_FakeResp(b"actual data")
            ):
                with self.assertRaises(RuntimeError) as ctx:
                    md2pdf.ensure_font(fonts_dir=fonts_dir)

            self.assertIn("integrity", str(ctx.exception).lower())
            self.assertFalse((fonts_dir / "reg.ttf").exists())

    def test_download_failure_raises_runtime_error(self):
        import md2pdf
        spec = md2pdf.FontResource(
            filename="reg.ttf", url="https://x/r", sha256="0" * 64,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            fonts_dir = Path(tmpdir)
            with mock.patch.dict(
                md2pdf.FONT_RESOURCES, {"regular": spec}, clear=True
            ), mock.patch("urllib.request.urlopen", side_effect=OSError("net error")):
                with self.assertRaises(RuntimeError) as ctx:
                    md2pdf.ensure_font(fonts_dir=fonts_dir)

            self.assertIn("download failed", str(ctx.exception).lower())
            self.assertFalse((fonts_dir / "reg.ttf").exists())


class TestConvertMdToPdf(unittest.TestCase):
    """Test convert_md_to_pdf() with mocked weasyprint."""

    def test_missing_md_raises(self):
        import md2pdf
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(FileNotFoundError) as ctx:
                md2pdf.convert_md_to_pdf(
                    "/nonexistent/file.md",
                    os.path.join(tmpdir, "out.pdf"),
                    font_path="/dev/null",
                )
        self.assertIn("Markdown file not found", str(ctx.exception))

    def test_missing_explicit_font_raises(self):
        import md2pdf
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            Path(md_file).write_text("# Test\n한국어", encoding="utf-8")

            with self.assertRaises(FileNotFoundError) as ctx:
                md2pdf.convert_md_to_pdf(
                    md_file,
                    os.path.join(tmpdir, "out.pdf"),
                    font_path="/nonexistent/font.ttf",
                )
        self.assertIn("Font file not found", str(ctx.exception))

    def test_successful_conversion_mocked(self):
        import md2pdf
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            Path(md_file).write_text("# 제목\n\n한국어 내용입니다.", encoding="utf-8")

            fake_font = os.path.join(tmpdir, "font.ttf")
            Path(fake_font).write_bytes(b"fake font")
            out_pdf = os.path.join(tmpdir, "out.pdf")

            with mock.patch("md2pdf.HTML") as mock_html, \
                 mock.patch("md2pdf.CSS"), \
                 mock.patch("md2pdf.FontConfiguration"):
                mock_html.return_value.write_pdf.return_value = None
                result = md2pdf.convert_md_to_pdf(md_file, out_pdf, font_path=fake_font)

            mock_html.assert_called_once()
            self.assertEqual(result, Path(out_pdf))

    def test_css_contains_font_face(self):
        import md2pdf
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            Path(md_file).write_text("Hello 안녕", encoding="utf-8")
            fake_font = os.path.join(tmpdir, "font.ttf")
            Path(fake_font).write_bytes(b"fake")
            out_pdf = os.path.join(tmpdir, "out.pdf")

            captured_css = []

            def capture_css(*args, **kwargs):
                if "string" in kwargs:
                    captured_css.append(kwargs["string"])
                return mock.MagicMock()

            with mock.patch("md2pdf.HTML") as mock_html, \
                 mock.patch("md2pdf.FontConfiguration"), \
                 mock.patch("md2pdf.CSS", side_effect=capture_css):
                mock_html.return_value.write_pdf.return_value = None
                md2pdf.convert_md_to_pdf(md_file, out_pdf, font_path=fake_font)

            self.assertTrue(any("@font-face" in c for c in captured_css))

    def test_write_pdf_failure_raises_runtime_error(self):
        import md2pdf
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            Path(md_file).write_text("# Test", encoding="utf-8")
            fake_font = os.path.join(tmpdir, "font.ttf")
            Path(fake_font).write_bytes(b"fake")
            out_pdf = os.path.join(tmpdir, "out.pdf")

            with mock.patch("md2pdf.HTML") as mock_html, \
                 mock.patch("md2pdf.FontConfiguration"):
                mock_html.return_value.write_pdf.side_effect = Exception("weasyprint error")
                with self.assertRaises(RuntimeError) as ctx:
                    md2pdf.convert_md_to_pdf(md_file, out_pdf, font_path=fake_font)

            self.assertIn("PDF conversion failed", str(ctx.exception))


class TestSha256Verify(unittest.TestCase):
    """Test the SHA256 verification helper."""

    def test_correct_hash(self):
        import md2pdf
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test data")
            path = Path(f.name)
        expected = hashlib.sha256(b"test data").hexdigest()
        try:
            self.assertTrue(md2pdf._verify_sha256(path, expected))
        finally:
            path.unlink()

    def test_wrong_hash(self):
        import md2pdf
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test data")
            path = Path(f.name)
        try:
            self.assertFalse(md2pdf._verify_sha256(path, "wronghash"))
        finally:
            path.unlink()


class TestGitHubStyleCSS(unittest.TestCase):
    """CSS produced by _build_css() must match GitHub-flavored markdown look,
    while preserving Korean readability settings."""

    def _css(self):
        import md2pdf
        return md2pdf._build_css({
            "regular": "file:///fake/regular.ttf",
            "bold": "file:///fake/bold.ttf",
            "code": "file:///fake/code.ttf",
        })

    def _block(self, css, selector):
        """Return body of the first standalone CSS rule for `selector`,
        or None if no such rule exists. Excludes grouped selectors like
        'h1, h2 {' so we can assert per-element styling."""
        m = re.search(
            r"(?:^|\})\s*" + re.escape(selector) + r"\s*\{([^}]+)\}",
            css,
            re.MULTILINE,
        )
        return m.group(1) if m else None

    def test_font_face_and_korean_font(self):
        css = self._css()
        self.assertIn("@font-face", css)
        self.assertIn("NanumGothic", css)

    def test_korean_readability_preserved(self):
        css = self._css()
        self.assertIn("word-break: keep-all", css)
        self.assertRegex(css, r"line-height:\s*1\.[5-9]")

    def test_h1_has_bottom_border(self):
        body = self._block(self._css(), "h1")
        self.assertIsNotNone(body, "h1 must have its own rule")
        self.assertIn("border-bottom", body)

    def test_h2_has_bottom_border(self):
        body = self._block(self._css(), "h2")
        self.assertIsNotNone(body, "h2 must have its own rule")
        self.assertIn("border-bottom", body)

    def test_blockquote_has_left_border(self):
        body = self._block(self._css(), "blockquote")
        self.assertIsNotNone(body)
        self.assertIn("border-left", body)

    def test_pre_block_has_background_and_padding(self):
        body = self._block(self._css(), "pre")
        self.assertIsNotNone(body, "pre must have its own rule (not grouped)")
        self.assertIn("background", body)
        self.assertIn("padding", body)

    def test_pre_block_wraps_long_lines(self):
        """Without wrapping, long code lines get clipped off the right edge
        of the PDF page (no horizontal scroll exists in print). The pre
        rule must (a) preserve newlines/indent via `pre-wrap`, (b) override
        body's `word-break: keep-all`, and (c) allow breaking inside long
        unbreakable tokens like URLs."""
        body = self._block(self._css(), "pre")
        self.assertIsNotNone(body)
        self.assertIn("pre-wrap", body)
        self.assertRegex(body, r"word-break\s*:\s*normal")
        self.assertRegex(
            body,
            r"overflow-wrap\s*:\s*(break-word|anywhere)",
            f"pre must enable in-token wrapping, got: {body!r}",
        )

    def test_pre_code_resets_background(self):
        css = self._css()
        self.assertIn("pre code", css)

    def test_codehilite_err_token_has_no_red_border(self):
        """Pygments' default style boxes Error tokens (often `<`, `>`, etc.
        in code the lexer can't fully tokenise) with `border: 1px solid
        #FF0000`. That paints random red squares in PDFs. Our override
        must neutralise the border on the cascade-winning rule."""
        css = self._css()
        matches = list(re.finditer(r"\.codehilite\s+\.err\s*\{([^}]+)\}", css))
        self.assertGreaterEqual(len(matches), 1, "Need a .codehilite .err rule")
        last_body = matches[-1].group(1)
        self.assertRegex(
            last_body,
            r"border\s*:\s*(none|0\b|unset)",
            f"Last .codehilite .err rule must drop the border, got: {last_body!r}",
        )

    def test_table_has_zebra_striping(self):
        self.assertIn("nth-child", self._css())

    def test_body_constrained_width(self):
        css = self._css()
        self.assertRegex(css, r"max-width:\s*\d")

    def test_hr_styled(self):
        body = self._block(self._css(), "hr")
        self.assertIsNotNone(body)
        self.assertIn("border", body)

    def test_uses_passed_font_uris(self):
        import md2pdf
        css = md2pdf._build_css({
            "regular": "file:///custom/regular.ttf",
            "bold": "file:///custom/bold.ttf",
            "code": "file:///custom/code.ttf",
        })
        self.assertIn("file:///custom/regular.ttf", css)
        self.assertIn("file:///custom/bold.ttf", css)
        self.assertIn("file:///custom/code.ttf", css)


class TestPygmentsHighlighting(unittest.TestCase):
    """Code blocks must receive Pygments-based syntax highlighting."""

    def test_css_includes_pygments_token_styles(self):
        import md2pdf
        css = md2pdf._build_css({
            "regular": "file:///x.ttf",
            "bold": "file:///x.ttf",
            "code": "file:///x.ttf",
        })
        self.assertIn(".codehilite", css)
        # .k = Keyword token class, .s = String token class.
        # These exist for every Pygments style.
        self.assertRegex(css, r"\.codehilite\s+\.k\b")
        self.assertRegex(css, r"\.codehilite\s+\.s\b")

    def test_render_html_highlights_python_keyword(self):
        import md2pdf
        html = md2pdf._render_html("```python\ndef hello():\n    return 1\n```\n")
        self.assertIn("codehilite", html)
        self.assertRegex(html, r'<span class="k[a-z]*">def</span>')

    def test_render_html_highlights_string_literal(self):
        import md2pdf
        html = md2pdf._render_html("```python\nx = 'hello'\n```\n")
        # String tokens get a class starting with 's'
        self.assertRegex(html, r'<span class="s[a-z0-9]*">')

    def test_render_html_handles_no_language(self):
        import md2pdf
        html = md2pdf._render_html("```\nplain text\n```\n")
        self.assertIn("plain text", html)

    def test_render_html_handles_unknown_language(self):
        import md2pdf
        # Unknown lexer should fall back gracefully, not crash.
        html = md2pdf._render_html("```nonexistentlang\nfoo bar\n```\n")
        self.assertIn("foo", html)

    def test_render_html_preserves_korean_in_code(self):
        import md2pdf
        html = md2pdf._render_html("```python\n# 한국어 주석\nx = '안녕'\n```\n")
        self.assertIn("한국어", html)
        self.assertIn("안녕", html)

    def test_render_html_keeps_fence_attribute_stripping(self):
        """Regression: _render_html must still apply the name=foo.yml fence
        attribute fix introduced earlier."""
        import md2pdf
        md = "## 3.1 Section\n\n```yaml name=foo.yml\nk: v\n```\n\n## 3.2 Next\n"
        html = md2pdf._render_html(md)
        self.assertIn("3.2", html)

    def test_render_html_renders_korean_heading(self):
        """Regression: existing markdown features still work."""
        import md2pdf
        html = md2pdf._render_html("# 제목\n\n본문")
        self.assertIn("<h1", html)
        self.assertIn("제목", html)


class TestMonospaceFontInheritance(unittest.TestCase):
    """Code blocks render as `<pre><code><span class="...">...</span>...</code></pre>`.
    Pygments wraps every token in a `<span>`. If the universal `*` rule sets
    `font-family: NanumGothic`, that rule applies *directly* to every span
    (specificity 0,0,0 — wins over inheritance), so spans inside `<code>` end
    up in the sans-serif body font instead of the D2Coding monospace face.
    Defense: keep font-family off `*`, set it on `body` instead, and let
    `code`/`pre` overrides cascade to descendants."""

    def _css(self):
        import md2pdf
        return md2pdf._build_css({
            "regular": "file:///r.ttf",
            "bold": "file:///b.ttf",
            "code": "file:///c.ttf",
        })

    def _block(self, css, selector):
        m = re.search(
            r"(?:^|\})\s*" + re.escape(selector) + r"\s*\{([^}]+)\}",
            css, re.MULTILINE,
        )
        return m.group(1) if m else None

    def test_universal_selector_does_not_set_font_family(self):
        body = self._block(self._css(), r"\*")
        if body is not None:
            self.assertNotIn(
                "font-family", body,
                "`*` must not set font-family — it would override inheritance "
                "for every descendant of <code>/<pre>, defeating monospace.",
            )

    def test_body_sets_default_font_family(self):
        body = self._block(self._css(), "body")
        self.assertIsNotNone(body)
        self.assertIn("font-family", body)
        self.assertIn("NanumGothic", body)

    def test_pre_block_uses_monospace_font(self):
        """The `<pre>` wrapper itself must declare the monospace face so it
        propagates to all descendant spans via inheritance."""
        body = self._block(self._css(), "pre")
        self.assertIsNotNone(body)
        self.assertIn("D2Coding", body)
        self.assertIn("monospace", body)


class TestCustomCSS(unittest.TestCase):
    """`convert_md_to_pdf(custom_css=...)` adds a user stylesheet AFTER the
    built-in one so the user can override base rules through CSS cascade."""

    def _run_with_custom(self, custom_css_path):
        """Run convert_md_to_pdf with WeasyPrint mocked, return the list of
        CSS load specs in the order CSS() was instantiated. Each entry is
        either ('string', body) or ('filename', path)."""
        import md2pdf
        seen = []

        def capture_css(*args, **kwargs):
            if "filename" in kwargs:
                seen.append(("filename", kwargs["filename"]))
            elif "string" in kwargs:
                seen.append(("string", kwargs["string"]))
            return mock.MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "x.md")
            Path(md_file).write_text("# hi", encoding="utf-8")
            font = os.path.join(tmpdir, "f.ttf")
            Path(font).write_bytes(b"x")
            out = os.path.join(tmpdir, "out.pdf")

            with mock.patch("md2pdf.HTML") as mock_html, \
                 mock.patch("md2pdf.CSS", side_effect=capture_css), \
                 mock.patch("md2pdf.FontConfiguration"):
                mock_html.return_value.write_pdf.return_value = None
                md2pdf.convert_md_to_pdf(
                    md_file, out, font_path=font, custom_css=custom_css_path
                )
            return seen

    def test_custom_css_passed_as_filename_after_base(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            css_file = os.path.join(tmpdir, "custom.css")
            Path(css_file).write_text("body { color: red; }", encoding="utf-8")
            seen = self._run_with_custom(css_file)

        # Base CSS as inline string, custom CSS as filename
        kinds = [k for k, _ in seen]
        self.assertIn("string", kinds)
        self.assertIn("filename", kinds)

        # Custom must be AFTER base for cascade override
        base_idx = next(i for i, (k, _) in enumerate(seen) if k == "string")
        custom_idx = next(
            i for i, (k, v) in enumerate(seen) if k == "filename" and v == css_file
        )
        self.assertLess(
            base_idx, custom_idx,
            "Custom CSS must be loaded AFTER base for cascade override",
        )

    def test_no_custom_css_loads_only_base(self):
        seen = self._run_with_custom(None)
        kinds = [k for k, _ in seen]
        self.assertIn("string", kinds)
        self.assertNotIn("filename", kinds)

    def test_missing_custom_css_raises_file_not_found(self):
        import md2pdf
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "x.md")
            Path(md_file).write_text("# hi", encoding="utf-8")
            font = os.path.join(tmpdir, "f.ttf")
            Path(font).write_bytes(b"x")
            out = os.path.join(tmpdir, "out.pdf")

            with mock.patch("md2pdf.HTML") as mock_html, \
                 mock.patch("md2pdf.CSS"), \
                 mock.patch("md2pdf.FontConfiguration"):
                mock_html.return_value.write_pdf.return_value = None
                with self.assertRaises(FileNotFoundError) as ctx:
                    md2pdf.convert_md_to_pdf(
                        md_file, out, font_path=font,
                        custom_css="/nonexistent/style.css",
                    )
            self.assertIn("CSS file not found", str(ctx.exception))


class TestManualPageBreak(unittest.TestCase):
    """`<div class="page"></div>` triggers a page break (VSCode markdown-pdf
    compatible)."""

    def _css(self):
        import md2pdf
        return md2pdf._build_css({
            "regular": "file:///r.ttf",
            "bold": "file:///b.ttf",
            "code": "file:///c.ttf",
        })

    def test_page_class_has_break_after_rule(self):
        css = self._css()
        m = re.search(r"(?:^|\})\s*\.page\s*\{([^}]+)\}", css, re.MULTILINE)
        self.assertIsNotNone(m, ".page selector must exist")
        body = m.group(1)
        self.assertIn("page-break-after", body)
        self.assertIn("always", body)

    def test_div_page_passes_through_markdown(self):
        import md2pdf
        html = md2pdf._render_html('A\n\n<div class="page"></div>\n\nB\n')
        self.assertIn('class="page"', html)

    def test_self_closing_div_page_normalised_to_closing_form(self):
        """VSCode markdown-pdf uses `<div class="page"/>` (XHTML form). HTML5
        ignores the trailing `/`, so without normalisation the div would
        swallow the rest of the document and the page-break would never
        fire. We must rewrite it to `<div class="page"></div>`."""
        import md2pdf
        html = md2pdf._render_html('A\n\n<div class="page"/>\n\nB\n')
        self.assertIn('<div class="page"></div>', html)
        self.assertNotIn('<div class="page"/>', html)


class TestEmojiShortcodes(unittest.TestCase):
    """`:rocket:` style shortcodes become emoji glyphs in body text — but
    must remain literal inside `<code>` and `<pre>` blocks."""

    def test_emoji_in_paragraph_replaced(self):
        import md2pdf
        html = md2pdf._render_html("Launch :rocket: now\n")
        self.assertIn("🚀", html)
        self.assertNotIn(":rocket:", html)

    def test_multiple_emoji_replaced(self):
        import md2pdf
        html = md2pdf._render_html("Hello :smile: world :tada:\n")
        self.assertIn("😄", html)
        self.assertIn("🎉", html)

    def test_emoji_inside_inline_code_preserved(self):
        """Inline `code` containing :smile: must keep literal text."""
        import md2pdf
        html = md2pdf._render_html("Say `:smile:` in chat.\n")
        # Literal text must remain so the reader sees the shortcode
        self.assertIn(":smile:", html)

    def test_emoji_inside_fenced_code_preserved(self):
        import md2pdf
        md = "```\nprint(':rocket:')\n```\n"
        html = md2pdf._render_html(md)
        self.assertIn(":rocket:", html)
        self.assertNotIn("🚀", html)

    def test_unknown_shortcode_stays_literal(self):
        import md2pdf
        html = md2pdf._render_html("This :totally_made_up_name: stays.\n")
        self.assertIn(":totally_made_up_name:", html)

    def test_korean_paragraph_with_emoji(self):
        import md2pdf
        html = md2pdf._render_html("축하합니다 :tada: 한국어 테스트\n")
        self.assertIn("🎉", html)
        self.assertIn("축하합니다", html)
        self.assertIn("한국어 테스트", html)


class TestFootnotes(unittest.TestCase):
    """`[^1]` references and `[^1]: definition` blocks render with python-
    markdown's built-in footnotes extension."""

    def test_footnote_reference_creates_superscript(self):
        import md2pdf
        md = "본문[^1] 텍스트입니다.\n\n[^1]: 첫 번째 각주."
        html = md2pdf._render_html(md)
        # python-markdown emits <sup id="fnref:1"><a ...>1</a></sup>
        self.assertIn("fnref", html)
        self.assertIn("<sup", html)

    def test_footnote_definition_appears_in_output(self):
        import md2pdf
        md = "Body[^1] text.\n\n[^1]: footnote body content"
        html = md2pdf._render_html(md)
        self.assertIn("footnote body content", html)
        # Footnote section gets a class containing 'footnote'
        self.assertIn("footnote", html.lower())

    def test_korean_footnote(self):
        import md2pdf
        md = "한국어[^kr] 본문.\n\n[^kr]: 한국어 각주 설명입니다."
        html = md2pdf._render_html(md)
        self.assertIn("한국어 각주 설명입니다", html)
        self.assertIn("fnref", html)

    def test_no_footnote_in_plain_text(self):
        """Regression: plain text without footnote markers stays clean."""
        import md2pdf
        html = md2pdf._render_html("그냥 본문입니다.")
        self.assertNotIn("fnref", html)

    def test_css_styles_footnote_section(self):
        import md2pdf
        css = md2pdf._build_css({
            "regular": "file:///r.ttf",
            "bold": "file:///b.ttf",
            "code": "file:///c.ttf",
        })
        # `.footnote` selector exists with smaller font
        m = re.search(r"\.footnote\s*\{([^}]+)\}", css)
        self.assertIsNotNone(m, ".footnote selector must be styled")
        self.assertIn("font-size", m.group(1))


class TestTaskList(unittest.TestCase):
    """GitHub-style task lists: `- [ ]` / `- [x]` render as inline checkbox
    glyphs. We use a styled `<span class="taskbox">` instead of `<input
    type="checkbox">` because WeasyPrint (a print-target engine) does not
    reliably render form controls inline — the default `<input>` width pushes
    the label text to the next line."""

    def test_unchecked_renders_taskbox_span(self):
        import md2pdf
        html = md2pdf._render_html("- [ ] todo\n")
        self.assertIn('class="taskbox"', html)
        self.assertNotIn('class="taskbox checked"', html)
        self.assertIn('todo', html)

    def test_checked_renders_taskbox_checked_span(self):
        import md2pdf
        html = md2pdf._render_html("- [x] done\n")
        self.assertIn('class="taskbox checked"', html)
        self.assertIn('done', html)

    def test_uppercase_X_also_checked(self):
        import md2pdf
        html = md2pdf._render_html("- [X] done\n")
        self.assertIn('class="taskbox checked"', html)

    def test_asterisk_marker_also_supported(self):
        import md2pdf
        html = md2pdf._render_html("* [ ] todo\n")
        self.assertIn('class="taskbox"', html)

    def test_indented_task_supported(self):
        import md2pdf
        html = md2pdf._render_html("  - [ ] indented\n")
        self.assertIn('class="taskbox"', html)
        self.assertIn('indented', html)

    def test_korean_task_text_preserved(self):
        import md2pdf
        html = md2pdf._render_html("- [x] 한국어 작업 완료\n")
        self.assertIn('한국어 작업 완료', html)
        self.assertIn('class="taskbox checked"', html)

    def test_regular_list_unaffected(self):
        import md2pdf
        html = md2pdf._render_html("- normal item\n")
        self.assertNotIn('taskbox', html)

    def test_bracket_text_in_paragraph_unaffected(self):
        """`[foo]` syntax in regular text must not be misread as a task box."""
        import md2pdf
        html = md2pdf._render_html("Talk about [foo] and [bar].\n")
        self.assertNotIn('taskbox', html)

    def test_no_form_input_emitted(self):
        """Regression: must NOT emit `<input type="checkbox">` because
        WeasyPrint renders the form control with default block-ish width,
        wrapping the label text onto the next line."""
        import md2pdf
        html = md2pdf._render_html("- [ ] one\n- [x] two\n")
        self.assertNotIn('<input', html)

    def test_taskbox_and_label_in_same_li(self):
        """The span and the text after it must end up in the same `<li>`
        without a line break between them."""
        import md2pdf
        html = md2pdf._render_html("- [ ] todo\n")
        m = re.search(r"<li>(.*?)</li>", html, re.DOTALL)
        self.assertIsNotNone(m, "Expected a <li> in output")
        body = m.group(1)
        self.assertIn('taskbox', body)
        self.assertIn('todo', body)
        # No `<br>` or block-level break separating the marker from the label
        self.assertNotIn('<br', body)
        self.assertNotIn('<p>', body)


class TestTaskListCSS(unittest.TestCase):
    """CSS for `.taskbox` must give it a small, fixed inline-block size so
    WeasyPrint renders the marker and the label on the same line."""

    def _css(self):
        import md2pdf
        return md2pdf._build_css({
            "regular": "file:///r.ttf",
            "bold": "file:///b.ttf",
            "code": "file:///c.ttf",
        })

    def test_taskbox_rule_exists(self):
        css = self._css()
        self.assertIn(".taskbox", css)

    def test_taskbox_is_inline_block_with_em_size(self):
        css = self._css()
        m = re.search(r"\.taskbox\s*\{([^}]+)\}", css)
        self.assertIsNotNone(m, ".taskbox rule must exist")
        body = m.group(1)
        self.assertIn("inline-block", body)
        # Width must be a small em-relative size, NOT default ~200px <input> width
        self.assertRegex(body, r"width\s*:\s*0?\.\d+\s*em")
        self.assertRegex(body, r"height\s*:\s*0?\.\d+\s*em")

    def test_taskbox_checked_has_distinct_style(self):
        css = self._css()
        self.assertRegex(css, r"\.taskbox\.checked")


class TestPageNumbers(unittest.TestCase):
    """Page numbers rendered in the @page bottom-center margin box, with a
    flag to disable."""

    def _css(self, **kwargs):
        import md2pdf
        return md2pdf._build_css(
            {
                "regular": "file:///r.ttf",
                "bold": "file:///b.ttf",
                "code": "file:///c.ttf",
            },
            **kwargs,
        )

    def test_default_includes_page_counter(self):
        css = self._css()
        self.assertIn("@bottom-center", css)
        self.assertIn("counter(page)", css)
        self.assertIn("counter(pages)", css)

    def test_disable_omits_page_counter(self):
        css = self._css(page_numbers=False)
        self.assertNotIn("@bottom-center", css)
        self.assertNotIn("counter(page)", css)

    def test_page_counter_appears_after_at_page(self):
        css = self._css()
        page_idx = css.find("@page")
        bottom_idx = css.find("@bottom-center")
        self.assertGreater(page_idx, -1)
        self.assertGreater(bottom_idx, page_idx, "@bottom-center must follow @page {")


class TestConvertPropagatesPageNumbers(unittest.TestCase):
    """`convert_md_to_pdf(page_numbers=False)` must reach `_build_css`."""

    def test_disabling_reaches_css(self):
        import md2pdf
        captured_css = []

        def capture(*a, **kw):
            if "string" in kw:
                captured_css.append(kw["string"])
            return mock.MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "x.md")
            Path(md_file).write_text("# hi", encoding="utf-8")
            font = os.path.join(tmpdir, "f.ttf")
            Path(font).write_bytes(b"x")
            out = os.path.join(tmpdir, "out.pdf")

            with mock.patch("md2pdf.HTML") as mock_html, \
                 mock.patch("md2pdf.CSS", side_effect=capture), \
                 mock.patch("md2pdf.FontConfiguration"):
                mock_html.return_value.write_pdf.return_value = None
                md2pdf.convert_md_to_pdf(
                    md_file, out, font_path=font, page_numbers=False
                )

            full = " ".join(captured_css)
            self.assertNotIn("@bottom-center", full)


class TestImagesAndBaseUrl(unittest.TestCase):
    """Relative image paths in markdown must resolve against the .md file's
    own directory, and `<img>` must be capped at the page width."""

    def _css(self):
        import md2pdf
        return md2pdf._build_css({
            "regular": "file:///r.ttf",
            "bold": "file:///b.ttf",
            "code": "file:///c.ttf",
        })

    def _block(self, css, selector):
        m = re.search(
            r"(?:^|\})\s*" + re.escape(selector) + r"\s*\{([^}]+)\}",
            css, re.MULTILINE,
        )
        return m.group(1) if m else None

    def test_img_rule_caps_at_page_width(self):
        body = self._block(self._css(), "img")
        self.assertIsNotNone(body, "img must have its own rule")
        self.assertIn("max-width", body)
        self.assertIn("100%", body)
        self.assertIn("height", body)
        self.assertIn("auto", body)

    def test_html_called_with_md_directory_as_base_url(self):
        """`HTML(string=..., base_url=...)` must use the .md file's directory
        so that `![alt](images/foo.png)` resolves correctly regardless of cwd."""
        import md2pdf
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "doc.md")
            Path(md_file).write_text(
                "![logo](images/logo.png)\n\n# 제목\n", encoding="utf-8"
            )
            fake_font = os.path.join(tmpdir, "f.ttf")
            Path(fake_font).write_bytes(b"x")
            out = os.path.join(tmpdir, "out.pdf")

            with mock.patch("md2pdf.HTML") as mock_html, \
                 mock.patch("md2pdf.CSS"), \
                 mock.patch("md2pdf.FontConfiguration"):
                mock_html.return_value.write_pdf.return_value = None
                md2pdf.convert_md_to_pdf(md_file, out, font_path=fake_font)

            mock_html.assert_called_once()
            kwargs = mock_html.call_args.kwargs
            self.assertIn(
                "base_url", kwargs,
                "convert_md_to_pdf must pass base_url so relative image "
                "paths resolve against the .md file's directory",
            )
            self.assertEqual(
                kwargs["base_url"],
                os.path.dirname(os.path.abspath(md_file)),
            )


class TestFontMultiWeight(unittest.TestCase):
    """`_build_css` must register Regular + Bold NanumGothic and a code
    monospace font (D2Coding) so headings/strong render with real bold and
    code blocks use a Korean-aware fixed-width face."""

    def _css(self):
        import md2pdf
        return md2pdf._build_css({
            "regular": "file:///fake/regular.ttf",
            "bold": "file:///fake/bold.ttf",
            "code": "file:///fake/code.ttf",
        })

    def test_at_least_three_font_face_rules(self):
        self.assertGreaterEqual(self._css().count("@font-face"), 3)

    def test_nanumgothic_normal_weight_uses_regular_uri(self):
        block = re.search(
            r"@font-face\s*\{[^}]*?'NanumGothic'[^}]*?font-weight:\s*normal[^}]*?\}",
            self._css(), re.DOTALL,
        )
        self.assertIsNotNone(block, "Need a normal-weight NanumGothic @font-face")
        self.assertIn("file:///fake/regular.ttf", block.group(0))

    def test_nanumgothic_bold_weight_uses_bold_uri(self):
        block = re.search(
            r"@font-face\s*\{[^}]*?'NanumGothic'[^}]*?font-weight:\s*bold[^}]*?\}",
            self._css(), re.DOTALL,
        )
        self.assertIsNotNone(block, "Need a bold-weight NanumGothic @font-face")
        self.assertIn("file:///fake/bold.ttf", block.group(0))

    def test_d2coding_face_uses_code_uri(self):
        block = re.search(
            r"@font-face\s*\{[^}]*?'D2Coding'[^}]*?\}",
            self._css(), re.DOTALL,
        )
        self.assertIsNotNone(block, "Need a D2Coding @font-face")
        self.assertIn("file:///fake/code.ttf", block.group(0))

    def test_code_rule_prefers_d2coding(self):
        m = re.search(r"(?:^|\})\s*code\s*\{([^}]+)\}", self._css(), re.MULTILINE)
        self.assertIsNotNone(m)
        self.assertIn("D2Coding", m.group(1))


class TestEnsureFonts(unittest.TestCase):
    """ensure_fonts() must handle direct .ttf and zip-archived sources, with
    SHA256 verification before any disk write."""

    def test_resources_have_three_known_roles(self):
        import md2pdf
        self.assertEqual(set(md2pdf.FONT_RESOURCES.keys()), {"regular", "bold", "code"})

    def test_returns_existing_files_without_download(self):
        import md2pdf
        with tempfile.TemporaryDirectory() as tmpdir:
            fonts_dir = Path(tmpdir)
            for spec in md2pdf.FONT_RESOURCES.values():
                (fonts_dir / spec.filename).write_bytes(b"cached")

            with mock.patch("urllib.request.urlopen") as mock_open:
                paths = md2pdf.ensure_fonts(fonts_dir=fonts_dir)

            mock_open.assert_not_called()
            self.assertEqual(set(paths.keys()), {"regular", "bold", "code"})

    def test_downloads_plain_and_extracts_zip_member(self):
        """Regular/bold come as plain .ttf; code is shipped inside a zip."""
        import md2pdf

        # Build a fake zip whose internal layout matches the real D2Coding zip
        member_name = md2pdf.FONT_RESOURCES["code"].archive_member
        self.assertTrue(member_name, "Code resource must declare an archive_member")
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            zf.writestr(member_name, b"d2coding bytes")
            zf.writestr("README.txt", b"ignored")
        zip_data = zip_buf.getvalue()

        reg_data = b"regular bytes"
        bold_data = b"bold bytes"

        fake_resources = {
            "regular": md2pdf.FontResource(
                filename="reg.ttf", url="https://x/reg",
                sha256=hashlib.sha256(reg_data).hexdigest(),
            ),
            "bold": md2pdf.FontResource(
                filename="bold.ttf", url="https://x/bold",
                sha256=hashlib.sha256(bold_data).hexdigest(),
            ),
            "code": md2pdf.FontResource(
                filename="code.ttf", url="https://x/code.zip",
                sha256=hashlib.sha256(zip_data).hexdigest(),
                archive_member=member_name,
            ),
        }
        url_to_data = {
            "https://x/reg": reg_data,
            "https://x/bold": bold_data,
            "https://x/code.zip": zip_data,
        }

        class FakeResp:
            def __init__(self, data):
                self._data = data
            def __enter__(self): return self
            def __exit__(self, *a): pass
            def read(self): return self._data

        with tempfile.TemporaryDirectory() as tmpdir:
            fonts_dir = Path(tmpdir)
            with mock.patch.dict(md2pdf.FONT_RESOURCES, fake_resources, clear=True), \
                 mock.patch(
                     "urllib.request.urlopen",
                     side_effect=lambda url: FakeResp(url_to_data[url]),
                 ):
                paths = md2pdf.ensure_fonts(fonts_dir=fonts_dir)

            self.assertEqual((fonts_dir / "reg.ttf").read_bytes(), reg_data)
            self.assertEqual((fonts_dir / "bold.ttf").read_bytes(), bold_data)
            self.assertEqual((fonts_dir / "code.ttf").read_bytes(), b"d2coding bytes")

    def test_sha256_mismatch_raises_and_does_not_write(self):
        import md2pdf

        class FakeResp:
            def __enter__(self): return self
            def __exit__(self, *a): pass
            def read(self): return b"actual data"

        fake_resources = {
            "regular": md2pdf.FontResource(
                filename="reg.ttf", url="https://x/reg",
                sha256="0" * 64,
            ),
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            fonts_dir = Path(tmpdir)
            with mock.patch.dict(md2pdf.FONT_RESOURCES, fake_resources, clear=True), \
                 mock.patch("urllib.request.urlopen", return_value=FakeResp()):
                with self.assertRaises(RuntimeError) as ctx:
                    md2pdf.ensure_fonts(fonts_dir=fonts_dir)

            self.assertIn("integrity", str(ctx.exception).lower())
            self.assertFalse((fonts_dir / "reg.ttf").exists())

    def test_download_failure_raises_runtime_error(self):
        import md2pdf
        fake_resources = {
            "regular": md2pdf.FontResource(
                filename="reg.ttf", url="https://x/reg",
                sha256="0" * 64,
            ),
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            fonts_dir = Path(tmpdir)
            with mock.patch.dict(md2pdf.FONT_RESOURCES, fake_resources, clear=True), \
                 mock.patch("urllib.request.urlopen", side_effect=OSError("net down")):
                with self.assertRaises(RuntimeError) as ctx:
                    md2pdf.ensure_fonts(fonts_dir=fonts_dir)

            self.assertIn("download failed", str(ctx.exception).lower())


def _weasyprint_available() -> bool:
    import md2pdf
    return md2pdf.HTML is not None


@unittest.skipUnless(
    (Path(__file__).parent / "fonts" / "NanumGothic-Regular.ttf").exists(),
    "NanumGothic-Regular.ttf not downloaded — run the script once to trigger download",
)
@unittest.skipUnless(
    _weasyprint_available(),
    "WeasyPrint native libraries (pango/harfbuzz/cairo) not loadable in this env",
)
class TestIntegration(unittest.TestCase):
    """Integration tests requiring the actual font file."""

    def test_real_pdf_generated(self):
        import md2pdf
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            Path(md_file).write_text(
                "# 한국어 테스트\n\n이것은 **PDF 변환** 테스트입니다.\n\n- 항목 1\n- 항목 2\n",
                encoding="utf-8",
            )
            out_pdf = os.path.join(tmpdir, "out.pdf")
            result = md2pdf.convert_md_to_pdf(md_file, out_pdf)
            self.assertTrue(result.exists())
            self.assertGreater(result.stat().st_size, 1000)

    def test_sample_md_converts(self):
        import md2pdf
        sample = Path(__file__).parent / "sample.md"
        if not sample.exists():
            self.skipTest("sample.md not found")
        with tempfile.TemporaryDirectory() as tmpdir:
            out_pdf = os.path.join(tmpdir, "sample.pdf")
            result = md2pdf.convert_md_to_pdf(str(sample), out_pdf)
            self.assertTrue(result.exists())
            self.assertGreater(result.stat().st_size, 1000)


class TestArgParser(unittest.TestCase):
    """Test the argparse-based CLI."""

    def test_input_only(self):
        import md2pdf
        args = md2pdf._build_arg_parser().parse_args(["foo.md"])
        self.assertEqual(args.input, "foo.md")
        self.assertFalse(args.webui)
        self.assertEqual(args.port, 5000)

    def test_webui_with_short_port(self):
        import md2pdf
        args = md2pdf._build_arg_parser().parse_args(["--webui", "-p", "8080"])
        self.assertTrue(args.webui)
        self.assertEqual(args.port, 8080)

    def test_webui_with_long_port(self):
        import md2pdf
        args = md2pdf._build_arg_parser().parse_args(["--webui", "--port", "9000"])
        self.assertTrue(args.webui)
        self.assertEqual(args.port, 9000)

    def test_no_args_prints_help(self):
        import md2pdf
        with mock.patch("sys.stdout"):
            rc = md2pdf.main([])
        self.assertEqual(rc, 0)

    def test_main_dispatches_to_webui(self):
        import md2pdf
        with mock.patch("md2pdf.run_webui") as mock_run:
            md2pdf.main(["--webui", "-p", "1234"])
        mock_run.assert_called_once_with(port=1234)

    def test_default_page_numbers_on(self):
        import md2pdf
        args = md2pdf._build_arg_parser().parse_args(["doc.md"])
        self.assertTrue(args.page_numbers)

    def test_no_page_numbers_flag(self):
        import md2pdf
        args = md2pdf._build_arg_parser().parse_args(["doc.md", "--no-page-numbers"])
        self.assertFalse(args.page_numbers)

    def test_main_passes_no_page_numbers_to_convert(self):
        import md2pdf
        with mock.patch("md2pdf.convert_md_to_pdf") as mock_conv:
            mock_conv.return_value = Path("/tmp/x.pdf")
            md2pdf.main(["doc.md", "out.pdf", "--no-page-numbers"])
        # Inspect the kwargs that main() passed through
        _, kwargs = mock_conv.call_args
        self.assertIn("page_numbers", kwargs)
        self.assertFalse(kwargs["page_numbers"])

    def test_css_flag_parsed(self):
        import md2pdf
        args = md2pdf._build_arg_parser().parse_args(
            ["doc.md", "--css", "custom.css"]
        )
        self.assertEqual(args.css, "custom.css")

    def test_default_css_is_none(self):
        import md2pdf
        args = md2pdf._build_arg_parser().parse_args(["doc.md"])
        self.assertIsNone(args.css)

    def test_main_passes_css_to_convert(self):
        import md2pdf
        with mock.patch("md2pdf.convert_md_to_pdf") as mock_conv:
            mock_conv.return_value = Path("/tmp/x.pdf")
            md2pdf.main(["doc.md", "out.pdf", "--css", "my.css"])
        _, kwargs = mock_conv.call_args
        self.assertEqual(kwargs.get("custom_css"), "my.css")


class TestWebUI(unittest.TestCase):
    """Test the Flask web UI routes with mocked conversion."""

    def setUp(self):
        import md2pdf
        self.md2pdf = md2pdf
        self.app = md2pdf.create_app()
        self.client = self.app.test_client()

    def test_index_renders_form(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_data(as_text=True)
        self.assertIn("md2pdf", body)
        self.assertIn('action="/convert"', body)
        self.assertIn('type="file"', body)

    def test_index_is_mobile_friendly(self):
        resp = self.client.get("/")
        body = resp.get_data(as_text=True)
        self.assertIn('name="viewport"', body)
        self.assertIn("width=device-width", body)

    def test_index_has_drag_and_drop_zone(self):
        resp = self.client.get("/")
        body = resp.get_data(as_text=True)
        self.assertIn("drop-zone", body)
        self.assertIn("dragover", body)

    def test_index_has_loading_overlay_markup(self):
        """An overlay with a spinner must be present in the HTML so JS can
        toggle it during conversion."""
        resp = self.client.get("/")
        body = resp.get_data(as_text=True)
        self.assertIn('id="overlay"', body)
        self.assertIn("spinner", body)
        # Korean progress text — not just an icon
        self.assertIn("변환 중", body)

    def test_index_has_spin_keyframes(self):
        resp = self.client.get("/")
        body = resp.get_data(as_text=True)
        self.assertIn("@keyframes spin", body)

    def test_index_intercepts_form_submit_with_fetch(self):
        """On submit JS must call fetch('/convert') and prevent the default
        full-page navigation so the overlay can stay visible."""
        resp = self.client.get("/")
        body = resp.get_data(as_text=True)
        self.assertIn("preventDefault", body)
        self.assertIn("fetch", body)
        self.assertIn("/convert", body)

    def test_index_has_page_numbers_checkbox(self):
        resp = self.client.get("/")
        body = resp.get_data(as_text=True)
        self.assertIn('name="page_numbers"', body)
        # Checked by default — page numbers ON unless user opts out
        self.assertRegex(body, r'name="page_numbers"[^>]*\schecked')

    def test_convert_disables_page_numbers_when_unchecked(self):
        captured = {}

        def fake_convert(md_path, pdf_path, font_path=None, **kwargs):
            captured.update(kwargs)
            Path(pdf_path).write_bytes(b"%PDF-1.4 fake")
            return Path(pdf_path)

        # Browser submits checked checkboxes only; absence == unchecked
        with mock.patch("md2pdf.convert_md_to_pdf", side_effect=fake_convert):
            data = {"file": (io.BytesIO(b"# hi"), "doc.md")}
            resp = self.client.post(
                "/convert", data=data, content_type="multipart/form-data"
            )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("page_numbers", captured)
        self.assertFalse(captured["page_numbers"])

    def test_index_has_custom_css_input(self):
        resp = self.client.get("/")
        body = resp.get_data(as_text=True)
        self.assertIn('name="custom_css"', body)
        # Hint that .css files are accepted
        self.assertIn(".css", body)

    def test_convert_with_custom_css_passes_path(self):
        captured = {}

        def fake_convert(md_path, pdf_path, font_path=None, **kwargs):
            captured.update(kwargs)
            captured["md_path"] = md_path
            Path(pdf_path).write_bytes(b"%PDF-1.4 fake")
            return Path(pdf_path)

        with mock.patch("md2pdf.convert_md_to_pdf", side_effect=fake_convert):
            data = {
                "file": (io.BytesIO(b"# hi"), "doc.md"),
                "custom_css": (io.BytesIO(b"body { color: red; }"), "style.css"),
            }
            resp = self.client.post(
                "/convert", data=data, content_type="multipart/form-data"
            )

        self.assertEqual(resp.status_code, 200)
        self.assertIn("custom_css", captured)
        self.assertIsNotNone(captured["custom_css"])
        # The path should exist when convert_md_to_pdf is called
        # (it'll be cleaned up after but the side_effect ran during the call)
        self.assertTrue(captured["custom_css"].endswith(".css"))

    def test_convert_without_custom_css_passes_none(self):
        captured = {}

        def fake_convert(md_path, pdf_path, font_path=None, **kwargs):
            captured.update(kwargs)
            Path(pdf_path).write_bytes(b"%PDF-1.4 fake")
            return Path(pdf_path)

        with mock.patch("md2pdf.convert_md_to_pdf", side_effect=fake_convert):
            data = {"file": (io.BytesIO(b"# hi"), "doc.md")}
            resp = self.client.post(
                "/convert", data=data, content_type="multipart/form-data"
            )

        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(captured.get("custom_css"))

    def test_convert_enables_page_numbers_when_checked(self):
        captured = {}

        def fake_convert(md_path, pdf_path, font_path=None, **kwargs):
            captured.update(kwargs)
            Path(pdf_path).write_bytes(b"%PDF-1.4 fake")
            return Path(pdf_path)

        with mock.patch("md2pdf.convert_md_to_pdf", side_effect=fake_convert):
            data = {
                "file": (io.BytesIO(b"# hi"), "doc.md"),
                "page_numbers": "on",
            }
            resp = self.client.post(
                "/convert", data=data, content_type="multipart/form-data"
            )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(captured.get("page_numbers"))

    def test_convert_success(self):
        def fake_convert(md_path, pdf_path, font_path=None, **kwargs):
            Path(pdf_path).write_bytes(b"%PDF-1.4 fake pdf bytes")
            return Path(pdf_path)

        with mock.patch("md2pdf.convert_md_to_pdf", side_effect=fake_convert):
            data = {"file": (io.BytesIO("# 한국어 제목".encode("utf-8")), "doc.md")}
            resp = self.client.post(
                "/convert", data=data, content_type="multipart/form-data"
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, "application/pdf")
        self.assertTrue(resp.data.startswith(b"%PDF"))
        cd = resp.headers.get("Content-Disposition", "")
        self.assertIn("doc.pdf", cd)

    def test_convert_rejects_non_md_extension(self):
        data = {"file": (io.BytesIO(b"not markdown"), "evil.txt")}
        resp = self.client.post(
            "/convert", data=data, content_type="multipart/form-data"
        )
        self.assertEqual(resp.status_code, 400)
        body = resp.get_data(as_text=True)
        self.assertIn("Markdown", body)
        self.assertIn("에러", body)

    def test_convert_missing_file_shows_error(self):
        resp = self.client.post(
            "/convert", data={}, content_type="multipart/form-data"
        )
        self.assertEqual(resp.status_code, 400)
        body = resp.get_data(as_text=True)
        self.assertIn("업로드", body)

    def test_convert_runtime_error_shows_notification(self):
        with mock.patch(
            "md2pdf.convert_md_to_pdf",
            side_effect=RuntimeError("PDF conversion failed: boom"),
        ):
            data = {"file": (io.BytesIO(b"# hi"), "x.md")}
            resp = self.client.post(
                "/convert", data=data, content_type="multipart/form-data"
            )

        self.assertEqual(resp.status_code, 500)
        body = resp.get_data(as_text=True)
        self.assertIn("변환 실패", body)
        self.assertIn("boom", body)


class TestYamlFrontmatterStripping(unittest.TestCase):
    """Pandoc-style YAML metadata blocks (`---\\n...\\n---\\n` at the very
    top of the file) must be stripped before python-markdown sees the text;
    otherwise the leading `---` is parsed as a horizontal rule and the
    metadata leaks into the body as a paragraph."""

    def test_yaml_frontmatter_at_top_is_removed(self):
        import md2pdf
        md = (
            '---\n'
            'title: "Test"\n'
            'author: A\n'
            'documentclass: book\n'
            '---\n\n'
            '# 머리말\n\n'
            '본문 내용.\n'
        )
        html = md2pdf._render_html(md)
        self.assertNotIn("title:", html)
        self.assertNotIn("documentclass", html)
        self.assertNotIn("author:", html)
        self.assertIn("머리말", html)
        self.assertIn("본문 내용", html)

    def test_yaml_frontmatter_with_dotdotdot_terminator(self):
        """Pandoc allows the closing fence to be `...` instead of `---`."""
        import md2pdf
        md = '---\ntitle: T\n...\n\n# Body\n'
        html = md2pdf._render_html(md)
        self.assertNotIn("title:", html)
        self.assertIn("Body", html)

    def test_no_frontmatter_passthrough(self):
        import md2pdf
        html = md2pdf._render_html("# Hello\n\nBody.\n")
        self.assertIn("Hello", html)
        self.assertIn("Body", html)

    def test_horizontal_rule_in_body_preserved(self):
        """Three dashes mid-document is a horizontal rule, NOT frontmatter."""
        import md2pdf
        md = "# Hello\n\nBefore.\n\n---\n\nAfter.\n"
        html = md2pdf._render_html(md)
        self.assertIn("<hr", html)
        self.assertIn("Before", html)
        self.assertIn("After", html)

    def test_first_heading_after_frontmatter_renders(self):
        """Regression: ensure the heading right after stripped frontmatter
        is parsed as a heading (i.e. the strip consumes the trailing newline)."""
        import md2pdf
        md = '---\ntitle: T\n---\n\n# Heading\n'
        html = md2pdf._render_html(md)
        self.assertRegex(html, r"<h1[^>]*>Heading</h1>")


class TestLatexPageBreakCommands(unittest.TestCase):
    """Pandoc/LaTeX hard page-break commands (`\\newpage`, `\\pagebreak`) on
    a line of their own become `<div class="page"></div>` so the existing
    `.page { page-break-after: always }` CSS triggers a real page break."""

    def test_newpage_becomes_page_div(self):
        import md2pdf
        md = "A\n\n\\newpage\n\nB\n"
        html = md2pdf._render_html(md)
        self.assertIn('class="page"', html)
        self.assertNotIn(r'\newpage', html)

    def test_pagebreak_becomes_page_div(self):
        import md2pdf
        md = "A\n\n\\pagebreak\n\nB\n"
        html = md2pdf._render_html(md)
        self.assertIn('class="page"', html)
        self.assertNotIn(r'\pagebreak', html)

    def test_indented_newpage_still_converted(self):
        import md2pdf
        md = "A\n\n   \\newpage   \n\nB\n"
        html = md2pdf._render_html(md)
        self.assertIn('class="page"', html)
        self.assertNotIn(r'\newpage', html)

    def test_newpage_within_text_left_alone(self):
        """`\\newpage` embedded mid-sentence is not a hard break — leave it."""
        import md2pdf
        md = "이 코드는 \\newpage 명령을 사용한다.\n"
        html = md2pdf._render_html(md)
        self.assertNotIn('class="page"', html)

    def test_multiple_newpages_each_convert(self):
        import md2pdf
        md = "A\n\n\\newpage\n\nB\n\n\\newpage\n\nC\n"
        html = md2pdf._render_html(md)
        self.assertEqual(html.count('class="page"'), 2)


class TestLeadingPageBreakStripped(unittest.TestCase):
    """A `\\newpage` *before any content* would render a blank first page —
    the page-break fires with nothing on the page above it. Pandoc authors
    commonly write `\\newpage` immediately after the YAML metadata block
    expecting Pandoc to fill the first page with a title page rendered from
    the metadata; we don't, so the leading page-break must be stripped."""

    def test_leading_newpage_after_frontmatter_dropped(self):
        import md2pdf
        md = '---\ntitle: T\n---\n\n\\newpage\n\n# 머리말\n\nBody.\n'
        html = md2pdf._render_html(md)
        # No page break before the first heading
        self.assertNotRegex(html, r'class="page"[^<]*</div>\s*<h1')
        self.assertIn("머리말", html)

    def test_leading_newpage_at_document_start_dropped(self):
        """Even without frontmatter, a `\\newpage` at the very top makes
        page 1 blank."""
        import md2pdf
        md = '\\newpage\n\n# Title\n\nBody.\n'
        html = md2pdf._render_html(md)
        self.assertNotIn('class="page"', html)
        self.assertIn("Title", html)

    def test_multiple_leading_newpages_all_dropped(self):
        import md2pdf
        md = '---\ntitle: T\n---\n\n\\newpage\n\n\\pagebreak\n\n# Title\n'
        html = md2pdf._render_html(md)
        self.assertNotIn('class="page"', html)

    def test_newpage_after_real_content_preserved(self):
        """Regression: only the leading run is dropped — page breaks between
        chapters must still fire."""
        import md2pdf
        md = '# Chapter 1\n\nBody.\n\n\\newpage\n\n# Chapter 2\n'
        html = md2pdf._render_html(md)
        self.assertIn('class="page"', html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
