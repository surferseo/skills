/**
 * Check the packaging the official validators do not cover.
 *
 * skills-ref, OpenAI's quick_validate.py, and `claude plugin validate` check SKILL.md
 * frontmatter. This script checks the rest of each skills/<name>/ package:
 *
 * - agents/openai.yaml UI metadata and the Surfer MCP dependency ChatGPT and Codex read
 * - a standalone LICENSE identical to the root one, so single-skill installs stay licensed
 * - relative links in SKILL.md that resolve
 * - stray system files anywhere in the repository, which block directory submissions
 *
 * Run `node scripts/check-packaging.ts --links` to also confirm every http(s) URL answers.
 */
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse } from 'yaml';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SKILLS = join(ROOT, 'skills');
const MCP_URL = 'https://mcp.surferseo.com/mcp';
const STRAY = new Set(['.DS_Store', 'Thumbs.db', 'desktop.ini', '__MACOSX']);
const errors: string[] = [];

const fail = (message: string): void => {
  errors.push(message);
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const isText = (value: unknown): value is string => typeof value === 'string' && value.trim() !== '';

function checkOpenAI(skillDir: string): void {
  const path = join(skillDir, 'agents', 'openai.yaml');
  let ui: unknown;
  try {
    ui = parse(readFileSync(path, 'utf8'));
  } catch (error) {
    fail(`${path}: missing or invalid: ${(error as Error).message}`);
    return;
  }
  if (!isRecord(ui)) {
    fail(`${path}: must be a mapping`);
    return;
  }
  const unknown = Object.keys(ui).filter((key) => !['interface', 'policy', 'dependencies'].includes(key));
  if (unknown.length > 0) fail(`${path}: unknown top-level keys ${JSON.stringify(unknown)}`);

  const ui_ = ui.interface;
  if (!isRecord(ui_)) {
    fail(`${path}: interface must be a mapping`);
  } else {
    for (const field of ['display_name', 'short_description', 'default_prompt']) {
      if (!isText(ui_[field])) fail(`${path}: interface.${field} must be a nonempty string`);
    }
    for (const field of ['icon_small', 'icon_large']) {
      const value = ui_[field];
      if (value !== undefined && !(typeof value === 'string' && existsSync(join(skillDir, value)))) {
        fail(`${path}: interface.${field} points to a missing file ${String(value)}`);
      }
    }
    const color = ui_.brand_color;
    if (color !== undefined && !/^#[0-9A-Fa-f]{6}$/.test(String(color))) {
      fail(`${path}: interface.brand_color must be a #RRGGBB hex value`);
    }
  }

  const policy = ui.policy;
  if (policy !== undefined) {
    const flag = isRecord(policy) ? policy.allow_implicit_invocation : undefined;
    if (!isRecord(policy) || (flag !== undefined && typeof flag !== 'boolean')) {
      fail(`${path}: policy.allow_implicit_invocation must be a boolean`);
    }
  }

  const tools = isRecord(ui.dependencies) ? ui.dependencies.tools : undefined;
  if (!Array.isArray(tools) || tools.length === 0) {
    fail(`${path}: dependencies.tools must declare the Surfer MCP server`);
    return;
  }
  let surfer = false;
  for (const tool of tools as unknown[]) {
    if (!isRecord(tool)) {
      fail(`${path}: each dependency must be a mapping`);
      continue;
    }
    if (tool.type !== 'mcp') fail(`${path}: dependency type must be mcp`);
    if (!isText(tool.value)) fail(`${path}: dependency value must be a nonempty string`);
    if (tool.transport !== 'streamable_http') fail(`${path}: dependency transport must be streamable_http`);
    const url = tool.url;
    if (typeof url !== 'string' || !url.startsWith('https://')) fail(`${path}: dependency url must be https`);
    if (url === MCP_URL) surfer = true;
  }
  if (!surfer) fail(`${path}: no dependency points at ${MCP_URL}`);
}

function checkSkill(skillDir: string): void {
  const skillMd = join(skillDir, 'SKILL.md');
  if (!existsSync(skillMd)) {
    fail(`${skillDir}: missing SKILL.md`);
    return;
  }
  checkOpenAI(skillDir);
  const notice = join(skillDir, 'LICENSE');
  if (!existsSync(notice) || !readFileSync(notice).equals(ROOT_LICENSE)) {
    fail(`${skillDir}: LICENSE must exist and match the root LICENSE`);
  }
  const body = readFileSync(skillMd, 'utf8');
  for (const match of body.matchAll(/\]\(([^)#\s]+)(?:#[^)]*)?\)/g)) {
    const target = match[1];
    if (/^(https?:|mailto:)/.test(target)) continue;
    if (!existsSync(join(skillDir, target))) fail(`${skillMd}: broken relative link ${target}`);
  }
}

function listFiles(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    if (entry.name === '.git' || entry.name === 'node_modules') return [];
    const path = join(dir, entry.name);
    return entry.isDirectory() ? [path, ...listFiles(path)] : [path];
  });
}

async function checkLinks(): Promise<void> {
  const sources = [join(ROOT, 'README.md')];
  for (const skill of skillDirs) sources.push(join(skill, 'SKILL.md'), join(skill, 'agents', 'openai.yaml'));
  const urls = new Set<string>();
  for (const source of sources) {
    for (const match of readFileSync(source, 'utf8').matchAll(/https?:\/\/[^\s)<>`"']+/g)) {
      urls.add(match[0].replace(/[.,]+$/, ''));
    }
  }
  await Promise.all(
    [...urls].sort().map(async (url) => {
      if (url.startsWith(MCP_URL)) return; // answers 401 without OAuth
      try {
        const response = await fetch(url, {
          headers: { 'User-Agent': 'surfer-skills-validator' },
          signal: AbortSignal.timeout(20_000),
        });
        if (response.status >= 400) fail(`${url}: HTTP ${response.status}`);
      } catch (error) {
        fail(`${url}: ${(error as Error).message}`);
      }
    }),
  );
}

const ROOT_LICENSE = readFileSync(join(ROOT, 'LICENSE'));
for (const path of listFiles(ROOT)) {
  if (STRAY.has(path.split('/').pop() ?? '')) fail(`${path}: remove system files before publishing`);
}
const skillDirs = readdirSync(SKILLS, { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => join(SKILLS, entry.name))
  .sort();
if (skillDirs.length === 0) fail('no skills found under skills/');
for (const skillDir of skillDirs) checkSkill(skillDir);
if (readFileSync(join(ROOT, 'README.md'), 'utf8').split(/\s+/).filter(Boolean).length < 40) {
  fail('README.md must have at least 40 words');
}
if (process.argv.includes('--links')) await checkLinks();

if (errors.length > 0) {
  console.error(errors.join('\n'));
  process.exit(1);
}
console.log(`Checked packaging of ${skillDirs.length} skills`);
