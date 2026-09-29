/**
 * Install the skills with the skills CLI into empty projects and compare the copies
 * file by file against skills/. Override the CLI with SKILLS_CLI, for example
 * SKILLS_CLI="npx --yes skills@1.7.0".
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readdirSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const [cliCommand, ...cliArgs] = (process.env.SKILLS_CLI ?? 'npx --yes skills@1.7.0').split(/\s+/);
const SOURCE_SKILLS = readdirSync(join(ROOT, 'skills'), { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .sort();
const AGENT_DIRS: Record<string, string> = { codex: '.agents/skills', 'claude-code': '.claude/skills' };

const assert = (condition: boolean, ...context: unknown[]): void => {
  if (!condition) {
    console.error(...context);
    process.exit(1);
  }
};

function filesUnder(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true, recursive: true })
    .filter((entry) => entry.isFile())
    .map((entry) => relative(dir, join(entry.parentPath, entry.name)))
    .sort();
}

function install(target: string, skill: string, agent: string): string {
  execFileSync(cliCommand, [...cliArgs, 'add', ROOT, '--skill', skill, '--agent', agent, '--yes', '--copy'], {
    cwd: target,
    stdio: 'inherit',
  });
  return join(target, AGENT_DIRS[agent]);
}

function compare(name: string, installed: string): number {
  const source = join(ROOT, 'skills', name);
  const sourceFiles = filesUnder(source);
  const installedFiles = filesUnder(installed);
  assert(JSON.stringify(sourceFiles) === JSON.stringify(installedFiles), name, sourceFiles, installedFiles);
  for (const path of sourceFiles) {
    assert(readFileSync(join(source, path)).equals(readFileSync(join(installed, path))), name, path, 'differs');
  }
  return sourceFiles.length;
}

function withTempDir(prefix: string, run: (dir: string) => void): void {
  const dir = mkdtempSync(join(tmpdir(), prefix));
  try {
    run(dir);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

for (const name of ['surfer-create-outline', 'surfer-connect']) {
  withTempDir('surfer-install-', (dir) => {
    const skillsDir = install(dir, name, 'codex');
    const packages = readdirSync(skillsDir).filter((entry) => entry.startsWith('surfer-')).sort();
    assert(JSON.stringify(packages) === JSON.stringify([name]), packages);
    const count = compare(name, join(skillsDir, name));
    console.log(`Isolated install verified: ${name} (${count} files)`);
  });
}

for (const agent of Object.keys(AGENT_DIRS)) {
  withTempDir('surfer-install-all-', (dir) => {
    const skillsDir = install(dir, '*', agent);
    const installed = readdirSync(skillsDir).filter((entry) => entry.startsWith('surfer-')).sort();
    assert(JSON.stringify(installed) === JSON.stringify(SOURCE_SKILLS), agent, installed, SOURCE_SKILLS);
    for (const name of installed) compare(name, join(skillsDir, name));
    console.log(`All-skills install verified for ${agent}: ${installed.length} skills`);
  });
}
