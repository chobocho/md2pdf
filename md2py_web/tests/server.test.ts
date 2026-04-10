import { test } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { AddressInfo } from "node:net";
import { createServer } from "../src/server.js";

function listen(server: http.Server): Promise<number> {
  return new Promise((resolve) => {
    server.listen(0, "127.0.0.1", () => {
      const addr = server.address() as AddressInfo;
      resolve(addr.port);
    });
  });
}

function close(server: http.Server): Promise<void> {
  return new Promise((resolve, reject) =>
    server.close((err) => (err ? reject(err) : resolve()))
  );
}

interface Resp {
  status: number;
  headers: http.IncomingHttpHeaders;
  body: string;
}

function request(
  port: number,
  method: string,
  path: string,
  body?: string,
  headers: Record<string, string> = {}
): Promise<Resp> {
  return new Promise((resolve, reject) => {
    const req = http.request(
      {
        host: "127.0.0.1",
        port,
        path,
        method,
        headers: {
          "Content-Length": body ? Buffer.byteLength(body).toString() : "0",
          ...headers,
        },
      },
      (res) => {
        const chunks: Buffer[] = [];
        res.on("data", (c) => chunks.push(c));
        res.on("end", () =>
          resolve({
            status: res.statusCode || 0,
            headers: res.headers,
            body: Buffer.concat(chunks).toString("utf-8"),
          })
        );
      }
    );
    req.on("error", reject);
    if (body) req.write(body);
    req.end();
  });
}

test("GET / returns the upload UI HTML", async () => {
  const server = createServer();
  const port = await listen(server);
  try {
    const r = await request(port, "GET", "/");
    assert.equal(r.status, 200);
    assert.match(r.headers["content-type"] || "", /text\/html/);
    assert.match(r.body, /md2py_web|md2pdf/i);
    assert.match(r.body, /form/i);
  } finally {
    await close(server);
  }
});

test("GET /health returns ok JSON", async () => {
  const server = createServer();
  const port = await listen(server);
  try {
    const r = await request(port, "GET", "/health");
    assert.equal(r.status, 200);
    assert.match(r.headers["content-type"] || "", /application\/json/);
    assert.deepEqual(JSON.parse(r.body), { ok: true });
  } finally {
    await close(server);
  }
});

test("POST /convert with valid markdown returns html document", async () => {
  const server = createServer();
  const port = await listen(server);
  try {
    const body = JSON.stringify({ markdown: "# 한국어\n\n본문" });
    const r = await request(port, "POST", "/convert", body, {
      "Content-Type": "application/json",
    });
    assert.equal(r.status, 200);
    const parsed = JSON.parse(r.body);
    assert.ok(parsed.html);
    assert.match(parsed.html, /<h1>한국어<\/h1>/);
    assert.match(parsed.html, /<!doctype html>/i);
  } finally {
    await close(server);
  }
});

test("POST /convert with invalid JSON returns 400 + error message", async () => {
  const server = createServer();
  const port = await listen(server);
  try {
    const r = await request(port, "POST", "/convert", "not json{", {
      "Content-Type": "application/json",
    });
    assert.equal(r.status, 400);
    const parsed = JSON.parse(r.body);
    assert.ok(parsed.error);
    assert.match(parsed.error, /json/i);
  } finally {
    await close(server);
  }
});

test("POST /convert with missing markdown field returns 400", async () => {
  const server = createServer();
  const port = await listen(server);
  try {
    const r = await request(port, "POST", "/convert", JSON.stringify({}), {
      "Content-Type": "application/json",
    });
    assert.equal(r.status, 400);
    const parsed = JSON.parse(r.body);
    assert.match(parsed.error, /markdown/i);
  } finally {
    await close(server);
  }
});

test("unknown route returns 404", async () => {
  const server = createServer();
  const port = await listen(server);
  try {
    const r = await request(port, "GET", "/no-such-route");
    assert.equal(r.status, 404);
  } finally {
    await close(server);
  }
});

test("POST /convert respects body size limit", async () => {
  const server = createServer({ maxBodyBytes: 100 });
  const port = await listen(server);
  try {
    const big = "x".repeat(200);
    const r = await request(
      port,
      "POST",
      "/convert",
      JSON.stringify({ markdown: big }),
      { "Content-Type": "application/json" }
    );
    assert.equal(r.status, 413);
  } finally {
    await close(server);
  }
});
