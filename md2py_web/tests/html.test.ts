import { test } from "node:test";
import assert from "node:assert/strict";
import { wrapDocument } from "../src/html.js";

test("wrapDocument returns a full HTML document", () => {
  const out = wrapDocument("<p>hi</p>", "Test");
  assert.match(out, /<!doctype html>/i);
  assert.match(out, /<html[^>]*>/);
  assert.match(out, /<head>/);
  assert.match(out, /<body[^>]*>/);
  assert.match(out, /<\/html>/);
});

test("wrapDocument injects the title", () => {
  const out = wrapDocument("<p>hi</p>", "MyDoc");
  assert.match(out, /<title>MyDoc<\/title>/);
});

test("wrapDocument injects the body html", () => {
  const out = wrapDocument("<p>UNIQUE_BODY_TOKEN</p>", "T");
  assert.match(out, /UNIQUE_BODY_TOKEN/);
});

test("wrapDocument includes print CSS for PDF export", () => {
  const out = wrapDocument("<p>hi</p>", "T");
  assert.match(out, /<style[\s\S]*@media print/);
});

test("wrapDocument declares utf-8 charset for Korean", () => {
  const out = wrapDocument("<p>한글</p>", "한글 문서");
  assert.match(out, /<meta charset=["']?utf-8/i);
  assert.match(out, /한글/);
});

test("wrapDocument escapes title HTML special chars", () => {
  const out = wrapDocument("<p>x</p>", "<evil>");
  assert.match(out, /<title>&lt;evil&gt;<\/title>/);
});
