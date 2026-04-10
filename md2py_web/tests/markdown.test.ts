import { test } from "node:test";
import assert from "node:assert/strict";
import { mdToHtml } from "../src/markdown.js";

test("h1 heading", () => {
  assert.equal(mdToHtml("# Title"), "<h1>Title</h1>");
});

test("h2 through h6 headings", () => {
  assert.match(mdToHtml("## Two"), /<h2>Two<\/h2>/);
  assert.match(mdToHtml("### Three"), /<h3>Three<\/h3>/);
  assert.match(mdToHtml("#### Four"), /<h4>Four<\/h4>/);
  assert.match(mdToHtml("##### Five"), /<h5>Five<\/h5>/);
  assert.match(mdToHtml("###### Six"), /<h6>Six<\/h6>/);
});

test("paragraph wraps plain text", () => {
  assert.equal(mdToHtml("hello world"), "<p>hello world</p>");
});

test("two paragraphs separated by blank line", () => {
  const out = mdToHtml("first\n\nsecond");
  assert.match(out, /<p>first<\/p>/);
  assert.match(out, /<p>second<\/p>/);
});

test("bold inline **text**", () => {
  assert.equal(mdToHtml("**bold**"), "<p><strong>bold</strong></p>");
});

test("italic inline *text*", () => {
  assert.equal(mdToHtml("*it*"), "<p><em>it</em></p>");
});

test("inline code with backticks", () => {
  assert.equal(mdToHtml("`x`"), "<p><code>x</code></p>");
});

test("fenced code block preserves content verbatim", () => {
  const md = "```\nlet x = 1;\n```";
  const out = mdToHtml(md);
  assert.match(out, /<pre><code>[\s\S]*let x = 1;[\s\S]*<\/code><\/pre>/);
});

test("fenced code block with language tag", () => {
  const md = "```js\nconst a = 1;\n```";
  const out = mdToHtml(md);
  assert.match(out, /<pre><code class="language-js">[\s\S]*const a = 1;/);
});

test("unordered list", () => {
  const out = mdToHtml("- a\n- b\n- c");
  assert.match(out, /<ul>/);
  assert.match(out, /<li>a<\/li>/);
  assert.match(out, /<li>b<\/li>/);
  assert.match(out, /<li>c<\/li>/);
  assert.match(out, /<\/ul>/);
});

test("ordered list", () => {
  const out = mdToHtml("1. one\n2. two");
  assert.match(out, /<ol>/);
  assert.match(out, /<li>one<\/li>/);
  assert.match(out, /<li>two<\/li>/);
});

test("link inline", () => {
  const out = mdToHtml("[Anthropic](https://anthropic.com)");
  assert.match(out, /<a href="https:\/\/anthropic\.com">Anthropic<\/a>/);
});

test("blockquote", () => {
  assert.match(mdToHtml("> quoted"), /<blockquote>quoted<\/blockquote>/);
});

test("horizontal rule", () => {
  assert.match(mdToHtml("---"), /<hr ?\/?>/);
});

test("html escaping in plain text", () => {
  const out = mdToHtml("a < b & c > d");
  assert.match(out, /a &lt; b &amp; c &gt; d/);
});

test("html escaping inside inline code", () => {
  const out = mdToHtml("`<script>`");
  assert.match(out, /<code>&lt;script&gt;<\/code>/);
});

test("Korean text is preserved", () => {
  const out = mdToHtml("# 한국어 제목\n\n안녕하세요");
  assert.match(out, /<h1>한국어 제목<\/h1>/);
  assert.match(out, /<p>안녕하세요<\/p>/);
});

test("bold and italic mixed in paragraph", () => {
  const out = mdToHtml("normal **bold** and *italic*");
  assert.match(out, /<strong>bold<\/strong>/);
  assert.match(out, /<em>italic<\/em>/);
});

test("multiple headings produce ordered output", () => {
  const out = mdToHtml("# A\n## B\n### C");
  const aIdx = out.indexOf("<h1>A</h1>");
  const bIdx = out.indexOf("<h2>B</h2>");
  const cIdx = out.indexOf("<h3>C</h3>");
  assert.ok(aIdx >= 0 && bIdx > aIdx && cIdx > bIdx);
});

test("empty input produces empty string", () => {
  assert.equal(mdToHtml(""), "");
  assert.equal(mdToHtml("\n\n\n"), "");
});

test("fenced code block does not interpret markdown inside", () => {
  const md = "```\n**not bold**\n```";
  const out = mdToHtml(md);
  assert.match(out, /\*\*not bold\*\*/);
  assert.doesNotMatch(out, /<strong>/);
});

test("inline code is not parsed for markdown", () => {
  const out = mdToHtml("`**still code**`");
  assert.match(out, /<code>\*\*still code\*\*<\/code>/);
  assert.doesNotMatch(out, /<strong>/);
});
