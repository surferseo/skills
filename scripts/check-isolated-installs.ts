/**
 * Install the skills with the skills CLI into empty projects and compare the copies
 * byte for byte against skills/. Override the CLI with SKILLS_CLI, for example
 * SKILLS_CLI="npx --yes skills@1.7.0".
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readdirSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const [cli, ...cliArgs] = (process.env.SKILLS_CLI ?? 'npx --yes skills@1.7.0').split(/\s+/);
const AGENT_DIRS: Record<string, string> = { codex: '.agents/skills', 'claude-code': '.claude/skills' };

function fail(...context: unknown[]): never {
  console.error(...context);
  process.exit(1);
}

// Sorted relative paths of every file under dir.
function files(dir: string): string[] {
  return readdirSync(dir, { recursive: true, withFileTypes: true })
    .filter((entry) => entry.isFile())
    .map((entry) => relative(dir, join(entry.parentPath, entry.name)))
    .sort();
}

// Install `skill` for `agent` into a fresh temp project, check which skill folders appeared
// and that each matches skills/<name> byte for byte.
function check(skill: string, agent: string, expected: string[]): void {
  const project = mkdtempSync(join(tmpdir(), 'surfer-install-'));
  try {
    execFileSync(cli, [...cliArgs, 'add', ROOT, '--skill', skill, '--agent', agent, '--yes', '--copy'], {
      cwd: project,
      stdio: 'inherit',
    });
    const installedDir = join(project, AGENT_DIRS[agent]);
    const installed = readdirSync(installedDir).filter((name) => name.startsWith('surfer-')).sort();
    if (installed.join() !== expected.join()) fail(agent, skill, 'installed', installed, 'expected', expected);
    for (const name of installed) {
      const source = join(ROOT, 'skills', name);
      const copy = join(installedDir, name);
      if (files(source).join() !== files(copy).join()) fail(name, files(source), files(copy));
      for (const path of files(source)) {
        if (!readFileSync(join(source, path)).equals(readFileSync(join(copy, path)))) fail(name, path, 'differs');
      }
    }
    console.log(`Verified ${agent} install of ${skill}: ${installed.length} skill(s)`);
  } finally {
    rmSync(project, { recursive: true, force: true });
  }
}

const allSkills = readdirSync(join(ROOT, 'skills'), { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .sort();
for (const name of ['surfer-create-outline', 'surfer-connect']) check(name, 'codex', [name]);
for (const agent of Object.keys(AGENT_DIRS)) check('*', agent, allSkills);
