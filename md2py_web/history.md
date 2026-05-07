# Change History — md2py_web

## 2026-05-07 — 한글 파일명 보존 (PDF 저장 시 파일명 유지)

### 증상
Web UI에서 한글이 포함된 `.md` 파일(예: `한글파일.md`)을 업로드해 변환 후 "브라우저에서 인쇄 → PDF 저장"을 누르면, 저장 다이얼로그의 기본 파일명에서 한글이 사라지거나 익명의 blob UUID가 제안됨. 결과적으로 사용자는 매번 파일명을 직접 다시 타이핑해야 했음.

### 원인
1. UI가 `title`로 **파일명 전체**(`한글파일.md`)를 서버에 보내, iframe `<title>`이 `한글파일.md`로 설정됨 — 저장 시 `.md`가 본문에 끼어 들어가 `한글파일.md.pdf` 형태가 됨.
2. iframe의 src가 `URL.createObjectURL(blob)`로 만든 `blob:...UUID` URL이라, Chromium이 인쇄 대상 sub-frame의 제안 파일명을 결정할 때 iframe document의 `<title>` 대신 URL slug나 iframe element의 `name` 속성에 의존하는 경로로 빠지면서 한글이 누락됨.
3. iframe element의 `name` 속성이 비어 있어 fallback 경로에서도 의미 있는 이름을 얻을 수 없음.

### 수정 (`src/ui.ts`)
1. `file.name`에서 `\.(md|markdown)$` 확장자를 제거한 `stem`을 계산. 빈 문자열이면 `'document'`로 fallback.
2. POST `/convert` 본문의 `title`로 **stem만** 전달 → iframe `<title>`이 `한글파일`로 설정되어 저장 파일명이 `한글파일.pdf`가 됨.
3. blob URL 할당 직전에 `preview.name = stem` 설정 → Chromium의 sub-frame 인쇄 파일명 결정 우선순위에서 가장 안정적인 소스(iframe element의 `name`)에 한글 stem을 직접 주입.

### TDD
1. `tests/ui.test.ts` 신규 4건 (RED 4):
   - `.md`/`.markdown` 확장자 strip 정규식 존재
   - `title: stem` 전송
   - `preview.name = stem` 설정
   - `... || 'document'` fallback
2. `ui.ts` 수정 후 GREEN, 전체 49건 회귀 없음 (기존 45건 + 신규 4건).
3. 라이브 스모크: `node dist/src/index.js --webui -p 5901` 후 `curl /` 응답에서 `stem` 계산, `title: stem` 본문, `preview.name = stem` 모두 노출 확인.

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
