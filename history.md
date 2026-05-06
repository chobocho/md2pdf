# Change History

## 2026-05-06 — Pandoc 호환성: YAML 프론트매터·`\newpage` 처리

### 증상
`scheme-book-full.md`(Pandoc 스타일 원고)를 변환했을 때:
1. YAML 메타데이터 블록(`---\ntitle: …\n---`)이 PDF 첫 페이지에 본문 단락으로 그대로 노출.
   - 첫 `---`이 `<hr>`로, 둘째 `---`이 setext h2로 파싱되고 그 사이가 일반 단락이 되어버림.
2. 본문 곳곳에 등장하는 `\newpage`(53회) 강제 페이지 분리 지시어가 그대로 텍스트로 인쇄되고 페이지가 넘어가지 않음.

### 원인
`_preprocess_markdown`이 Pandoc 메타데이터 블록과 LaTeX 페이지 분리 명령을 인식하지 못함. python-markdown 자체에는 두 문법 모두 없음(전자는 `meta` 익스텐션이 있지만 그래도 본문에 누출되지는 않을 뿐 별도 데이터 구조로 보관됨; 본 프로젝트에선 단순히 잘라내는 편이 명확함).

### 수정
`_preprocess_markdown`에 두 정규식 추가:
1. `\A---\r?\n.*?\r?\n(?:---|\.\.\.)\r?\n` (DOTALL) — 파일 맨 앞의 메타데이터 블록을 통째로 제거. Pandoc 스펙대로 종결자는 `---` 또는 `...` 둘 다 허용.
2. `^[ \t]*\\(?:newpage|pagebreak)[ \t]*$` (MULTILINE) — 단독 줄로 등장한 `\newpage` / `\pagebreak`를 기존에 이미 존재하던 `<div class="page"></div>` 마크업으로 치환. 따라서 `.page { page-break-after: always }` CSS가 그대로 동작 → 별도 CSS 변경 불필요.

문장 안에 박혀 있는 `\newpage`(예: "이 코드는 `\newpage` 명령을 사용한다")는 변환 대상이 아니다 — 줄 전체가 명령 하나뿐일 때만 페이지 분리로 본다.

### TDD
1. `TestYamlFrontmatterStripping` 5건, `TestLatexPageBreakCommands` 5건 신규 추가, 6건 RED 확인.
2. 전처리기 수정 후 GREEN, 전체 126건 회귀 없음.
3. `scheme-book-full.md` 실측: HTML 본문에서 `documentclass`/`newpage`/`pagebreak` 0건, `class="page"` 53건(원본의 `\newpage` 53회와 일치).

## 2026-05-05 — 코드 블록 고정폭 폰트 적용 (Pygments 토큰 span 문제)

### 증상
``` ``` 코드 블록의 토큰들이 D2Coding이 아닌 본문 sans-serif(NanumGothic)로 출력 — 가독성 저하 및 정렬 깨짐.

### 원인
codehilite 출력 구조: `<pre><code><span class="k">def</span>...</code></pre>`
- `code { font-family: 'D2Coding', ... }` 규칙은 `<code>`에만 직접 적용
- 하지만 `* { font-family: 'NanumGothic' }` 규칙이 specificity (0,0,0)로 모든 `<span>`에 **직접** 적용 → 부모 `<code>`로부터의 상속을 차단
- 결과: 토큰 span들이 NanumGothic으로 렌더

### 수정
1. `*` 규칙에서 `font-family` 제거 (`box-sizing`만 유지)
2. `body`로 `font-family: 'NanumGothic', sans-serif;` 이동 → 자연스러운 상속 cascade 복원
3. `pre`에 `font-family: 'D2Coding', ...` 추가 → `<pre>` 자체와 모든 자손 span이 monospace 상속

### TDD
1. `TestMonospaceFontInheritance` 신규 3건 (RED 확인)
   - `test_universal_selector_does_not_set_font_family`
   - `test_body_sets_default_font_family`
   - `test_pre_block_uses_monospace_font`
2. CSS 수정 후 GREEN, 전체 116건 회귀 없음 (사전 실패 1건 무관)

## 2026-05-05 — 태스크 리스트 체크박스 줄바꿈 버그 수정

### 증상
`- [ ] 텍스트` / `- [x] 텍스트`가 PDF에서 체크박스 다음 글자가 한 줄 아래로 출력됨.

### 원인
전처리 단계에서 `<input type="checkbox" disabled>` HTML로 변환했는데, WeasyPrint는 인쇄 매체 엔진이라 폼 컨트롤 지원이 약함. `<input>`이 기본 너비(폼 텍스트 입력 기본값 ~200px)로 렌더링되어 옆 텍스트가 다음 줄로 밀려남.

### 수정
1. 전처리: `<input type="checkbox" disabled>` → `<span class="taskbox"></span>`
   - 체크된 항목은 `<span class="taskbox checked"></span>`
2. CSS: `.taskbox`를 `display: inline-block`, `width/height: 0.85em`로 고정 → 항상 인라인 작은 박스로 렌더
3. `.taskbox.checked::before { content: "✓" }`로 체크 표시 (GitHub 스타일 파란 배경)

### TDD
1. `TestTaskList` 7건 갱신 + 2건 추가 (`test_no_form_input_emitted`, `test_taskbox_and_label_in_same_li`)
2. `TestTaskListCSS` 3건 신규 (rule 존재, inline-block + em 사이즈, checked 스타일)
3. 구현 후 13건 모두 GREEN, 전체 회귀 없음 (기존 113건 중 무관한 1건 사전 실패만 잔존)

## 2026-05-05 — 코드 블록 긴 라인 줄바꿈 (clip 방지)

### 증상
PDF 코드 블록의 긴 라인(URL, 긴 파라미터 호출 등)이 페이지 오른쪽 밖으로 나가 잘려 보임. 인쇄 매체엔 가로 스크롤이 없으므로 `overflow: auto`만으로는 보이지 않음.

### 원인
`pre` 규칙이 두 가지 부족:
1. `white-space: pre`(`<pre>` 기본값)이라 긴 라인이 줄바꿈 안 됨
2. body의 `word-break: keep-all` 상속 → 단어 중간에서도 끊지 않음

### 수정 (`pre` 규칙 3가지 변경)
- `overflow: auto` 제거 (PDF에선 무용)
- `white-space: pre-wrap` — 들여쓰기/개행 보존하면서 라인은 자동 줄바꿈
- `word-break: normal` — body의 `keep-all` 명시적 오버라이드
- `overflow-wrap: break-word` — 공백 없는 긴 토큰(URL 등)도 끊어 줄바꿈

### TDD
1. `TestGitHubStyleCSS.test_pre_block_wraps_long_lines` 추가 (RED 1)
   - `pre-wrap`, `word-break: normal`, `overflow-wrap: break-word|anywhere` 보장
2. `pre` 규칙 갱신 후 GREEN

### 검증
- `python -m unittest test_md2pdf` → **108 tests OK**
- 통합 케이스 `/tmp/long_test.md`: 페이지 폭을 훨씬 넘는 URL(`query1...query5`) + 한국어 긴 echo
  - 수정 전: 페이지 우측에서 잘려 `query5=value5` 등 누락
  - 수정 후: PDF 추출 텍스트에 `query5=value5` 완전 포함 ✅ — 줄바꿈됨

## 2026-05-05 — 코드 출력의 빨간 테두리 버그 수정 (Pygments `.err` 토큰)

### 증상
PDF의 코드 블록에서 `<`, `>` 같은 기호 일부가 빨간 테두리 박스로 둘러싸여 표시됨.

### 원인
Pygments `default` 스타일의 Error 토큰 규칙:
```css
.codehilite .err { border: 1px solid #F00 }
```
어휘 분석기가 분류하지 못한 토큰(`.err` 클래스)에 빨간 테두리를 그림. CSS 비교 연산자(`x < 100`), TOML placeholder(`<YOUR_TOKEN>`) 등에서 자주 발생.

### 수정
`_build_css` 출력 끝쪽에 오버라이드 규칙 추가:
```css
.codehilite .err { border: none; }
```
Pygments 기본 규칙보다 뒤에 위치 → 같은 specificity에서 cascade 우선순위로 승. Pygments 출력은 그대로 두고 우리는 명시적으로 무력화 → 향후 Pygments 스타일 변경에도 견고.

### TDD
1. `TestGitHubStyleCSS.test_codehilite_err_token_has_no_red_border` 추가 (RED)
   - 마지막 `.codehilite .err` 규칙이 `border: none|0|unset` 매칭 보장
2. `_build_css`에 오버라이드 추가 후 GREEN

### 검증
- `python -m unittest test_md2pdf` → **107 tests OK**
- 재현 케이스 `/tmp/err_real.md`:
  - CSS `if x < 100` + TOML `<YOUR_TOKEN>` → `.err` 7개 토큰 확인
  - 수정 후 PDF에 빨간 테두리 없음 (오버라이드 규칙 활성)

## 2026-05-05 — Web UI에 변환 진행 overlay/스피너 추가

업로드 후 변환이 진행되는 동안 사용자에게 시각 피드백을 주기 위해 모달 overlay와 회전 스피너를 표시. 변환 완료 시 자동 다운로드 + overlay 사라짐.

### 변경 사항

#### HTML
- `<main>` 다음에 `<div id="overlay" class="overlay" hidden>` 추가
- 내부에 `.spinner`(회전 원)와 `.overlay-text`("변환 중...") 배치
- `aria-hidden`, `role="status"`, `aria-label`로 접근성 표시

#### CSS
- `.overlay`: position: fixed, 반투명 검정 + backdrop-filter blur, z-index 1000, fade-in 애니메이션
- `.spinner`: 52×52 원, 4px 테두리, top만 accent 컬러, 0.9s linear spin
- `@keyframes spin`, `@keyframes fade-in`

#### JS
- 기존 IIFE에 폼 submit 가로채기 추가
- `fetch('/convert', { method: 'POST', body: FormData })` AJAX 변환
- 응답 분기:
  - **OK**: `Content-Disposition` 헤더에서 파일명 파싱 (RFC 5987 `filename*=UTF-8''<percent>` 우선, 일반 `filename="..."` fallback) → `URL.createObjectURL(blob)` + 임시 `<a download>` 클릭으로 다운로드 트리거 → "완료!" 표시 후 0.5s 뒤 overlay 숨김
  - **에러 (4xx/5xx)**: 응답 HTML 본문으로 `document.write` 페이지 교체 → 기존 빨간 배너 동작 유지
  - **네트워크 예외**: alert + overlay 즉시 숨김
- 파일 미선택 시 `e.preventDefault()` 안 하고 HTML5 `required` 검증에 위임

### 설계 결정 — 일반 form submit 대신 AJAX
- 표준 form submit은 다운로드 시작 시점을 JS가 알 수 없음 → overlay를 안전히 숨길 방법 없음
- AJAX는 응답 도착 시점이 명확 → 정확히 다운로드 트리거 + overlay 종료 가능
- 단점: JS 미사용 환경에서는 작동 안 함. 단, form `action="/convert"`는 그대로 두어 noscript 시 표준 submit으로 fallback

### TDD
1. `TestWebUI` +3 (RED 3):
   - `test_index_has_loading_overlay_markup`: `id="overlay"`, `spinner`, `변환 중` 존재
   - `test_index_has_spin_keyframes`: `@keyframes spin` 존재
   - `test_index_intercepts_form_submit_with_fetch`: `preventDefault`, `fetch`, `/convert` 존재
2. HTML/CSS/JS 추가 후 GREEN

### 검증
- `python -m unittest test_md2pdf` → **106 tests OK** (+3)
- 라이브 dev server 스모크 테스트 (port 5099):
  - `GET /`: overlay/spinner/keyframes/preventDefault/fetch 모두 응답 HTML에 노출 ✅
  - `POST /convert` (multipart, page_numbers=on): 200 OK, application/pdf, 7.6KB 정상 ✅
- 시각 확인 (애니메이션, blur, fade-in): CLI 환경이라 직접 검증 불가 — 브라우저에서 사용자 확인 필요

### 부수 정리
- `filename\*=` 정규식의 Python SyntaxWarning 제거: 백슬래시 escape (`\\*`)

## 2026-05-05 — [T8] 사용자 커스텀 CSS 주입 (CLI + Web UI)

VSCode `markdown-pdf.styles` 옵션 대응. 사용자가 `--css custom.css`(CLI) 또는 폼 업로드(Web UI)로 추가 스타일시트를 전달하면 기본 CSS **뒤**에 cascade되어 부분 덮어쓰기 가능.

### 변경 사항

#### `convert_md_to_pdf`
- 새 kwarg `custom_css: str | Path | None = None`
- `custom_css`가 주어졌고 파일 미존재 → `FileNotFoundError("CSS file not found: ...")`
- WeasyPrint stylesheets 리스트에 base 다음으로 `CSS(filename=str(custom_css), ...)` 추가
- cascade 순서: source order = priority for equal specificity → 사용자 규칙이 매칭되는 base 규칙을 덮어씀

#### CLI
- `--css PATH` 인자 추가 (기본값 `None`)
- `main()`이 `convert_md_to_pdf(custom_css=args.css)`로 전달

#### Web UI
- 폼에 `<input type="file" name="custom_css" accept=".css,text/css">` 추가
- `.option.css-input` CSS 스타일 (label + 파일 input 세로 배치)
- POST 핸들러: 업로드된 파일을 `tempfile.TemporaryDirectory()`의 `user.css`로 저장 후 path 전달
- 업로드 안 된 경우 `custom_css=None` (FileStorage.filename이 빈 문자열)

### TDD
1. 11개 테스트 추가 (RED 8, GREEN 3 자연 통과):
   - `TestCustomCSS` 3: stylesheet 순서 검증, 미사용 시 base만, 미존재 파일 → FileNotFoundError
   - `TestArgParser` +3: `--css` 파싱, 기본값 `None`, `main()`이 kwarg로 전달
   - `TestWebUI` +3: 폼에 file input, 업로드 시 path 전달, 미업로드 시 `None` 전달
2. 구현 후 모두 GREEN

### 검증
- `python -m unittest test_md2pdf` → **103 tests OK**
- 통합 테스트 `/tmp/css_demo.md` + `/tmp/red_h1.css`:
  - 기본: 8459B
  - 커스텀 적용: 8500B (색상/테두리 정보 추가 임베딩)
- 미존재 CSS 경로: `Error: CSS file not found: /nonexistent.css` (FileNotFoundError → main에서 stderr + exit 1)

## 2026-05-05 — [T6] 수동 페이지 나누기 (`<div class="page"/>`)

VSCode `vscode-markdown-pdf` 확장과 호환되는 페이지 분할 마커. 사용자가 마크다운 안에 `<div class="page"></div>` 또는 self-closing `<div class="page"/>`를 두면 그 위치에서 페이지가 나뉨.

### 변경 사항
- CSS: `.page { page-break-after: always }` 추가
- `_preprocess_markdown`에 self-closing 정규화 추가
  - 정규식 `<div\s+class=["\']page["\']\s*/>` → `<div class="page"></div>`
  - 이유: HTML5 파서는 self-closing `<div/>`의 `/`를 무시 → `<div>`로 해석 → 닫는 태그 없음 → 나머지 문서가 div의 자식이 되어 page-break가 적용 안 됨

### TDD
1. `TestManualPageBreak` 3개 테스트
   - CSS 규칙 존재 (RED → GREEN)
   - closing form pass-through (자동 GREEN)
   - self-closing 정규화 (RED → GREEN, 통합 테스트로 발견된 문제)
2. 초기 구현은 CSS만 추가 → self-closing 형식이 통합 테스트에서 page-break 실패
3. `_preprocess_markdown`에 정규화 추가 후 GREEN
4. 테스트 강화: 단순 `class="page"` 존재가 아닌 정확히 `<div class="page"></div>` 매칭 확인

### 검증
- `python -m unittest test_md2pdf` → **94 tests OK**
- 통합 테스트 `/tmp/break_test.md`:
  - 입력: `# 페이지 1` + `<div class="page"></div>` + `# 페이지 2` + `<div class="page"/>` + `# 페이지 3`
  - 결과: PDF 3 페이지, 각 페이지 첫 줄이 의도한 헤딩 ✅
- 두 형식(closing/self-closing) 모두 동일 동작

## 2026-05-05 — [T9] 이모지 shortcode 지원 (코드 블록 보호)

`:rocket:`, `:smile:`, `:tada:` 같은 GitHub 스타일 shortcode를 실제 이모지 글리프로 변환. 코드 블록(`<pre>`, `<code>`) 안의 `:foo:` 텍스트는 변환에서 제외해 소스 코드 무결성 유지.

### 변경 사항
- `pip install emoji` (2.15.0, ~70KB) — 새 의존성
- `_emojize_html(html)` 헬퍼:
  - `<pre ...>...</pre>`, `<code ...>...</code>` 블록을 정규식으로 분리
  - 비-코드 부분만 `emoji.emojize(part, language="alias")` 적용
  - 모르는 shortcode(`:totally_made_up:`)는 그대로 통과
- `_render_html`: markdown 변환 후 마지막 단계에서 `_emojize_html` 호출

### 설계 결정 — markdown 변환 후 후처리
- 변환 전 처리: 코드 펜스 안의 `:rocket:`도 변환됨 (잘못)
- 변환 후 후처리: HTML 구조에서 `<pre>`/`<code>` 식별 가능 → 안전
- 정규식 `(<pre\b[^>]*>.*?</pre>|<code\b[^>]*>.*?</code>)` + `re.DOTALL`로 한 패스에 split

### TDD
1. `TestEmojiShortcodes` 6개 테스트 (RED 3, GREEN 3 자동)
   - 본문 이모지 변환, 다중 변환, 한국어 + 이모지: 초기 RED
   - 인라인 코드 보호, 펜스 코드 보호, 미지정 shortcode 보존: 변환 미구현 상태에서도 자연스럽게 GREEN
2. `_emojize_html` 구현 후 모든 GREEN

### 검증
- `python -m unittest test_md2pdf` → **91 tests OK**
- 통합 검증 `/tmp/checklist.md`:
  - 본문: `:clipboard:` → 📋, `:rocket:` → 🚀, `:tada:` → 🎉 ✅
  - 인라인 ``` `:smile:` ``` → 그대로 `:smile:` ✅
  - 펜스 코드 ```python ... :rocket: ... ``` → 그대로 `:rocket:` ✅
  - 각주 안의 `:gear:` → ⚙️ (각주는 일반 본문이므로 변환됨) ✅

## 2026-05-05 — [T4] 각주(footnotes) 지원

`[^1]` 참조와 `[^1]: 정의` 블록을 footnote 첨자 + 하단 정의 섹션으로 렌더.

### 핵심
- python-markdown의 `extensions=["extra"]`에는 `footnotes`가 이미 포함되어 있어 **추가 코드 없이 동작 확인**
- `<sup id="fnref:1"><a href="#fn:1">1</a></sup>` 본문 첨자
- `<div class="footnote"><hr><ol><li id="fn:1">...각주 텍스트...<a class="footnote-backref">↩</a></li></ol></div>` 하단 섹션

### CSS 추가
- `sup`: 0.75em, super vertical-align, line-height 0
- `.footnote`: 32px 상단 여백, 0.85em 글씨, `#59636e` 색상
- `.footnote hr`: 1px solid 구분선, 12px 하단 여백
- `.footnote ol`: 1.4em 좌측 padding
- `a.footnote-ref`, `a.footnote-backref`: GitHub blue (`#0969da`), 밑줄 없음

### TDD
1. `TestFootnotes` 5개 테스트 — 모두 GREEN (사실상 회귀 테스트로 동작; CSS 스타일 잠금)
2. CSS 규칙 추가 후 `test_css_styles_footnote_section` GREEN

### 검증
- `python -m unittest test_md2pdf` → **85 tests OK**
- HTML 출력 직접 확인: `<sup>1</sup>` + `<div class="footnote">` 정상

## 2026-05-05 — [T3] 작업 목록 체크박스 (task list)

GitHub 스타일 `- [ ] todo` / `- [x] done` 마커를 disabled checkbox로 렌더. python-markdown에는 내장 지원이 없으므로 자체 정규식 전처리로 해결 (의존성 없음).

### 변경 사항
- `_preprocess_markdown(md_text)` 헬퍼 분리 (기존 fence 속성 정규식 + 새 task list 정규식)
- 정규식 2개:
  - `^([ \t]*[-*+])[ \t]+\[ \][ \t]+` → `\1 <input type="checkbox" disabled> `
  - `^([ \t]*[-*+])[ \t]+\[[xX]\][ \t]+` → `\1 <input type="checkbox" disabled checked> `
- `_render_html`은 `_preprocess_markdown` 호출 후 markdown 처리
- 들여쓰기, `*`/`+` 마커, 대문자 `[X]` 모두 지원

### CSS
- `li input[type="checkbox"]`: `margin-right: 0.5em`, `vertical-align: middle`

### 안전 장치
- 패턴은 줄 시작 + list marker 다음에만 매칭 → 본문 중 `[foo]` 등 일반 대괄호는 영향 없음
- 코드 블록 안의 `- [ ]` 텍스트도 markdown이 코드로 인식 → 정규식이 코드 블록 외부에만 적용되도록 의도된 동작

### TDD
1. `TestTaskList` 8개 테스트 (RED 6, GREEN 2)
   - 기본 unchecked/checked, 대문자 X, asterisk 마커, 들여쓰기, 한국어, 일반 리스트 미영향, 단순 본문 대괄호 미영향
2. `_preprocess_markdown` 구현 후 모두 GREEN

### 검증
- `python -m unittest test_md2pdf` → **80 tests OK**
- 통합 PDF 렌더 확인: 체크박스 + 텍스트 정상 (시각 확인은 PDF 뷰어 필요)

## 2026-05-05 — [T5] 페이지 번호 (꼬리말)

VSCode `vscode-markdown-pdf`의 `displayHeaderFooter` / `pageNumber` 옵션 대응. WeasyPrint의 `@page` 마진 박스 기능을 사용해 `<현재> / <전체>` 형식 페이지 번호를 꼬리말 중앙에 렌더. CLI/Web UI 양쪽에서 토글 가능.

### 변경 사항

#### CSS (`_build_css`)
- 새 kwarg `page_numbers: bool = True`
- `True`일 때 `@page { @bottom-center { content: counter(page) " / " counter(pages); ... } }` 주입
  - NanumGothic sans-serif, 9pt, `#59636e` (회색)
- `False`일 때 `@bottom-center` 블록 omit

#### `convert_md_to_pdf`
- 새 kwarg `page_numbers: bool = True`
- `_build_css(font_uris, page_numbers=page_numbers)`로 전달

#### CLI
- `--no-page-numbers` 플래그 (`action="store_false", dest="page_numbers"`)
- `set_defaults(page_numbers=True)` — 기본 ON
- `main()`이 `convert_md_to_pdf(..., page_numbers=args.page_numbers)`로 전달

#### Web UI
- 폼에 체크박스 `<input type="checkbox" name="page_numbers" checked>` 추가
- 체크박스용 `.option` CSS 스타일 (accent color 적용)
- POST 핸들러: `request.form.get("page_numbers") == "on"` (브라우저는 체크된 박스만 전송)

### 머리말은 일단 제외
- 원래 task 제목은 "페이지 번호와 머리말/꼬리말"이지만, 머리말 콘텐츠는 H1 추출 등 추가 정책 결정이 필요
- 이번엔 가장 임팩트 큰 페이지 번호(꼬리말)만 처리. 머리말은 별도 task로 분리 가능

### 스코프 결정 — 기본 ON
- 페이지 번호는 보통 인쇄/공유 시 가장 유용한 보조 정보
- 옵트인보다 옵트아웃이 사용자 의도에 부합
- 기존 PDF 출력에 미세한 시각 변화 (꼬리말 한 줄)이지만 의도된 개선

### TDD
1. 10개 테스트 추가 (RED 10):
   - `TestPageNumbers` 3: CSS 토글 동작
   - `TestConvertPropagatesPageNumbers` 1: kwarg 전파
   - `TestArgParser` +3: `--no-page-numbers`, 기본값, `main()` 전달
   - `TestWebUI` +3: 체크박스 존재, 체크/언체크 시 동작
2. 구현 후 GREEN
3. 기존 `test_convert_success`의 `fake_convert` 시그니처에 `**kwargs` 추가 (회귀 수정)

### 검증
- `python -m unittest test_md2pdf` → **72 tests OK**
- 통합 검증
  - `python md2pdf.py sample.md`: 페이지 6 → `6 / 39`, 마지막 → `39 / 39` ✅
  - `python md2pdf.py sample.md --no-page-numbers`: 전체 텍스트에 `\d+/\d+` 패턴 없음 ✅
  - Web UI: GET `/`로 체크박스 HTML 확인 + POST 시 `page_numbers` kwarg 전달 mocking 검증

## 2026-05-05 — [T7] 상대 경로 이미지 base_url 처리

마크다운에 `![alt](images/foo.png)` 같은 상대 경로 이미지가 있을 때, 사용자의 현재 작업 디렉터리(cwd)와 무관하게 `.md` 파일 자체의 디렉터리를 기준으로 이미지를 찾도록 수정.

### 변경 사항
- `convert_md_to_pdf`에서 `base_url = os.path.dirname(os.path.abspath(md_filepath))` 계산
- `HTML(string=final_html, base_url=base_url)`로 WeasyPrint에 전달
- 절대 경로(`/abs/img.png`)와 외부 URL(`https://...`)은 base_url과 무관하게 그대로 동작

### 설계 결정 — base64 임베딩 대신 base_url
- WeasyPrint가 file system에서 직접 이미지를 읽으므로 base64 인코딩 오버헤드 없음
- 큰 이미지도 메모리 효율적으로 처리 (전체를 문자열에 넣지 않음)
- PDF 품질을 위해 다운샘플링 X
- `img { max-width: 100%; height: auto }`는 T1에서 이미 추가됨 (페이지 폭 초과 방지)

### TDD
1. `TestImagesAndBaseUrl` 2개 테스트 (RED 1, GREEN 1)
   - `test_img_rule_caps_at_page_width`: T1 회귀 테스트 (CSS 규칙 확인) — 이미 GREEN
   - `test_html_called_with_md_directory_as_base_url`: `HTML` mock으로 호출 인자 검증 — 초기 RED, 구현 후 GREEN
2. 통합 검증
   - 1×1 빨간 픽셀 PNG (70B)를 `/tmp/pixel.png`에 두고 `/tmp/img_test.md`에서 상대 경로로 참조
   - cwd=`/root/github/md2pdf` → PDF에 이미지 임베드 ✅
   - cwd=`/` (다른 위치) → PDF에 이미지 임베드 ✅ (cwd 독립성 검증)
   - pypdf로 PDF 페이지 내 이미지 1개 확인 (원본과 동일한 70B)

### 검증
- `python -m unittest test_md2pdf` → **62 tests OK**
- 실제 이미지 포함 마크다운 변환 시 PDF 페이지에 이미지 객체 임베드 확인

## 2026-05-05 — [T-FONT] Bold + D2Coding 폰트 다중 weight 지원

지금까지는 NanumGothic Regular 1개만 사용해 헤딩의 굵은 글씨와 코드 블록의 한글 고정폭을 모두 합성으로 처리. 이번 변경으로 헤딩은 진짜 Bold 글리프로, 코드 블록은 한글 친화 모노스페이스(D2Coding)로 렌더됨.

### 변경 사항

#### 폰트 시스템
- `FontResource` dataclass + `FONT_RESOURCES` 딕셔너리 도입
  - `regular`: NanumGothic-Regular.ttf (기존)
  - `bold`: NanumGothic-Bold.ttf (`f96298f9...`, 같은 google/fonts 저장소)
  - `code`: D2Coding.ttf (zip에서 추출 — `0f1c9192...`, naver/d2codingfont VER1.3.2 릴리스)
- Italic은 NanumGothic 공식 italic 폰트가 없어 합성 italic 유지 (제외)
- `_ensure_font_resource(spec, fonts_dir)`:
  - 메모리에 다운로드 → SHA256 검증 → 디스크 쓰기 (atomic; 실패 시 partial file 없음)
  - `archive_member`가 설정되면 zip 안의 해당 항목만 추출
  - `urllib.request.urlretrieve` → `urlopen + read` (메모리 검증 위함)
- `ensure_fonts() -> dict[str, Path]`: 모든 폰트 보장, 역할별 경로 반환
- `ensure_font()`: 하위호환 — Regular만

#### CSS
- `_build_css(font_uris: dict)`로 시그니처 변경 (3개 URI 받음)
- `@font-face` 3개 emit:
  - NanumGothic / `font-weight: normal`
  - NanumGothic / `font-weight: bold`  ← 헤딩과 `<strong>`가 진짜 Bold 사용
  - D2Coding / `font-weight: normal`  ← 코드 블록 한글 고정폭
- `code` 규칙은 T1에서 이미 `'D2Coding', 'NanumGothic', Consolas, ...` 스택을 가지고 있어 자동 활용

#### convert_md_to_pdf
- `font_path` 인자: 단일 파일을 모든 역할(regular/bold/code)에 적용하는 override 모드 — 테스트와 자급 폰트 사용자 모두 호환
- `font_path=None`: `ensure_fonts()` 자동 호출

### .gitignore
- 기존 `fonts/*.ttf`, `fonts/*.otf` 규칙으로 신규 파일도 자동 제외
- `git check-ignore` 검증 완료 (NanumGothic-Bold.ttf, D2Coding.ttf 모두 ignored)

### TDD
1. `TestFontMultiWeight` 5 + `TestEnsureFonts` 5 = 10개 테스트 추가 (RED)
2. 기존 `TestEnsureFont` 4개를 `urlopen + _FakeResp` 패턴으로 갱신
3. `TestGitHubStyleCSS._css()`와 `TestPygmentsHighlighting`을 dict 시그니처로 갱신
4. 구현 (GREEN)
5. zip 멤버 추출 검증: 가짜 zip을 메모리에 만들어 archive_member로 추출되는지 확인

### 검증
- `python -m unittest test_md2pdf` → **60 tests OK**
- 통합 테스트: NanumGothic-Bold.ttf(2.0MB), D2Coding.ttf(4.0MB) 자동 다운로드 + SHA256 검증 통과
- PDF 임베디드 폰트(pypdf 분석): `NanumGothic`, `NanumGothic-Bold`, `D2Coding` 3개 모두 subset으로 임베드 확인
- `sample.md → sample.pdf`: 39p / 141KB (T2) → 39p / 175KB (T-FONT)
  - +34KB는 Bold + D2Coding subset 임베딩 효과
  - 페이지 수 동일 (텍스트 레이아웃 회귀 없음)
- 누적 PDF 크기 변화: 160KB(원본) → 132KB(T1) → 141KB(T2) → **175KB(T-FONT)**

## 2026-05-05 — [T2] Pygments 기반 코드 하이라이팅

VSCode `vscode-markdown-pdf`가 사용하는 highlight.js를 우리 환경(JS 미실행)에서는 쓸 수 없으므로 동등 효과를 Pygments(Python 라이브러리)로 구현. 펜스 코드 블록의 키워드, 문자열, 주석, 함수명 등이 색상으로 구분됨.

### 변경 사항
- python-markdown extension에 `codehilite` 추가
  - `guess_lang=False`: 미지정 펜스(```\n...\n```)는 plain 처리 (오인식 방지)
  - `css_class="codehilite"`, `noclasses=False`: 인라인 style이 아닌 CSS 클래스 사용 (PDF diff 가능성 유지)
  - `pygments_style="default"`: 밝은 배경 친화적, GitHub 컬러에 가까움
- `_pygments_css()` 헬퍼: `HtmlFormatter(...).get_style_defs(".codehilite")`로 토큰 컬러 규칙 생성
  - Pygments가 함께 출력하는 unscoped `pre { line-height: 125% }`, `td.linenos`, `span.linenos` 규칙은 제거 (우리 `pre` 규칙과 충돌하거나 미사용)
- `_render_html(md_text)` 헬퍼: 기존 fence 속성 정규식 + extension 호출을 한 곳에 모음 → 테스트가 extension 목록 중복 정의 안 해도 됨
- `_build_css(font_uri)`는 Pygments 규칙을 먼저, 우리 규칙을 뒤에 배치 → 같은 selector(`pre`)에서 cascade 우선순위로 우리가 승

### TDD
1. `TestPygmentsHighlighting` 8개 테스트 (RED): CSS에 `.codehilite .k` / `.s` 토큰 클래스, `def` 키워드가 `<span class="k">`로 감싸짐, 문자열 토큰 span, 미지정/미지원 언어 fallback, 한글 코드 보존, fence 속성 정규식 회귀 방지
2. `_render_html` + `_pygments_css` + `_build_css` 통합 (GREEN)
3. 기존 `convert_md_to_pdf`의 인라인 정규식 + `markdown.markdown()` 호출 → `_render_html()` 한 줄로 단순화

### 검증
- `python -m unittest test_md2pdf` → **50 tests OK**
- `sample.md → sample.pdf`: 39p / 132KB (T1) → 39p / 141KB (T2)
  - 페이지 수 동일 (텍스트 레이아웃 변화 없음)
  - 약 12KB 증가는 토큰별 색상 정보 임베딩 효과
- 한국어 문자열 리터럴(`f"안녕, {name}"`) 토큰화 확인: 따옴표 안 한글 보존, `{name}` interpolation 별도 span

## 2026-05-05 — [T1] GitHub 스타일 마크다운 CSS 적용

VSCode `vscode-markdown-pdf` 확장의 `markdown.css`를 참고해 PDF 시각 골조를 GitHub flavored markdown 풍으로 교체. 한국어 가독성 설정(`word-break: keep-all`, `line-height` 1.7)은 유지.

### 시각 변경
- h1, h2 하단 1px 테두리(`#d1d9e0`) — 챕터/섹션 구분 명확
- 본문 `max-width: 980px; margin: 0 auto` — 좁은 페이지에서도 일관된 컬럼
- 헤딩 크기 위계(2em / 1.5em / 1.25em / 1em / 0.9em / 0.85em) 명시
- 인라인 `code`: 옅은 회색 배경 + `border-radius: 6px` + 작은 padding
- `pre` 블록: `#f6f8fa` 배경 + 16px padding + `border-radius: 6px`로 분명한 박스
- `pre code`는 배경/패딩 리셋 (이중 강조 방지)
- `blockquote`: 좌측 4px solid 막대 + `#59636e` 회색 글자
- 테이블 zebra 줄무늬 (`tr:nth-child(2n)`) + 셀 padding 6/13px
- `hr`: 2px solid 가로선
- 링크: `#0969da`(GitHub blue), 밑줄 제거
- `img { max-width: 100%; height: auto }`로 페이지 폭 초과 방지

### 구조 변경
- `_build_css(font_uri) -> str` 헬퍼로 CSS 추출 → 단위 테스트 가능
- `convert_md_to_pdf()`는 `_build_css()` 호출만 수행
- `from weasyprint import ...`을 try/except로 감싸 CSS 단위 테스트가 native lib(pango/harfbuzz/cairo) 없이도 실행되도록 함. WeasyPrint 사용 시점에 명확한 RuntimeError 발생

### TDD
1. `TestGitHubStyleCSS` 11개 테스트를 먼저 작성 (RED): 한국어 설정 회귀, 헤딩 테두리, blockquote, pre/code, zebra, max-width, hr, font-uri 패스스루
2. `_build_css` 추출 + CSS 재작성 (GREEN)
3. `TestConvertMdToPdf`와 `TestIntegration`은 `FontConfiguration` mocking 추가 및 native lib 부재 시 skipUnless 적용 — 환경 회귀 방지

### 검증
- 단위 테스트: `python -m unittest test_md2pdf` → 42 tests OK (통합 2개 환경 따라 skip)
- 통합 테스트(현 환경에서 harfbuzz/fontconfig 심볼릭 링크 후): 42/42 통과
- `sample.md → sample.pdf`: 46p / 160KB → 39p / 132KB (line-height + padding 최적화 효과; 페이지 수 감소는 컬럼 폭 활용 향상 때문)
- 첫 페이지 텍스트 무결성 확인, 한글 줄바꿈 자연스러움

## 2026-05-03 — 웹 UI 모바일 친화 디자인 개편

`--webui` 모드의 업로드 페이지(`FORM_TEMPLATE`)를 모던 모바일 스타일로 재구성.

- `viewport` 메타 태그 추가로 모바일에서 1:1 스케일 렌더링.
- 시스템 폰트 스택(-apple-system / Segoe UI / Noto Sans KR / Apple SD Gothic Neo) 적용으로 iOS·Android 네이티브 느낌.
- 그라디언트 hero 카드 + 둥근 모서리(`--radius: 18px`) + soft shadow로 카드형 레이아웃 구성.
- 드래그 앤 드롭 영역(`#drop-zone`) 추가: `dragover` 상태에서 강조, 파일 드롭/탭 모두 지원, 선택된 파일명/용량 표시.
- 터치 친화 제출 버튼(min-height 52px, 그라디언트, active 시 누름 효과).
- `prefers-color-scheme: dark` 미디어 쿼리로 다크 모드 자동 대응.
- 안전 영역(env(safe-area-inset-*)) 패딩으로 노치/홈 인디케이터 회피.

TDD: `TestWebUI`에 `test_index_is_mobile_friendly`, `test_index_has_drag_and_drop_zone` 두 케이스 추가 후 구현. 기존 라우트 동작과 한국어 에러 문구(`에러`, `업로드`, `변환 실패`)는 그대로 유지하여 회귀 없음.

## 2026-04-10 — sample.md 손상 버그 수정

`751d57c` 커밋 이후 `sample.md`가 null bytes(0x00)로 완전히 손상되어 PDF 변환이 실패하는 버그 수정.
원인: 외부 요인으로 파일이 덮어써진 것으로 추정 (md2py_web 빌드 스크립트는 sample.md를 건드리지 않음).
`git restore sample.md`로 직전 커밋의 정상 파일(1,525줄)을 복원.
전체 29개 테스트 통과 확인.

## 2026-04-10 — TypeScript port (`md2py_web/`)

A new sibling project, `md2py_web/`, ports md2pdf to TypeScript with
**zero runtime external dependencies** (Node.js built-ins only).
TDD: 45 tests written before implementation, all passing. Build via
`./md2py_web/build.sh` which produces a self-contained `release/`
folder. See [`md2py_web/history.md`](./md2py_web/history.md) for the
full change list.

## 2026-04-10 — Web UI, CLI Refactor & Fence Attribute Fix

### New Features

1. **Web UI for Markdown ➜ PDF conversion**
   - Run `python md2pdf.py --webui` to start a Flask-based upload page.
   - Single page with file upload form; converted PDF is streamed back as
     a download.
   - Errors (missing file, wrong extension, conversion failure) are shown
     as a red banner on the same page **and** logged to stderr.
   - 16 MB upload size cap (`MAX_CONTENT_LENGTH`).

2. **`-p` / `--port` option**
   - Choose the Web UI port (default `5000`).
   - Example: `python md2pdf.py --webui -p 8080`.

3. **`exit` console command**
   - While the Web UI is running, a daemon thread watches stdin.
   - Typing `exit` (followed by Enter) on the console terminates the app
     cleanly via `os._exit(0)`.

4. **CLI rewritten with `argparse`**
   - New options: `--webui`, `-p/--port`, `--font`.
   - Existing positional usage (`python md2pdf.py input.md [output.pdf]`)
     still works unchanged.
   - New `main(argv=None)` entry point makes the CLI testable.

### Fence Attribute Fix

- `convert_md_to_pdf()` now strips unsupported `name=foo.yml` attributes
  from fenced-code info strings before handing the text to
  python-markdown. Without this, fences with extra attributes were not
  recognised as code blocks and the surrounding headings/text were
  misparsed (sections after such fences would silently disappear).

### Changes

#### `md2pdf.py`
- Added `create_app()` Flask factory with `GET /` and `POST /convert` routes.
- Added `run_webui(port, host)` entry point.
- Added `_stdin_exit_monitor()` daemon thread for the `exit` console command.
- Added `_build_arg_parser()` and `main(argv)` for testable CLI dispatch.
- PDF response uses an in-memory `BytesIO` so the temporary directory can
  be cleaned up before Flask streams the file.
- Fence-attribute regex stripping (see above).

#### `test_md2pdf.py`
- Added `TestArgParser` (5 tests): positional input, `--webui -p`,
  `--webui --port`, no-args help, `main()` dispatching to `run_webui`.
- Added `TestWebUI` (5 tests) using Flask's `test_client`:
  - GET `/` renders the form.
  - POST `/convert` with mocked `convert_md_to_pdf` returns PDF bytes
    with `Content-Disposition: attachment; filename=…pdf`.
  - POST with non-`.md` filename → 400 + Korean error banner.
  - POST with no file field → 400 + "업로드" error.
  - POST where `convert_md_to_pdf` raises `RuntimeError` → 500 +
    "변환 실패" banner containing the underlying error message.
- Added `TestFenceAttributeStripping` (3 tests) for the regex preprocessing.
- Total: **29 tests, all passing**.

#### `README.md`
- New "Web UI" section documenting `--webui`, `-p/--port`, and the `exit`
  console command.

### Verification

- `python -m unittest test_md2pdf.py -v` → 29 passed.
- Live smoke test: `python md2pdf.py --webui -p 5099` + `curl /` returned
  HTTP 200 with the upload form HTML.

---

## 2026-04-09 — Korean Font Fix & Test Suite

### Problems Fixed

1. **weasyprint import error** — `ModuleNotFoundError: No module named 'tinycss2.color5'`  
   Fixed by upgrading `tinycss2` from 1.4.0 to 1.5.1:
   ```bash
   pip install --upgrade tinycss2
   ```

2. **Korean font not bundled** — The original script hardcoded `NanumGothic-Regular.ttf`
   in the current working directory with no download mechanism, causing immediate failure
   on any fresh clone.

3. **Font path relative to cwd** — Font was looked up relative to wherever the user ran
   the command, not relative to the script. This caused failures when running from a
   different directory.

4. **No error propagation** — Errors were silently printed and the function returned
   `None`, making it impossible to test or handle errors programmatically.

### Changes

#### `md2pdf.py`
- Added `ensure_font(fonts_dir)` — auto-downloads `NanumGothic-Regular.ttf` from
  Google Fonts GitHub on first use into `<script_dir>/fonts/`
- Added SHA256 integrity verification of the downloaded font
- Font path now defaults to `<script_dir>/fonts/NanumGothic-Regular.ttf` (relative
  to script, not cwd)
- `convert_md_to_pdf()` now raises `FileNotFoundError` for missing inputs instead of
  printing and returning `None`
- `convert_md_to_pdf()` now raises `RuntimeError` on PDF generation failure
- `convert_md_to_pdf()` returns `Path(pdf_filepath)` on success
- Improved CSS: added `word-break: keep-all`, `overflow-wrap: break-word`, page margins,
  blockquote styling, and better heading styles for Korean readability
- Added `toc` extension to markdown for table-of-contents support
- `font_path` parameter added to `convert_md_to_pdf()` for custom font override

#### `test_md2pdf.py` (new)
- 13 unit/integration tests across 5 test classes:
  - `TestKoreanMarkdown` — verifies Korean text survives markdown-to-HTML conversion
  - `TestEnsureFont` — tests download, cache hit, SHA256 failure, network failure
  - `TestConvertMdToPdf` — tests error cases and mocked successful conversion
  - `TestSha256Verify` — tests the hash helper directly
  - `TestIntegration` — real PDF rendering tests (skipped if font not present)

#### `fonts/.gitkeep` (new)
- Tracks the `fonts/` directory in git without committing font binaries

#### `.gitignore` (new)
- Ignores `fonts/*.ttf`, `fonts/*.otf`, `*.pyc`, `*.pdf`, `__pycache__/`

#### `README.md` (new)
- Usage instructions, requirements, offline font setup, custom font API, test instructions

### Font
**NanumGothic Regular** — SIL Open Font License 1.1  
Downloaded from: https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf  
SHA256: `76f45ef4a6bcff344c837c95a7dcc26e017e38b5846d5ae0cdcb5b86be2e2d31`
