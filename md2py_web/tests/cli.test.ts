import { test } from "node:test";
import assert from "node:assert/strict";
import { parseArgs } from "../src/cli.js";

test("no args → help mode", () => {
  const r = parseArgs([]);
  assert.equal(r.mode, "help");
});

test("--help / -h → help mode", () => {
  assert.equal(parseArgs(["--help"]).mode, "help");
  assert.equal(parseArgs(["-h"]).mode, "help");
});

test("--webui without port → web mode, default port 8080", () => {
  const r = parseArgs(["--webui"]);
  assert.equal(r.mode, "web");
  assert.equal(r.port, 8080);
});

test("--webui -p 3000 → web mode port 3000", () => {
  const r = parseArgs(["--webui", "-p", "3000"]);
  assert.equal(r.mode, "web");
  assert.equal(r.port, 3000);
});

test("--webui --port 9000 → web mode port 9000", () => {
  const r = parseArgs(["--webui", "--port", "9000"]);
  assert.equal(r.mode, "web");
  assert.equal(r.port, 9000);
});

test("input file only → cli mode, input set, no output", () => {
  const r = parseArgs(["doc.md"]);
  assert.equal(r.mode, "cli");
  assert.equal(r.input, "doc.md");
  assert.equal(r.output, undefined);
});

test("input + output → cli mode, both set", () => {
  const r = parseArgs(["doc.md", "out.html"]);
  assert.equal(r.mode, "cli");
  assert.equal(r.input, "doc.md");
  assert.equal(r.output, "out.html");
});

test("port flag without value → error mode with message", () => {
  const r = parseArgs(["--webui", "-p"]);
  assert.equal(r.mode, "error");
  assert.match(r.error || "", /port/i);
});

test("non-numeric port → error mode", () => {
  const r = parseArgs(["--webui", "-p", "abc"]);
  assert.equal(r.mode, "error");
});

test("unknown flag → error mode", () => {
  const r = parseArgs(["--unknown"]);
  assert.equal(r.mode, "error");
});
