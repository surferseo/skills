#!/usr/bin/env python3
"""Exercise the pinned skills CLI with truly isolated single-skill installs."""
from pathlib import Path
import os
import shlex
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CLI = shlex.split(os.environ.get('SKILLS_CLI', 'npx --yes skills@1.7.0'))
for name in ('surfer-create-content-brief', 'surfer-content-recommendations', 'surfer-api'):
    with tempfile.TemporaryDirectory(prefix='surfer-install-') as directory:
        target = Path(directory)
        subprocess.run(CLI + ['add', str(ROOT), '--skill', name, '--agent', 'codex', '--yes', '--copy'], cwd=target, check=True)
        packages = sorted((target / '.agents/skills').glob('surfer-*'))
        assert [p.name for p in packages] == [name], packages
        source = ROOT / 'skills' / name
        installed = packages[0]
        source_files = sorted(p.relative_to(source) for p in source.rglob('*') if p.is_file())
        installed_files = sorted(p.relative_to(installed) for p in installed.rglob('*') if p.is_file())
        assert source_files == installed_files, (name, source_files, installed_files)
        for path in source_files:
            assert (source / path).read_bytes() == (installed / path).read_bytes(), (name, path)
        print(f'Isolated install verified: {name} ({len(source_files)} files)')

with tempfile.TemporaryDirectory(prefix='surfer-install-all-') as directory:
    target = Path(directory)
    subprocess.run(CLI + ['add', str(ROOT), '--skill', '*', '--agent', 'codex', '--yes', '--copy'], cwd=target, check=True)
    installed = sorted(p.name for p in (target / '.agents/skills').glob('surfer-*'))
    source = sorted(p.name for p in (ROOT / 'skills').glob('surfer-*'))
    assert installed == source, (installed, source)
    print(f'All-skills install verified: {len(installed)} skills')

with tempfile.TemporaryDirectory(prefix='surfer-install-subset-') as directory:
    target = Path(directory)
    subset = {'surfer-write-article', 'surfer-connect', 'surfer-api'}
    subprocess.run(CLI + ['add', str(ROOT), '--skill', 'surfer-write-article',
                          '--skill', 'surfer-connect', '--skill', 'surfer-api',
                          '--agent', 'codex', '--yes', '--copy'], cwd=target, check=True)
    installed = {p.name for p in (target / '.agents/skills').glob('surfer-*')}
    assert installed == subset, (installed, subset)
    print('Three-skill README subset verified')
