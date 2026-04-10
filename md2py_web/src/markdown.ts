/**
 * Minimal Markdown → HTML renderer.
 * Zero runtime dependencies. Pure TypeScript / JavaScript.
 *
 * Supported syntax:
 *   # H1 .. ###### H6
 *   paragraphs (blank-line separated)
 *   **bold**, *italic*, `inline code`
 *   ```fenced``` code blocks (with optional language)
 *   - / * unordered lists, 1. ordered lists
 *   [text](url) links
 *   > blockquote
 *   --- horizontal rule
 */

export function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

const PLACEHOLDER_OPEN = "\u0000C";
const PLACEHOLDER_CLOSE = "\u0000";

function processInline(text: string): string {
  const codes: string[] = [];

  // 1. Extract inline code first so its content is protected from
  //    further substitution and HTML-escape its body.
  let work = text.replace(/`([^`]+)`/g, (_m, code) => {
    codes.push(`<code>${escapeHtml(code)}</code>`);
    return `${PLACEHOLDER_OPEN}${codes.length - 1}${PLACEHOLDER_CLOSE}`;
  });

  // 2. HTML-escape the remaining text.
  work = escapeHtml(work);

  // 3. Bold must run before italic so that ** is not consumed as two *.
  work = work.replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>");

  // 4. Italic.
  work = work.replace(/\*([^*\n]+)\*/g, "<em>$1</em>");

  // 5. Links — escapeHtml already converted & in urls, which is correct
  //    for HTML href values.
  work = work.replace(
    /\[([^\]]+)\]\(([^)\s]+)\)/g,
    (_m, label, url) => `<a href="${url}">${label}</a>`
  );

  // 6. Restore inline-code placeholders.
  work = work.replace(
    new RegExp(`${PLACEHOLDER_OPEN}(\\d+)${PLACEHOLDER_CLOSE}`, "g"),
    (_m, idx) => codes[Number(idx)]
  );

  return work;
}

function isBlankLine(line: string): boolean {
  return line.trim() === "";
}

function isBlockStart(line: string): boolean {
  return (
    /^#{1,6}\s/.test(line) ||
    /^```/.test(line) ||
    /^---+\s*$/.test(line) ||
    /^>\s?/.test(line) ||
    /^[-*]\s/.test(line) ||
    /^\d+\.\s/.test(line) ||
    isBlankLine(line)
  );
}

export function mdToHtml(src: string): string {
  const lines = src.split(/\r?\n/);
  const out: string[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (isBlankLine(line)) {
      i++;
      continue;
    }

    // Fenced code block
    const fenceMatch = line.match(/^```(\w*)\s*$/);
    if (fenceMatch) {
      const lang = fenceMatch[1];
      i++;
      const codeLines: string[] = [];
      while (i < lines.length && !/^```\s*$/.test(lines[i])) {
        codeLines.push(lines[i]);
        i++;
      }
      if (i < lines.length) i++; // skip closing fence
      const escaped = escapeHtml(codeLines.join("\n"));
      const cls = lang ? ` class="language-${lang}"` : "";
      out.push(`<pre><code${cls}>${escaped}\n</code></pre>`);
      continue;
    }

    // Heading
    const headingMatch = line.match(/^(#{1,6})\s+(.*)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const text = processInline(headingMatch[2]);
      out.push(`<h${level}>${text}</h${level}>`);
      i++;
      continue;
    }

    // Horizontal rule
    if (/^---+\s*$/.test(line)) {
      out.push("<hr />");
      i++;
      continue;
    }

    // Blockquote (single-line per quote, consecutive lines collapse with <br>)
    if (/^>\s?/.test(line)) {
      const quoteLines: string[] = [];
      while (i < lines.length && /^>\s?/.test(lines[i])) {
        quoteLines.push(lines[i].replace(/^>\s?/, ""));
        i++;
      }
      out.push(
        `<blockquote>${processInline(quoteLines.join(" "))}</blockquote>`
      );
      continue;
    }

    // Unordered list
    if (/^[-*]\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^[-*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^[-*]\s+/, ""));
        i++;
      }
      const lis = items.map((t) => `<li>${processInline(t)}</li>`).join("");
      out.push(`<ul>${lis}</ul>`);
      continue;
    }

    // Ordered list
    if (/^\d+\.\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\d+\.\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\d+\.\s+/, ""));
        i++;
      }
      const lis = items.map((t) => `<li>${processInline(t)}</li>`).join("");
      out.push(`<ol>${lis}</ol>`);
      continue;
    }

    // Paragraph: collect lines until blank or another block start
    const paraLines: string[] = [line];
    i++;
    while (i < lines.length && !isBlockStart(lines[i])) {
      paraLines.push(lines[i]);
      i++;
    }
    out.push(`<p>${processInline(paraLines.join(" "))}</p>`);
  }

  return out.join("");
}
