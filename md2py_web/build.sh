#!/usr/bin/env bash
#
# build.sh — md2py_web release builder
#
# Cleans previous artifacts, compiles TypeScript, then assembles a
# self-contained release/ folder containing only the files needed to run
# md2py_web with `node release/dist/index.js`.
#
# Usage:  ./build.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "[build] root: $ROOT"

# 1. Clean
echo "[build] cleaning dist/ release/"
rm -rf dist release

# 2. Compile TypeScript
echo "[build] compiling TypeScript (npx tsc)"
npx --no-install tsc

if [ ! -d dist/src ]; then
  echo "[build] ERROR: dist/src was not produced by tsc" >&2
  exit 1
fi

# 3. Run tests on the freshly built artifacts
echo "[build] running tests"
node --test dist/tests/*.test.js > /dev/null

# 4. Assemble release/
echo "[build] assembling release/"
mkdir -p release/dist

# Only copy compiled src/ — never tests/ — into the release.
cp -r dist/src/* release/dist/

# Documentation and metadata
cp README.md release/
cp history.md release/
cp LICENSE release/ 2>/dev/null || true

# Slimmed-down package.json: drop devDependencies and scripts that
# reference build tools, since the release ships only runtime artifacts.
cat > release/package.json <<'JSON'
{
  "name": "md2py_web",
  "version": "0.1.0",
  "description": "Markdown to printable HTML / PDF — TypeScript port of md2pdf with zero runtime dependencies.",
  "type": "module",
  "bin": {
    "md2py-web": "dist/index.js"
  },
  "scripts": {
    "start": "node dist/index.js"
  },
  "dependencies": {},
  "license": "MIT"
}
JSON

# Convenience launcher
cat > release/run.sh <<'SH'
#!/usr/bin/env bash
# Convenience launcher for md2py_web. Forwards all args to node.
HERE="$(cd "$(dirname "$0")" && pwd)"
exec node "$HERE/dist/index.js" "$@"
SH
chmod +x release/run.sh

# Make the entry point executable too
chmod +x release/dist/index.js 2>/dev/null || true

# 5. Summary
echo "[build] release contents:"
( cd release && find . -maxdepth 3 -type f | sort | sed 's/^/  /' )

echo "[build] done. Run with:  ./release/run.sh --webui -p 8080"
