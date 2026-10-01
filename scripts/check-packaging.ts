/** Check the committed plugin package beyond the Agent Skills validator. */

import { posix } from "node:path";
import { buffer } from "node:stream/consumers";

import { extract } from "tar-stream";
import { parseDocument } from "yaml";

import { git, PACKAGE_PATHS } from "./build-plugin.ts";

type PackageFiles = ReadonlyMap<string, Buffer>;

const MCP_URL = "https://mcp.surferseo.com/mcp";
const INTERFACE_FIELDS = [
  "display_name",
  "short_description",
  "default_prompt",
];
const decoder = new TextDecoder("utf8", { fatal: true, ignoreBOM: true });

function matches(value: unknown, pattern: RegExp): value is string {
  return typeof value === "string" && pattern.exec(value)?.[0] === value;
}

function readText(files: PackageFiles, path: string): string {
  const data = files.get(path);

  if (data === undefined) {
    throw new Error(`Missing ${path}`);
  }

  return decoder.decode(data);
}

async function loadPackage(): Promise<PackageFiles> {
  const archive = extract();
  const files = new Map<string, Buffer>();

  archive.end(git("archive", "--format=tar", "HEAD", ...PACKAGE_PATHS));

  for await (const entry of archive) {
    const { name, type } = entry.header;

    if (type === "directory") {
      entry.resume();

      continue;
    }

    if (type !== "file") {
      throw new Error(`Package resource must be a regular file: ${name}`);
    }

    files.set(name, await buffer(entry));
  }

  return files;
}

function checkPlugin(files: PackageFiles, skills: string[]): string[] {
  try {
    const manifest = JSON.parse(readText(files, "plugin.json"));
    const listing = manifest.extensions["com.openai"].interface;

    JSON.parse(readText(files, "mcp.json"));

    const failures: string[] = [];
    const { name, version } = manifest;
    const subtitle = listing.shortDescription;

    if (!matches(name, /^[a-z0-9]+(?:-[a-z0-9]+)*$/) || name.length > 64) {
      failures.push(
        "Plugin name must be lowercase kebab-case, at most 64 characters",
      );
    }

    if (!matches(version, /^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.+-]+)?$/)) {
      failures.push("Plugin version must be safe for a versioned ZIP filename");
    }

    if (typeof subtitle !== "string" || [...subtitle].length > 30) {
      failures.push(
        "Plugin subtitle must be a string of at most 30 characters",
      );
    }

    for (const field of [
      "logo",
      "composerIcon",
      "logoDark",
      "composerIconDark",
    ]) {
      if (!(field in listing)) {
        continue;
      }

      const asset = listing[field];

      if (
        typeof asset !== "string" ||
        posix.isAbsolute(asset) ||
        asset.split("/").includes("..") ||
        !files.has(posix.normalize(asset))
      ) {
        failures.push(
          `${field} must refer to a packaged asset: ${JSON.stringify(asset)}`,
        );
      }
    }

    if (skills.length === 0) {
      failures.push("No committed skills found");
    }

    for (const skill of skills) {
      if (!files.has(`skills/${skill}/SKILL.md`)) {
        failures.push(`Missing SKILL.md for ${skill}`);
      }
    }

    return failures;
  } catch (error) {
    return [`Cannot read plugin metadata: ${error}`];
  }
}

function checkMetadata(files: PackageFiles, path: string): string[] {
  let metadata: unknown;

  try {
    const document = parseDocument(readText(files, path), {
      version: "1.1",
      uniqueKeys: false,
    });
    const error = document.errors[0] ?? document.warnings[0];

    if (error) {
      throw error;
    }

    metadata = document.toJS({ mapAsMap: true });
  } catch (error) {
    return [`${path}: cannot read YAML: ${error}`];
  }

  if (!(metadata instanceof Map)) {
    return [`${path}: expected a YAML mapping`];
  }

  const failures: string[] = [];
  const ui: unknown = metadata.get("interface");

  if (!(ui instanceof Map)) {
    failures.push(`${path}: interface must be a mapping`);
  } else {
    for (const field of INTERFACE_FIELDS) {
      const value: unknown = ui.get(field);

      if (typeof value !== "string" || !value.trim()) {
        failures.push(`${path}: interface.${field} must be a non-empty string`);
      }
    }
  }

  const dependencies: unknown = metadata.get("dependencies");
  const tools: unknown =
    dependencies instanceof Map ? dependencies.get("tools") : undefined;

  if (!Array.isArray(tools)) {
    failures.push(`${path}: dependencies.tools must be a list`);
  } else if (
    !tools.some(
      (tool: unknown) =>
        tool instanceof Map &&
        tool.get("type") === "mcp" &&
        tool.get("transport") === "streamable_http" &&
        tool.get("url") === MCP_URL,
    )
  ) {
    failures.push(
      `${path}: dependencies.tools must include the streamable_http MCP server at ${MCP_URL}`,
    );
  }

  return failures;
}

function checkLicense(
  files: PackageFiles,
  path: string,
  rootLicense: Buffer,
): string[] {
  if (!files.get(path)?.equals(rootLicense)) {
    return [`${path}: must exist and match the root LICENSE byte for byte`];
  }

  return [];
}

async function main(): Promise<number> {
  try {
    const files = await loadPackage();
    const rootLicense = files.get("LICENSE");

    if (rootLicense === undefined) {
      throw new Error("Missing LICENSE");
    }

    const names = [...files.keys()]
      .filter((path) => path.startsWith("skills/"))
      .map((path) => path.split("/")[1]);
    const skills = [...new Set(names)].sort();
    const failures = checkPlugin(files, skills);

    for (const skill of skills) {
      failures.push(
        ...checkMetadata(files, `skills/${skill}/agents/openai.yaml`),
      );
      failures.push(
        ...checkLicense(files, `skills/${skill}/LICENSE`, rootLicense),
      );
    }

    if (failures.length > 0) {
      console.error(failures.join("\n"));

      return 1;
    }

    console.log(
      `Checked committed package, metadata and licenses for ${skills.length} skills`,
    );

    return 0;
  } catch (error) {
    console.error(`Cannot read committed package: ${error}`);

    return 1;
  }
}

if (import.meta.main) {
  process.exitCode = await main();
}
