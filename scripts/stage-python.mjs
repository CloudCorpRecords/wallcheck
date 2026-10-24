// Stage the canonical Python sources (src/wallcheck) into python/
// so the npm tarball carries a fresh copy next to the Node launcher.
// The Python tree under src/ stays the single source of truth; this
// copy is generated at build/pack time and is gitignored.
import { cpSync, existsSync, rmSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const src = path.join(root, "src", "wallcheck");
const dest = path.join(root, "python", "wallcheck");

if (!existsSync(path.join(src, "__main__.py"))) {
  console.error(`stage-python: source tree not found at ${src}`);
  process.exit(1);
}

rmSync(path.join(root, "python"), { recursive: true, force: true });
cpSync(src, dest, {
  recursive: true,
  filter: (p) => !p.includes("__pycache__") && !p.endsWith(".pyc"),
});
console.log(`stage-python: copied ${src} -> ${dest}`);
