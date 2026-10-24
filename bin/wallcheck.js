#!/usr/bin/env node
// wallcheck npm launcher: a thin Node shim over the bundled Python
// implementation, mirroring the GHCR image entrypoint exactly
// (PYTHONPATH=<package>/python, `python3 -m wallcheck`, default
// command `mcp`). wallcheck is Python standard library only, so
// there is nothing to install beyond Python 3.11+ on PATH.
//
// Usage:
//   wallcheck            -> stdio MCP server (same default as Docker CMD)
//   wallcheck mcp        -> stdio MCP server
//   wallcheck probe <url>, audit <domain>, --version, ... -> the CLI
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const pythonPath = path.join(here, "..", "python");
const entry = path.join(pythonPath, "wallcheck", "__main__.py");

function fail(message) {
  process.stderr.write(`wallcheck: ${message}\n`);
  process.exit(1);
}

if (!existsSync(entry)) {
  fail("bundled Python sources are missing from this install; reinstall @reneturcios/wallcheck.");
}

const python =
  process.env.WALLCHECK_PYTHON || (process.platform === "win32" ? "python" : "python3");

const args = process.argv.slice(2);
const forwarded = args.length > 0 ? args : ["mcp"];

const env = { ...process.env };
env.PYTHONPATH = env.PYTHONPATH
  ? pythonPath + path.delimiter + env.PYTHONPATH
  : pythonPath;

const child = spawn(python, ["-m", "wallcheck", ...forwarded], {
  env,
  stdio: "inherit",
});

child.on("error", (err) => {
  fail(
    `could not start ${python} (${err.message}). wallcheck needs Python 3.11 or newer on PATH.`
  );
});

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => {
    try {
      child.kill(signal);
    } catch {
      /* child already gone */
    }
  });
}

child.on("close", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
  } else {
    process.exit(code ?? 1);
  }
});
