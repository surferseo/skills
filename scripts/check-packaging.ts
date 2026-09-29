/**
 * Packaging checks the official validators (skills-ref, OpenAI's quick_validate.py,
 * `claude plugin validate`) do not cover: agents/openai.yaml metadata and the Surfer MCP
 * dependency, a per-skill LICENSE identical to the root one, and relative links in SKILL.md.
 * Pass --links to also confirm every documented http(s) URL answers.
 */
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse } from 'yaml';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const MCP_URL = 'https://mcp.surferseo.com/mcp';
const LICENSE = readFileSync(join(ROOT, 'LICENSE'));
const skills = readdirSync(join(ROOT, 'skills'), { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => join(ROOT, 'skills', entry.name))
  .sort();
const failures: string[] = [];
const read = (path: string): string => (existsSync(path) ? readFileSync(path, 'utf8') : '');

for (const dir of skills) {
  const yamlPath = join(dir, 'agents', 'openai.yaml');
  let ui: any;
  try {
    ui = parse(read(yamlPath));
  } catch (error) {
    failures.push(`${yamlPath}: ${(error as Error).message}`);
  }
  for (const field of ['display_name', 'short_description', 'default_prompt']) {
    const value = ui?.interface?.[field];
    if (typeof value !== 'string' || !value.trim()) failures.push(`${yamlPath}: interface.${field} must be a non-empty string`);
  }
  const tools: any[] = Array.isArray(ui?.dependencies?.tools) ? ui.dependencies.tools : [];
  if (!tools.some((t) => t?.type === 'mcp' && t.transport === 'streamable_http' && t.url === MCP_URL)) {
    failures.push(`${yamlPath}: dependencies.tools must include the streamable_http MCP server at ${MCP_URL}`);
  }

  const license = join(dir, 'LICENSE');
  if (!existsSync(license) || !readFileSync(license).equals(LICENSE)) failures.push(`${license}: must match the root LICENSE`);

  const skillMd = join(dir, 'SKILL.md');
  for (const [, target] of read(skillMd).matchAll(/\]\(([^)#\s]+)(?:#[^)]*)?\)/g)) {
    if (!/^(https?|mailto):/.test(target) && !existsSync(join(dir, target))) failures.push(`${skillMd}: broken link ${target}`);
  }
}

if (process.argv.includes('--links')) {
  const sources = [join(ROOT, 'README.md'), ...skills.flatMap((d) => [join(d, 'SKILL.md'), join(d, 'agents', 'openai.yaml')])];
  const urls = new Set(sources.flatMap((s) => [...read(s).matchAll(/https?:\/\/[^\s)<>`"']+/g)].map((m) => m[0].replace(/[.,]+$/, ''))));
  await Promise.all([...urls].filter((url) => !url.startsWith(MCP_URL)).map(async (url) => {
    try {
      const response = await fetch(url, { signal: AbortSignal.timeout(20_000) });
      if (response.status >= 400) failures.push(`${url}: HTTP ${response.status}`);
    } catch (error) {
      failures.push(`${url}: ${(error as Error).message}`);
    }
  }));
}

if (failures.length > 0) {
  console.error(failures.join('\n'));
  process.exit(1);
}
console.log(`Checked ${skills.length} skills`);
