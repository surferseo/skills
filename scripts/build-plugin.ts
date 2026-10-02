/** Build a versioned plugin ZIP from the committed resources in HEAD. */

import { execFileSync } from "node:child_process";
import { mkdirSync } from "node:fs";
import { resolve } from "node:path";
import { parseArgs } from "node:util";

export const ROOT = resolve(import.meta.dirname, "..");
export const PACKAGE_PATHS = [
  "plugin.json",
  "mcp.json",
  "LICENSE",
  "README.md",
  "skills",
  "assets",
];

export function git(...args: string[]): Buffer {
  return execFileSync("git", args, {
    cwd: ROOT,
    maxBuffer: 64 * 1024 * 1024,
  });
}

function buildPlugin(outputDir = resolve(ROOT, "dist")): string {
  const { name, version }: { name: string; version: string } = JSON.parse(
    git("show", "HEAD:plugin.json").toString("utf8"),
  );
  const output = resolve(outputDir, `${name}-${version}.zip`);

  mkdirSync(outputDir, { recursive: true });
  git(
    "archive",
    "--format=zip",
    `--prefix=${name}/`,
    `--output=${output}`,
    "HEAD",
    ...PACKAGE_PATHS,
  );

  return output;
}

if (import.meta.main) {
  const { values } = parseArgs({
    options: {
      "output-dir": { type: "string" },
      help: { type: "boolean", short: "h" },
    },
  });

  if (values.help) {
    console.log("Usage: node scripts/build-plugin.ts [--output-dir DIRECTORY]");
  } else {
    console.log(buildPlugin(values["output-dir"]));
  }
}
