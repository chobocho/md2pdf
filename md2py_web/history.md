# Change History — md2py_web

## 2026-04-10 — Initial TypeScript port of md2pdf

### Goal

Port the Python md2pdf project to TypeScript with the strict constraint
of **zero runtime external dependencies** (Node.js built-ins only).
Korean support remains a first-class requirement.

### Design

- Output target switched from binary PDF to **printable HTML** with a
  `@media print` stylesheet. This avoids the need for a font-embedding
  PDF library at runtime; users print → Save as PDF in the browser,
  which uses installed CJK fonts (Noto/Malgun/NanumGothic, etc.) for
  perfect Korean rendering.
- TypeScript compiler is a **build-time** dependency only. The shipped
  release contains plain `.js` files that import nothing outside of
  `node:*` and the local package.

### Modules

| File              | Responsibility                                                  |
|-------------------|-----------------------------------------------------------------|
| `src/markdown.ts` | Pure Markdown → HTML parser. Headings, paragraphs, bold, italic, inline & fenced code, lists, links, blockquotes, hr, HTML escaping. |
| `src/html.ts`     | Wraps body HTML in a full document with print-friendly CSS.     |
| `src/server.ts`   | `node:http` server with `GET /`, `GET /health`, `POST /convert`, body-size cap, JSON error responses logged to stderr. |
| `src/cli.ts`      | Pure `parseArgs()` for `--webui`, `-p/--port`, positional input/output, `--help`. |
| `src/ui.ts`       | Embedded upload page (form + fetch + preview + Korean error banners). |
| `src/index.ts`    | Entry point. Dispatches CLI vs web UI; installs the stdin `exit` watcher and SIGINT/SIGTERM hooks. |

### TDD

Tests were written **first** under `tests/` before the source files,
then the implementation made them pass. Final counts:

| Suite                   | Tests | Notes                                                |
|-------------------------|------:|------------------------------------------------------|
| `markdown.test.ts`      |   22  | Each Markdown construct + escaping + Korean         |
| `html.test.ts`          |    6  | doctype, title escape, print CSS, charset           |
| `cli.test.ts`           |   10  | All flags, defaults, error cases                    |
| `server.test.ts`        |    7  | All routes, JSON errors, body-size 413               |
| **Total**               | **45**| `npm test` → all passing                            |

Test runner: built-in `node:test` + `node:assert/strict`. No mocha,
no jest, no chai — zero test deps either.

### Build pipeline

`./build.sh` performs clean → `npx tsc` → run all tests on the freshly
compiled output → assemble `release/` with the compiled `src/` only,
`README.md`, `history.md`, a slim `package.json`, and a `run.sh`
launcher. The release folder is self-contained.

### Verification

- 45/45 tests pass (`node --test dist/tests/*.test.js`).
- Live smoke test:
  - `node dist/src/index.js --webui -p 5199` → curl `GET /` 200,
    `GET /health` 200 (`{"ok":true}`), `POST /convert` 200.
  - SIGTERM cleanly shuts down the server.
  - Console `exit` command also terminates via the readline watcher.
- CLI smoke test:
  - `node dist/src/index.js test.md test.html` produces a
    full HTML document containing the Korean source intact.
- Independent reviewer (Explore agent) confirmed:
  - All `import` statements use `node:*` or local relative paths.
  - `package.json#dependencies` is empty.
  - `tsconfig.strict` is true; build succeeds without errors.
  - No `any`, no swallowed errors, no unbounded loops.

### Files added

```
md2py_web/
  src/{markdown,html,server,cli,ui,index}.ts
  tests/{markdown,html,cli,server}.test.ts
  tsconfig.json
  package.json
  .gitignore
  build.sh
  README.md
  history.md
```

### Limitations (acknowledged)

- The Markdown parser does not support tables, nested lists, footnotes,
  task lists, or other GitHub-flavored extensions. Adding any of these
  is straightforward but was out of scope for v0.1.
- The output is HTML, not a binary PDF — see the README for the
  rationale (zero-runtime-deps + Korean support).
