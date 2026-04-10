# md2py_web

A **TypeScript port of [md2pdf](../README.md)** with **zero runtime
dependencies**. Converts Markdown to a printable HTML document — use your
browser's *Print → Save as PDF* to produce a PDF (this preserves Korean
text via the browser's installed CJK fonts).

> Why HTML instead of PDF bytes?  Generating real PDFs that support
> Korean requires embedding a CJK font, which would force a runtime
> dependency on a font/PDF library. By targeting printable HTML and
> letting the browser handle PDF export, md2py_web stays 100% built-in
> Node — no `npm install` is needed for end users.

## Features

- Pure TypeScript / Node.js — runtime uses only `node:http`, `node:fs`,
  `node:readline`, etc. No npm packages at runtime.
- Self-contained Markdown parser (headings, paragraphs, bold, italic,
  inline & fenced code, ordered/unordered lists, links, blockquotes,
  horizontal rules, HTML escaping, Korean preserved).
- Web UI mode (`--webui`) with file upload, preview, error notifications.
- Console `exit` command terminates the running web server cleanly.
- CLI batch mode for `.md → .html` conversion.
- 45 unit + integration tests via Node's built-in `node:test`.
- TDD: tests were written before the implementation.

## Requirements

- Node.js ≥ 18 (for built-in `node:test` and ESM support)
- TypeScript 5.x (build-time only — devDependency)

## Quick Start

```bash
# Build & test
./build.sh

# Web UI on default port 8080
./release/run.sh --webui

# Web UI on a custom port
./release/run.sh --webui -p 5000

# Batch CLI: convert one file
./release/run.sh input.md output.html
```

While the web UI is running, type `exit` (Enter) in the console to
terminate the server.

## CLI

```
md2py_web — Markdown ➜ printable HTML / PDF

Usage:
  md2py_web <input.md> [output.html]
  md2py_web --webui [-p <port>]
  md2py_web --help

Options:
  --webui          Start the web UI server.
  -p, --port N     Web UI port (default: 8080).
  -h, --help       Show this help message.
```

## Web UI

```
GET  /          → Upload form (HTML page)
GET  /health    → {"ok": true}
POST /convert   → JSON {markdown, title?} → JSON {html} or {error}
```

Errors are reported **both** in the browser (red banner) and on stderr.
Body size is capped at 8 MiB by default.

## Development

```bash
# Install dev tooling (typescript + @types/node)
npm install

# Compile + run tests
npm test

# Compile only
npm run build

# Run from source build
node dist/src/index.js --webui
```

### Layout

```
md2py_web/
├── src/
│   ├── markdown.ts   # MD → HTML parser (no deps)
│   ├── html.ts       # Document wrapper + print CSS
│   ├── server.ts     # node:http server
│   ├── cli.ts        # argv parser
│   ├── ui.ts         # embedded upload UI
│   └── index.ts      # entry point
├── tests/
│   ├── markdown.test.ts
│   ├── html.test.ts
│   ├── cli.test.ts
│   └── server.test.ts
├── tsconfig.json
├── package.json
├── build.sh          # produces release/
└── README.md
```

### Test summary

```
$ npm test
✔ 45 tests passing  (markdown 22 · html 6 · cli 10 · server 7)
```

## build.sh

`./build.sh` performs:

1. `rm -rf dist release`
2. `npx tsc` — compile to `dist/`
3. `node --test dist/tests/*.test.js` — run all tests
4. Assemble `release/` containing `dist/` (compiled `src/` only),
   `README.md`, `history.md`, `package.json`, and a `run.sh` launcher.

The release folder is fully self-contained and can be copied/zipped as a
deliverable.

## Limitations

- The output is **printable HTML**, not a binary PDF. Use a browser's
  *Print → Save as PDF* to obtain a PDF file. (This is the trade-off
  for the zero-runtime-deps constraint while still supporting Korean.)
- The Markdown parser is intentionally minimal: no tables, no nested
  lists, no GitHub-flavored extras like task lists or autolinks.

## License

MIT. See `../LICENSE` of the parent repository.
