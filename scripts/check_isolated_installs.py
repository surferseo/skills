#!/usr/bin/env python3
"""Install the skills with the skills CLI into empty projects and compare the copies."""
from pathlib import Path
import os
import shlex
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CLI = shlex.split(os.environ.get('SKILLS_CLI', 'npx --yes skills@1.7.0'))
SOURCE_SKILLS = sorted(p.name for p in (ROOT / 'skills').iterdir() if p.is_dir())
AGENT_DIRS = {'codex': '.agents/skills', 'claude-code': '.claude/skills'}


def install(target, skill, agent):
    subprocess.run(CLI + ['add', str(ROOT), '--skill', skill, '--agent', agent, '--yes', '--copy'], cwd=target, check=True)
    return target / AGENT_DIRS[agent]


def compare(name, installed):
    source = ROOT / 'skills' / name
    source_files = sorted(p.relative_to(source) for p in source.rglob('*') if p.is_file())
    installed_files = sorted(p.relative_to(installed) for p in installed.rglob('*') if p.is_file())
    assert source_files == installed_files, (name, source_files, installed_files)
    for path in source_files:
        assert (source / path).read_bytes() == (installed / path).read_bytes(), (name, path)
    return len(source_files)


for name in ('surfer-create-outline', 'surfer-connect'):
    with tempfile.TemporaryDirectory(prefix='surfer-install-') as directory:
        skills_dir = install(Path(directory), name, 'codex')
        packages = sorted(skills_dir.glob('surfer-*'))
        assert [p.name for p in packages] == [name], packages
        count = compare(name, packages[0])
        print(f'Isolated install verified: {name} ({count} files)')

for agent in AGENT_DIRS:
    with tempfile.TemporaryDirectory(prefix='surfer-install-all-') as directory:
        skills_dir = install(Path(directory), '*', agent)
        installed = sorted(p.name for p in skills_dir.glob('surfer-*'))
        assert installed == SOURCE_SKILLS, (agent, installed, SOURCE_SKILLS)
        for name in installed:
            compare(name, skills_dir / name)
        print(f'All-skills install verified for {agent}: {len(installed)} skills')
