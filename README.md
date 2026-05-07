# md2pdf

마크다운을 한국어 폰트가 적용된 예쁜 PDF로 변환하는 도구. [WeasyPrint](https://weasyprint.org/), [Pygments](https://pygments.org/), [NanumGothic](https://fonts.google.com/specimen/Nanum+Gothic), [D2Coding](https://github.com/naver/d2codingfont) 사용.

## 주요 기능

- **GitHub 스타일 시각**: h1/h2 하단 테두리, blockquote 좌측 막대, 표 zebra 줄무늬, 인라인/블록 코드 구분
- **코드 하이라이팅**: Pygments로 키워드/문자열/주석 색상 구분 (펜스 언어 인식). 긴 라인은 자동 줄바꿈되어 페이지 폭에 맞게 흐름
- **한국어 폰트 다중 weight**: NanumGothic Regular + **Bold** + 코드용 D2Coding (모두 자동 다운로드)
- **생활한자 지원**: NanumGothic이 가지지 않은 CJK 한자(漢字)는 Noto Sans KR(한국 SubsetOTF, 약 8.1k자)로 글리프 단위 자동 fallback — `生活漢字`, `學校` 등이 빈 박스로 출력되지 않음
- **이미지**: 마크다운 파일 디렉터리 기준 상대 경로 자동 해석, `max-width: 100%`로 페이지 폭 초과 방지
- **페이지 번호**: 꼬리말 `현재 / 전체` (기본 ON, 끄기 가능)
- **수동 페이지 분할**: `<div class="page"></div>`로 임의 위치에서 페이지 나누기
- **마크다운 확장**:
  - 작업 목록 체크박스: `- [ ]` / `- [x]`
  - 각주: `[^1]` ... `[^1]: 설명`
  - 이모지 shortcode: `:rocket:` → 🚀 (코드 블록 안의 `:foo:`는 보존)
- **커스텀 CSS**: 사용자 스타일시트로 base 규칙 부분 덮어쓰기
- **Web UI**: 모바일 친화 디자인, 드래그&드롭 업로드, 변환 진행 스피너 overlay, 옵션 토글

## 요구 사항

- Python 3.10+
- weasyprint, markdown, pygments, emoji
- flask (Web UI 사용 시)

```bash
pip install weasyprint markdown pygments emoji flask
```

> **Termux / Android 환경**: weasyprint 임포트 실패 시 tinycss2 업그레이드:
> ```bash
> pip install --upgrade tinycss2
> ```

## 빠른 시작

```bash
python md2pdf.py input.md
# → input.pdf

python md2pdf.py input.md output.pdf
```

**최초 실행 시** `fonts/` 디렉터리에 다음 폰트가 자동 다운로드됩니다 (SHA256 검증):

| 역할 | 파일 | 출처 |
|------|------|------|
| 본문 (regular) | NanumGothic-Regular.ttf | Google Fonts |
| 본문 굵게 (bold) | NanumGothic-Bold.ttf | Google Fonts |
| 코드 (monospace) | D2Coding.ttf | naver/d2codingfont 릴리스 zip에서 추출 |
| 한자 (CJK fallback) | NotoSansKR-Regular.otf | notofonts/noto-cjk SubsetOTF/KR |

이후 실행은 캐시된 파일을 그대로 사용합니다.

## CLI 옵션

```bash
python md2pdf.py [옵션] input.md [output.pdf]
```

| 옵션 | 설명 |
|------|------|
| `--webui` | Web UI 서버 실행 |
| `-p PORT`, `--port PORT` | Web UI 포트 (기본 5000) |
| `--font PATH` | 모든 역할(regular/bold/code/hanja)에 단일 .ttf 강제 적용 |
| `--no-page-numbers` | 꼬리말 페이지 번호 숨기기 |
| `--css PATH` | 추가 CSS 파일 (base 뒤로 cascade되어 부분 덮어쓰기) |

예:

```bash
# 페이지 번호 끄기
python md2pdf.py doc.md --no-page-numbers

# 사용자 정의 색상 테마
python md2pdf.py doc.md --css my-theme.css

# 둘 다
python md2pdf.py doc.md --css my-theme.css --no-page-numbers
```

## Web UI

```bash
python md2pdf.py --webui
# 기본: http://0.0.0.0:5000

python md2pdf.py --webui -p 8080
```

브라우저에서 표시되는 URL을 열면 모바일 친화 업로드 페이지가 나옵니다:

- 마크다운 파일을 드래그&드롭 또는 탭으로 선택
- **페이지 번호 표시** 체크박스 (기본 ON)
- **커스텀 CSS** 파일 업로드 (선택)
- **PDF로 변환** 버튼 클릭 → 변환 중 모달 overlay에 회전 스피너와 "변환 중..." 표시 → 완료 시 PDF 자동 다운로드 + overlay 자동 종료

큰 파일도 변환 진행 상황을 시각적으로 알 수 있어, 작업이 멈춘 것처럼 보이지 않습니다.

에러(파일 미선택, 잘못된 확장자, 변환 실패)는 같은 페이지 빨간 배너 + stderr 로그로 표시됩니다.

콘솔에서 `exit`<Enter>를 입력하면 서버가 깨끗이 종료됩니다.

## 마크다운 문법 참고

### 작업 목록

```markdown
- [x] 완료된 작업
- [ ] 진행중인 작업
- [X] 대문자 X도 OK
```

### 각주

```markdown
본문[^1] 어딘가에 참조.

[^1]: 페이지 하단에 자동 정리됩니다.
```

### 이모지

```markdown
배포 :rocket: 완료 :tada:!
```

코드 블록 안의 `:foo:` 텍스트는 변환되지 않습니다 (소스 무결성 유지).

### 수동 페이지 분할

VSCode `markdown-pdf` 확장과 호환:

```markdown
첫 페이지

<div class="page"></div>

다음 페이지
```

`<div class="page"/>` (XHTML self-closing 형식)도 자동으로 정규화되어 동작합니다.

### 코드 하이라이팅

```markdown
​```python
def hello(name):
    return f"안녕, {name}"
​```
```

펜스 뒤에 언어 명시 시 Pygments 토큰 색상 자동 적용. 미지정 펜스는 plain 처리.

## 오프라인 사용

인터넷 없이 사용하려면 `fonts/` 디렉터리에 미리 폰트를 두세요:

```
md2pdf/
  fonts/
    NanumGothic-Regular.ttf
    NanumGothic-Bold.ttf
    D2Coding.ttf
    NotoSansKR-Regular.otf
  md2pdf.py
```

각 폰트는 다음 위치에서 받을 수 있습니다:

- NanumGothic Regular/Bold: https://fonts.google.com/specimen/Nanum+Gothic
- D2Coding: https://github.com/naver/d2codingfont/releases
- Noto Sans KR (한자 fallback): https://github.com/notofonts/noto-cjk/tree/main/Sans/SubsetOTF/KR

## Python API

```python
from md2pdf import convert_md_to_pdf

convert_md_to_pdf(
    "input.md",
    "output.pdf",
    font_path=None,           # 단일 .ttf로 모든 역할 덮어쓰기 (옵션)
    page_numbers=True,        # 꼬리말 페이지 번호
    custom_css="theme.css",   # 추가 스타일시트 (옵션)
)
```

## 테스트 실행

```bash
python -m unittest test_md2pdf -v
```

103개 테스트:
- 단위 테스트는 native lib(pango/harfbuzz) 없이도 동작 (WeasyPrint 호출은 mock)
- 통합 테스트는 폰트 파일과 native lib가 모두 있을 때만 실행 (없으면 자동 skip)

## 라이선스

- 코드: [LICENSE](./LICENSE) 참조
- **NanumGothic**: SIL Open Font License 1.1 (Sandoll, Google Fonts 배포)
- **D2Coding**: SIL Open Font License 1.1 (NAVER)

## 환경 노트

Android / Termux (Linux arm64), 표준 Linux (x86_64) 모두에서 검증.

`proot-distro`로 실행하는 Termux 환경에서는 다음 라이브러리 심볼릭 링크가 필요할 수 있습니다 (한 번만):

```bash
ln -sf $PREFIX/lib/libharfbuzz.so $PREFIX/lib/libharfbuzz.so.0
ln -sf $PREFIX/lib/libfontconfig.so $PREFIX/lib/libfontconfig.so.1
```

## 변경 이력

`history.md` 참조 — 모든 작업 단계가 한글로 기록되어 있습니다.

## TypeScript 포트 — `md2py_web/`

런타임 외부 의존성이 0인 TypeScript 포트가 [`md2py_web/`](./md2py_web/README.md)에 있습니다. Node.js 내장 모듈(`node:http`, `node:fs`, `node:readline`, `node:test`)만 사용하며, 브라우저 인쇄 대화상자에서 PDF로 저장 가능한 인쇄용 HTML을 출력합니다. `cd md2py_web && ./build.sh`로 빌드합니다.
