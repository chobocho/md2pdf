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

test("UI assigns the iframe `name` attribute to the filename stem", () => {
  // Chromium uses the iframe element's `name` attribute as the suggested
  // filename when printing a sub-frame to PDF. Setting it ensures Korean
  // filenames survive the Save-as dialog.
  assert.match(
    UI_HTML,
    /preview\.name\s*=\s*stem/,
    "expected `preview.name = stem` to be set before printing"
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
