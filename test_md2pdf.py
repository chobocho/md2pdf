import hashlib
import io
import os
import tempfile
import unittest
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


class TestEnsureFont(unittest.TestCase):
    """Test ensure_font() behavior."""

    def test_returns_existing_font(self):
        import md2pdf
        with tempfile.TemporaryDirectory() as tmpdir:
            fonts_dir = Path(tmpdir)
            fake_font = fonts_dir / md2pdf.FONT_FILENAME
            fake_font.write_bytes(b"fake font data")

            with mock.patch("urllib.request.urlretrieve") as mock_dl:
                result = md2pdf.ensure_font(fonts_dir=fonts_dir)

            mock_dl.assert_not_called()
            self.assertEqual(result, fake_font)

    def test_downloads_when_missing(self):
        import md2pdf
        with tempfile.TemporaryDirectory() as tmpdir:
            fonts_dir = Path(tmpdir)
            dest = fonts_dir / md2pdf.FONT_FILENAME

            def fake_download(url, path):
                Path(path).write_bytes(b"font data")

            with mock.patch("urllib.request.urlretrieve", side_effect=fake_download):
                with mock.patch("md2pdf._verify_sha256", return_value=True):
                    result = md2pdf.ensure_font(fonts_dir=fonts_dir)

            self.assertTrue(result.exists())

    def test_sha256_mismatch_raises_and_cleans_up(self):
        import md2pdf
        with tempfile.TemporaryDirectory() as tmpdir:
            fonts_dir = Path(tmpdir)
            dest = fonts_dir / md2pdf.FONT_FILENAME

            def fake_download(url, path):
                Path(path).write_bytes(b"corrupted data")

            with mock.patch("urllib.request.urlretrieve", side_effect=fake_download):
                with mock.patch("md2pdf._verify_sha256", return_value=False):
                    with self.assertRaises(RuntimeError) as ctx:
                        md2pdf.ensure_font(fonts_dir=fonts_dir)

            self.assertIn("integrity check failed", str(ctx.exception))
            self.assertFalse(dest.exists())

    def test_download_failure_cleans_up(self):
        import md2pdf
        with tempfile.TemporaryDirectory() as tmpdir:
            fonts_dir = Path(tmpdir)
            dest = fonts_dir / md2pdf.FONT_FILENAME

            def failing_download(url, path):
                Path(path).write_bytes(b"partial")
                raise OSError("Network error")

            with mock.patch("urllib.request.urlretrieve", side_effect=failing_download):
                with self.assertRaises(RuntimeError) as ctx:
                    md2pdf.ensure_font(fonts_dir=fonts_dir)

            self.assertIn("download failed", str(ctx.exception))
            self.assertFalse(dest.exists())


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

            with mock.patch("md2pdf.HTML") as mock_html:
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

            with mock.patch("md2pdf.HTML") as mock_html:
                with mock.patch("md2pdf.CSS", side_effect=capture_css):
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

            with mock.patch("md2pdf.HTML") as mock_html:
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


@unittest.skipUnless(
    (Path(__file__).parent / "fonts" / "NanumGothic-Regular.ttf").exists(),
    "NanumGothic-Regular.ttf not downloaded — run the script once to trigger download",
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

    def test_convert_success(self):
        def fake_convert(md_path, pdf_path, font_path=None):
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
