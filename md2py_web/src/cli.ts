/**
 * CLI argument parser. Pure function — no I/O, no external deps.
 */

export interface ParsedArgs {
  mode: "help" | "web" | "cli" | "error";
  port?: number;
  input?: string;
  output?: string;
  error?: string;
}

const KNOWN_FLAGS = new Set([
  "--webui",
  "-p",
  "--port",
  "-h",
  "--help",
]);

export function parseArgs(argv: string[]): ParsedArgs {
  if (argv.length === 0) return { mode: "help" };

  let webui = false;
  let port = 8080;
  const positional: string[] = [];

  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];

    if (a === "-h" || a === "--help") {
      return { mode: "help" };
    }

    if (a === "--webui") {
      webui = true;
      continue;
    }

    if (a === "-p" || a === "--port") {
      const v = argv[i + 1];
      if (v === undefined) {
        return { mode: "error", error: "Missing value for --port" };
      }
      const n = Number(v);
      if (!Number.isInteger(n) || n <= 0 || n > 65535) {
        return { mode: "error", error: `Invalid port: ${v}` };
      }
      port = n;
      i++;
      continue;
    }

    if (a.startsWith("-")) {
      // Unknown flag
      if (!KNOWN_FLAGS.has(a)) {
        return { mode: "error", error: `Unknown option: ${a}` };
      }
    }

    positional.push(a);
  }

  if (webui) {
    return { mode: "web", port };
  }

  if (positional.length === 0) {
    return { mode: "help" };
  }

  return {
    mode: "cli",
    input: positional[0],
    output: positional[1],
  };
}

export function helpText(): string {
  return `md2py_web — Markdown ➜ printable HTML / PDF

Usage:
  md2py_web <input.md> [output.html]
  md2py_web --webui [-p <port>]
  md2py_web --help

Options:
  --webui          Start the web UI server.
  -p, --port N     Web UI port (default: 8080).
  -h, --help       Show this help message.

Web UI controls:
  Type "exit" in the console to terminate the server.
`;
}
