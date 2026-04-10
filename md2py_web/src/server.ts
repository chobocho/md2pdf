/**
 * HTTP server for md2py_web. Uses only Node built-ins.
 */

import http, { IncomingMessage, ServerResponse } from "node:http";
import { mdToHtml } from "./markdown.js";
import { wrapDocument } from "./html.js";
import { UI_HTML } from "./ui.js";

export interface ServerOptions {
  /** Maximum allowed POST body size in bytes. Default: 8 MiB. */
  maxBodyBytes?: number;
}

const DEFAULT_MAX_BODY = 8 * 1024 * 1024;

function send(
  res: ServerResponse,
  status: number,
  contentType: string,
  body: string
): void {
  const buf = Buffer.from(body, "utf-8");
  res.writeHead(status, {
    "Content-Type": contentType,
    "Content-Length": buf.length.toString(),
  });
  res.end(buf);
}

function sendJson(res: ServerResponse, status: number, payload: unknown): void {
  send(res, status, "application/json; charset=utf-8", JSON.stringify(payload));
}

function readBody(
  req: IncomingMessage,
  maxBytes: number
): Promise<{ body: string } | { tooLarge: true }> {
  return new Promise((resolve, reject) => {
    let total = 0;
    const chunks: Buffer[] = [];
    req.on("data", (chunk: Buffer) => {
      total += chunk.length;
      if (total > maxBytes) {
        // Stop reading immediately.
        req.removeAllListeners("data");
        req.removeAllListeners("end");
        // Drain quietly so the client connection closes cleanly.
        req.on("data", () => {});
        req.on("end", () => resolve({ tooLarge: true }));
        return;
      }
      chunks.push(chunk);
    });
    req.on("end", () => resolve({ body: Buffer.concat(chunks).toString("utf-8") }));
    req.on("error", reject);
  });
}

export function createServer(opts: ServerOptions = {}): http.Server {
  const maxBytes = opts.maxBodyBytes ?? DEFAULT_MAX_BODY;

  return http.createServer(async (req, res) => {
    try {
      const url = req.url || "/";
      const method = req.method || "GET";

      // Reject oversized requests up-front when Content-Length is set.
      const declaredLen = Number(req.headers["content-length"] || 0);
      if (declaredLen > maxBytes) {
        sendJson(res, 413, { error: "Request body too large" });
        req.resume();
        return;
      }

      if (method === "GET" && url === "/") {
        send(res, 200, "text/html; charset=utf-8", UI_HTML);
        return;
      }

      if (method === "GET" && url === "/health") {
        sendJson(res, 200, { ok: true });
        return;
      }

      if (method === "POST" && url === "/convert") {
        const result = await readBody(req, maxBytes);
        if ("tooLarge" in result) {
          sendJson(res, 413, { error: "Request body too large" });
          return;
        }

        let parsed: unknown;
        try {
          parsed = JSON.parse(result.body);
        } catch (e) {
          const msg = `Invalid JSON: ${(e as Error).message}`;
          process.stderr.write(`[server] ${msg}\n`);
          sendJson(res, 400, { error: msg });
          return;
        }

        if (
          typeof parsed !== "object" ||
          parsed === null ||
          typeof (parsed as { markdown?: unknown }).markdown !== "string"
        ) {
          const msg = "Missing or invalid 'markdown' field";
          process.stderr.write(`[server] ${msg}\n`);
          sendJson(res, 400, { error: msg });
          return;
        }

        const { markdown, title } = parsed as { markdown: string; title?: string };
        try {
          const body = mdToHtml(markdown);
          const html = wrapDocument(body, title || "md2py_web document");
          sendJson(res, 200, { html });
        } catch (e) {
          const msg = `Conversion failed: ${(e as Error).message}`;
          process.stderr.write(`[server] ${msg}\n`);
          sendJson(res, 500, { error: msg });
        }
        return;
      }

      sendJson(res, 404, { error: `Not found: ${method} ${url}` });
    } catch (e) {
      process.stderr.write(`[server] Unhandled error: ${(e as Error).message}\n`);
      try {
        sendJson(res, 500, { error: "Internal server error" });
      } catch {
        /* response may already be sent */
      }
    }
  });
}
