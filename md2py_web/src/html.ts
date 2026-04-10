/**
 * Wrap rendered body HTML in a full printable HTML document.
 * Zero runtime dependencies.
 */

import { escapeHtml } from "./markdown.js";

const PRINT_CSS = `
  :root { color-scheme: light; }
  body {
    font-family: "Noto Sans CJK KR", "Malgun Gothic", "Apple SD Gothic Neo",
                 "NanumGothic", system-ui, -apple-system, sans-serif;
    line-height: 1.7;
    color: #222;
    max-width: 780px;
    margin: 40px auto;
    padding: 0 24px;
    word-break: keep-all;
    overflow-wrap: break-word;
  }
  h1, h2, h3, h4, h5, h6 { color: #111; margin-top: 1.6em; margin-bottom: 0.5em; }
  h1 { font-size: 2em; border-bottom: 2px solid #ddd; padding-bottom: 0.3em; }
  h2 { font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 0.2em; }
  p { margin: 0.8em 0; }
  pre {
    background: #f5f5f5;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 12px 14px;
    overflow-x: auto;
    font-size: 0.92em;
  }
  code { font-family: ui-monospace, "Cascadia Code", "Consolas", monospace; }
  p code, li code { background: #f5f5f5; padding: 1px 5px; border-radius: 3px; }
  blockquote {
    border-left: 4px solid #ccc;
    color: #555;
    margin: 0;
    padding: 4px 16px;
  }
  ul, ol { padding-left: 1.6em; }
  hr { border: none; border-top: 1px solid #ddd; margin: 28px 0; }
  a { color: #0066cc; }
  table { border-collapse: collapse; width: 100%; margin: 16px 0; }
  th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
  th { background: #f2f2f2; }

  @media print {
    body { margin: 0; padding: 0 16mm; max-width: none; }
    h1 { page-break-before: auto; }
    h1, h2, h3 { page-break-after: avoid; }
    pre, blockquote, table { page-break-inside: avoid; }
    a { color: #000; text-decoration: none; }
    @page { margin: 18mm; }
  }
`;

export function wrapDocument(bodyHtml: string, title: string): string {
  const safeTitle = escapeHtml(title);
  return `<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${safeTitle}</title>
<style>${PRINT_CSS}</style>
</head>
<body>
${bodyHtml}
</body>
</html>`;
}
