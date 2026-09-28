#!/usr/bin/env python3
"""Check portable skill metadata, included notices, and REST map structure."""
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / 'skills'
ID = re.compile(r'`([a-z][a-z0-9_]*__[a-z][a-z0-9_]*)`')
ROW = re.compile(r'^\| `([^`]+)` \| (.+) \| (.+) \| (https://[^ |]+) \|$')
MCP_ONLY = {'brand__get', 'brand__update', 'recommendation__list', 'recommendation__optimize', 'server__info'}
errors = []

def fail(message):
    errors.append(message)

root_license = (ROOT / 'LICENSE').read_bytes()
paths = sorted(SKILLS.glob('*/SKILL.md'))
if len(paths) != 8:
    fail(f'Expected eight skills, found {len(paths)}')

for path in paths:
    content = path.read_text()
    match = re.match(r'\A---\n(.*?)\n---\n', content, re.S)
    if not match:
        fail(f'{path}: missing YAML frontmatter')
        continue
    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        fail(f'{path}: invalid YAML: {exc}')
        continue
    if not isinstance(metadata, dict):
        fail(f'{path}: frontmatter must be a mapping')
        continue
    if metadata.get('name') != path.parent.name:
        fail(f'{path}: name must match its directory')
    description = metadata.get('description')
    if not isinstance(description, str) or not 1 <= len(description) <= 1024:
        fail(f'{path}: description must have 1–1024 characters')
    if metadata.get('license') != 'MIT':
        fail(f'{path}: missing MIT license metadata')
    notice = path.parent / 'LICENSE'
    if not notice.exists() or notice.read_bytes() != root_license:
        fail(f'{path}: missing or altered standalone license notice')
    for target in re.findall(r'\]\(([^)#]+)(?:#[^)]*)?\)', content):
        if not target.startswith(('http://', 'https://', 'mailto:')) and not (path.parent / target).exists():
            fail(f'{path}: broken relative link {target}')

map_path = SKILLS / 'surfer-api/capability-map.md'
rows = []
for line in map_path.read_text().splitlines():
    match = ROW.fullmatch(line)
    if match:
        rows.append(match.groups())
ids = [row[0] for row in rows]
if len(ids) != len(set(ids)):
    fail('REST capability map has duplicate IDs')
if len(ids) < 30:
    fail(f'REST capability map appears incomplete: {len(ids)} entries')
for capability, method_path, scope, url in rows:
    if not re.match(r'^(?:(?:GET|POST|PUT|PATCH|DELETE)\b|\*\*Composite\.)', method_path):
        fail(f'{capability}: missing HTTP method or composite mapping')
    if not url.startswith('https://app.surferseo.com/llms/') or not url.endswith('.txt'):
        fail(f'{capability}: unexpected live documentation URL')
    if not scope:
        fail(f'{capability}: empty workspace scope')

for target in re.findall(r'\]\(([^)#]+)(?:#[^)]*)?\)', (ROOT / 'README.md').read_text()):
    if not target.startswith(('http://', 'https://', 'mailto:')) and not (ROOT / target).exists():
        fail(f'README.md: broken relative link {target}')

for path in paths:
    if path.parent.name in ('surfer-api', 'surfer-connect'):
        continue
    used = set(ID.findall(path.read_text()))
    for capability in sorted(used - set(ids) - MCP_ONLY):
        fail(f'{path}: {capability} has no REST map entry or MCP-only declaration')

if errors:
    print('\n'.join(f'ERROR: {error}' for error in errors), file=sys.stderr)
    sys.exit(1)
print(f'Validated {len(paths)} skill packages and {len(rows)} REST bindings')
