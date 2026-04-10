/**
 * Static UI HTML for md2py_web. Embedded as a TypeScript constant so the
 * runtime has zero file-system dependencies.
 */

export const UI_HTML = `<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>md2py_web — Markdown ➜ PDF</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 720px; margin: 56px auto;
         padding: 0 20px; color: #222; }
  h1 { font-size: 1.6em; }
  .card { border: 1px solid #ddd; border-radius: 8px; padding: 24px;
          box-shadow: 0 2px 6px rgba(0,0,0,0.04); }
  .error { background: #fdecea; color: #b3261e; padding: 12px 16px;
           border: 1px solid #f5c2c0; border-radius: 6px; margin-bottom: 18px;
           display: none; white-space: pre-wrap; }
  .ok { background: #e7f5ec; color: #1e7a3c; padding: 8px 12px;
        border: 1px solid #b9e1c7; border-radius: 6px; margin: 12px 0;
        display: none; }
  input[type=file] { margin: 14px 0; }
  button { background: #0066cc; color: #fff; border: 0; padding: 10px 18px;
           border-radius: 6px; font-size: 1em; cursor: pointer; }
  button:hover { background: #004f9e; }
  button:disabled { background: #999; cursor: not-allowed; }
  iframe { width: 100%; height: 480px; border: 1px solid #ddd; border-radius: 6px;
           margin-top: 16px; display: none; background: #fff; }
  footer { margin-top: 24px; font-size: 0.85em; color: #888; }
  code { background: #f4f4f4; padding: 1px 5px; border-radius: 3px; }
</style>
</head>
<body>
  <h1>md2py_web</h1>
  <div class="card">
    <div class="error" id="error"></div>
    <div class="ok" id="ok"></div>
    <form id="f">
      <label>변환할 Markdown(.md) 파일을 선택하세요.</label><br>
      <input type="file" id="file" accept=".md,.markdown,text/markdown" required><br>
      <button type="submit" id="go">PDF로 변환</button>
      <button type="button" id="print" disabled>브라우저에서 인쇄 → PDF 저장</button>
    </form>
    <iframe id="preview" title="preview"></iframe>
    <footer>
      콘솔에서 <code>exit</code> 입력 시 서버가 종료됩니다.<br>
      변환 결과는 인쇄용 HTML로 표시되며, 브라우저의 <em>인쇄 → PDF로 저장</em>으로 PDF로 내보낼 수 있습니다.
    </footer>
  </div>

<script>
const f = document.getElementById('f');
const fileEl = document.getElementById('file');
const errBox = document.getElementById('error');
const okBox = document.getElementById('ok');
const preview = document.getElementById('preview');
const printBtn = document.getElementById('print');

function showError(msg) {
  errBox.textContent = msg;
  errBox.style.display = 'block';
  okBox.style.display = 'none';
  preview.style.display = 'none';
  printBtn.disabled = true;
}
function clearMessages() {
  errBox.style.display = 'none';
  okBox.style.display = 'none';
}

f.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearMessages();
  const file = fileEl.files && fileEl.files[0];
  if (!file) { showError('파일이 선택되지 않았습니다.'); return; }
  if (!/\\.(md|markdown)$/i.test(file.name)) {
    showError('Markdown(.md) 파일만 업로드할 수 있습니다: ' + file.name); return;
  }
  let text;
  try { text = await file.text(); }
  catch (err) { showError('파일을 읽지 못했습니다: ' + err); return; }

  try {
    const resp = await fetch('/convert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ markdown: text, title: file.name }),
    });
    const data = await resp.json();
    if (!resp.ok) {
      showError('변환 실패: ' + (data.error || resp.status));
      return;
    }
    okBox.textContent = '변환 완료. 아래 미리보기에서 확인하거나 인쇄하세요.';
    okBox.style.display = 'block';
    const blob = new Blob([data.html], { type: 'text/html' });
    preview.src = URL.createObjectURL(blob);
    preview.style.display = 'block';
    printBtn.disabled = false;
  } catch (err) {
    showError('네트워크 오류: ' + err);
  }
});

printBtn.addEventListener('click', () => {
  if (preview.contentWindow) preview.contentWindow.print();
});
</script>
</body>
</html>`;
