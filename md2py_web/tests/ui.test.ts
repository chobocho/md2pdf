import { test } from "node:test";
import assert from "node:assert/strict";
import { UI_HTML } from "../src/ui.js";

test("UI strips .md / .markdown extension before using filename as title", () => {
  // The embedded JS must compute a stem (without .md/.markdown) so that the
  // saved PDF filename does not become e.g. "한글파일.md.pdf".
  assert.match(
    UI_HTML,
    /\.replace\(\s*\/\\\.\(md\|markdown\)\$\/i\s*,\s*['"]['"]\s*\)/,
    "expected file.name.replace(/\\.(md|markdown)$/i, '') in UI script"
  );
});

test("UI sends the filename stem (not full filename) as title", () => {
  // The body of POST /convert should pass `title: stem` so the iframe
  // <title> contains the clean stem only.
  assert.match(
    UI_HTML,
    /title:\s*stem/,
    "expected `title: stem` in fetch body"
  );
});

test("UI does NOT assign the iframe `name` to the stem (Chromium sanitizes non-ASCII to `_`)", () => {
  // Setting iframe.name to a Korean stem causes Chromium to replace every
  // non-ASCII character with `_` when computing the print filename, which
  // collapses 한글파일 → `_.pdf`. The iframe document's <title> is the
  // correct filename source and must not be shadowed by `name`.
  assert.doesNotMatch(
    UI_HTML,
    /preview\.name\s*=\s*stem/,
    "preview.name must not be assigned the stem (Korean → `_` sanitization)"
  );
});

test("UI uses srcdoc (not blob URL) so the iframe <title> drives the print filename", () => {
  // Loading via blob: URL makes Chromium fall back to URL-based filename
  // hints. With srcdoc, the iframe is same-origin to the parent and the
  // iframe document's <title> is used as the suggested PDF filename.
  assert.match(
    UI_HTML,
    /preview\.srcdoc\s*=\s*data\.html/,
    "expected `preview.srcdoc = data.html` for reliable Korean filename"
  );
  assert.doesNotMatch(
    UI_HTML,
    /URL\.createObjectURL/,
    "blob URL approach must be removed in favor of srcdoc"
  );
});

test("UI falls back to a default name when stem would be empty", () => {
  // If a user uploads ".md" (rare but possible), stem is "" — we should
  // not pass an empty title/name. Fallback to a non-empty default.
  assert.match(
    UI_HTML,
    /\)\s*\|\|\s*['"]document['"]/,
    "expected `... || 'document'` fallback when computing stem"
  );
});
