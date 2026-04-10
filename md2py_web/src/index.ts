#!/usr/bin/env node
/**
 * md2py_web entry point. Dispatches between CLI and Web UI modes.
 * Zero runtime external dependencies.
 */

import { readFileSync, writeFileSync } from "node:fs";
import readline from "node:readline";
import { parseArgs, helpText } from "./cli.js";
import { createServer } from "./server.js";
import { mdToHtml } from "./markdown.js";
import { wrapDocument } from "./html.js";

function runCli(input: string, output?: string): number {
  let src: string;
  try {
    src = readFileSync(input, "utf-8");
  } catch (e) {
    process.stderr.write(`Error: cannot read ${input}: ${(e as Error).message}\n`);
    return 1;
  }
  const out = output ?? input.replace(/\.(md|markdown)$/i, ".html");
  try {
    const html = wrapDocument(mdToHtml(src), input);
    writeFileSync(out, html, "utf-8");
    process.stdout.write(`HTML saved: ${out}\n`);
    return 0;
  } catch (e) {
    process.stderr.write(`Error: conversion failed: ${(e as Error).message}\n`);
    return 1;
  }
}

function runWeb(port: number): void {
  const server = createServer();

  function shutdown(reason: string): void {
    process.stdout.write(`[webui] ${reason} — shutting down.\n`);
    server.close(() => process.exit(0));
    // Hard exit if close hangs.
    setTimeout(() => process.exit(0), 1500).unref();
  }

  server.listen(port, "0.0.0.0", () => {
    process.stdout.write(
      `[webui] serving on http://0.0.0.0:${port}  (type \`exit\` to quit)\n`
    );
  });

  // Watch stdin for the `exit` command.
  if (process.stdin.isTTY || !process.stdin.isTTY) {
    const rl = readline.createInterface({ input: process.stdin });
    rl.on("line", (line) => {
      if (line.trim().toLowerCase() === "exit") shutdown("exit requested");
    });
    rl.on("close", () => {
      /* stdin closed — let signals handle the rest */
    });
  }

  process.on("SIGINT", () => shutdown("SIGINT"));
  process.on("SIGTERM", () => shutdown("SIGTERM"));
}

export function main(argv: string[]): number {
  const args = parseArgs(argv);

  switch (args.mode) {
    case "help":
      process.stdout.write(helpText());
      return 0;
    case "error":
      process.stderr.write(`Error: ${args.error}\n\n`);
      process.stdout.write(helpText());
      return 2;
    case "web":
      runWeb(args.port ?? 8080);
      return 0; // server keeps the loop alive
    case "cli":
      return runCli(args.input!, args.output);
  }
}

// Detect if this file is being run directly (ESM-safe).
const isDirectRun = (() => {
  if (!process.argv[1]) return false;
  try {
    const url = new URL(import.meta.url);
    return url.pathname.endsWith(process.argv[1].split("/").pop() || "");
  } catch {
    return false;
  }
})();

if (isDirectRun) {
  const code = main(process.argv.slice(2));
  // For web mode, main returns 0 but the server keeps running.
  if (code !== 0 || parseArgs(process.argv.slice(2)).mode !== "web") {
    process.exit(code);
  }
}
