// Launcher tests: drive the real bundled Python MCP server through
// the Node bin shim, exactly as an MCP client would over stdio.
// Fully offline: the tools/call case uses `classify`, which never
// touches the network.
import assert from "node:assert/strict";
import { spawn, execFileSync } from "node:child_process";
import path from "node:path";
import { test, before, after } from "node:test";
import { fileURLToPath } from "node:url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const bin = path.join(root, "bin", "wallcheck.js");

before(() => {
  // Same staging step as `npm run build`.
  execFileSync(process.execPath, [path.join(root, "scripts", "stage-python.mjs")], {
    stdio: "inherit",
  });
});

function startServer() {
  const child = spawn(process.execPath, [bin], { stdio: ["pipe", "pipe", "pipe"] });
  let buffer = "";
  const waiters = new Map();
  child.stdout.setEncoding("utf8");
  child.stdout.on("data", (chunk) => {
    buffer += chunk;
    let idx;
    while ((idx = buffer.indexOf("\n")) >= 0) {
      const line = buffer.slice(0, idx).trim();
      buffer = buffer.slice(idx + 1);
      if (!line) continue;
      const msg = JSON.parse(line);
      if (msg.id !== undefined && waiters.has(msg.id)) {
        waiters.get(msg.id)(msg);
        waiters.delete(msg.id);
      }
    }
  });
  let nextId = 1;
  function request(method, params) {
    const id = nextId++;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error(`timeout waiting for ${method}`)), 20000);
      waiters.set(id, (msg) => {
        clearTimeout(timer);
        resolve(msg);
      });
      child.stdin.write(JSON.stringify({ jsonrpc: "2.0", id, method, params }) + "\n");
    });
  }
  return { child, request };
}

let server;
before(() => {
  server = startServer();
});
after(() => {
  server.child.kill();
});

test("initialize returns the wallcheck server identity", async () => {
  const res = await server.request("initialize", {
    protocolVersion: "2025-06-18",
    capabilities: {},
    clientInfo: { name: "launcher-test", version: "0.0.0" },
  });
  assert.equal(res.result.serverInfo.name, "wallcheck");
  assert.equal(res.result.serverInfo.version, "0.5.0");
});

test("tools/list returns probe_url, classify, scan_exposure, and audit", async () => {
  const res = await server.request("tools/list", {});
  const names = res.result.tools.map((t) => t.name).sort();
  assert.deepEqual(names, ["audit", "classify", "probe_url", "scan_exposure"]);
});

test("tools/call classify classifies a captured response offline", async () => {
  const res = await server.request("tools/call", {
    name: "classify",
    arguments: {
      status: 403,
      headers: { server: "cloudflare", "cf-ray": "8f00000000000000-LAX" },
      body: "Attention Required! | Cloudflare",
    },
  });
  assert.ok(res.result, "expected a result");
  assert.notEqual(res.result.isError, true);
  const payload = res.result.structuredContent;
  assert.ok(payload && typeof payload === "object", "expected structuredContent object");
  assert.equal(typeof payload.verdict, "string");
  assert.ok(payload.verdict.length > 0);
});

test("CLI forwarding: --version prints the Python CLI version", async () => {
  const out = execFileSync(process.execPath, [bin, "--version"], { encoding: "utf8" });
  assert.equal(out.trim(), "wallcheck 0.5.0");
});
