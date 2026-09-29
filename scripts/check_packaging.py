#!/usr/bin/env python3
"""Check the packaging the official validators do not cover.

skills-ref, OpenAI's quick_validate.py, and `claude plugin validate` check SKILL.md
frontmatter. This script checks the rest of each skills/<name>/ package:

- agents/openai.yaml UI metadata and the Surfer MCP dependency ChatGPT and Codex read
- a standalone LICENSE identical to the root one, so single-skill installs stay licensed
- relative links in SKILL.md that resolve
- stray system files anywhere in the repository, which block directory submissions

Run `python scripts/check_packaging.py --links` to also confirm every http(s) URL answers.
"""
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / 'skills'
MCP_URL = 'https://mcp.surferseo.com/mcp'
STRAY = {'.DS_Store', 'Thumbs.db', 'desktop.ini', '__MACOSX'}
errors = []


def fail(message):
    errors.append(message)


def check_openai(skill_dir):
    path = skill_dir / 'agents' / 'openai.yaml'
    try:
        ui = yaml.safe_load(path.read_text(encoding='utf-8'))
    except (OSError, yaml.YAMLError) as exc:
        fail(f'{path}: missing or invalid: {exc}')
        return
    if not isinstance(ui, dict):
        fail(f'{path}: must be a mapping')
        return
    unknown = set(ui) - {'interface', 'policy', 'dependencies'}
    if unknown:
        fail(f'{path}: unknown top-level keys {sorted(unknown)}')
    interface = ui.get('interface')
    if not isinstance(interface, dict):
        fail(f'{path}: interface must be a mapping')
    else:
        for field in ('display_name', 'short_description', 'default_prompt'):
            value = interface.get(field)
            if not isinstance(value, str) or not value.strip():
                fail(f'{path}: interface.{field} must be a nonempty string')
        for field in ('icon_small', 'icon_large'):
            value = interface.get(field)
            if value is not None and not (skill_dir / value).exists():
                fail(f'{path}: interface.{field} points to a missing file {value}')
        color = interface.get('brand_color')
        if color is not None and not re.fullmatch(r'#[0-9A-Fa-f]{6}', str(color)):
            fail(f'{path}: interface.brand_color must be a #RRGGBB hex value')
    policy = ui.get('policy')
    if policy is not None:
        if not isinstance(policy, dict) or not isinstance(policy.get('allow_implicit_invocation', True), bool):
            fail(f'{path}: policy.allow_implicit_invocation must be a boolean')
    dependencies = ui.get('dependencies')
    tools = dependencies.get('tools') if isinstance(dependencies, dict) else None
    if not isinstance(tools, list) or not tools:
        fail(f'{path}: dependencies.tools must declare the Surfer MCP server')
        return
    surfer = False
    for tool in tools:
        if not isinstance(tool, dict):
            fail(f'{path}: each dependency must be a mapping')
            continue
        if tool.get('type') != 'mcp':
            fail(f'{path}: dependency type must be mcp')
        if not isinstance(tool.get('value'), str) or not tool['value']:
            fail(f'{path}: dependency value must be a nonempty string')
        if tool.get('transport') != 'streamable_http':
            fail(f'{path}: dependency transport must be streamable_http')
        url = tool.get('url')
        if not isinstance(url, str) or not url.startswith('https://'):
            fail(f'{path}: dependency url must be https')
        if url == MCP_URL:
            surfer = True
    if not surfer:
        fail(f'{path}: no dependency points at {MCP_URL}')


def check_skill(skill_dir):
    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.exists():
        fail(f'{skill_dir}: missing SKILL.md')
        return
    check_openai(skill_dir)
    notice = skill_dir / 'LICENSE'
    if not notice.exists() or notice.read_bytes() != ROOT_LICENSE:
        fail(f'{skill_dir}: LICENSE must exist and match the root LICENSE')
    body = skill_md.read_text(encoding='utf-8')
    for target in re.findall(r'\]\(([^)#\s]+)(?:#[^)]*)?\)', body):
        if target.startswith(('http://', 'https://', 'mailto:')):
            continue
        if not (skill_dir / target).exists():
            fail(f'{skill_md}: broken relative link {target}')


def check_links():
    urls = set()
    for path in [ROOT / 'README.md', *SKILLS.glob('*/SKILL.md'), *SKILLS.glob('*/agents/openai.yaml')]:
        urls.update(re.findall(r'https?://[^\s)<>`"\']+', path.read_text(encoding='utf-8')))
    for url in sorted(urls):
        if url.startswith(MCP_URL):
            continue  # answers 401 without OAuth
        request = urllib.request.Request(url.rstrip('.,'), headers={'User-Agent': 'surfer-skills-validator'})
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                if response.status >= 400:
                    fail(f'{url}: HTTP {response.status}')
        except urllib.error.HTTPError as exc:
            fail(f'{url}: HTTP {exc.code}')
        except Exception as exc:  # noqa: BLE001
            fail(f'{url}: {exc}')


ROOT_LICENSE = (ROOT / 'LICENSE').read_bytes()
for stray in ROOT.rglob('*'):
    if stray.name in STRAY and '.git' not in stray.parts:
        fail(f'{stray}: remove system files before publishing')
skill_dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir())
if not skill_dirs:
    fail('no skills found under skills/')
for skill_dir in skill_dirs:
    check_skill(skill_dir)
if len((ROOT / 'README.md').read_text(encoding='utf-8').split()) < 40:
    fail('README.md must have at least 40 words')
if '--links' in sys.argv[1:]:
    check_links()

if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'Checked packaging of {len(skill_dirs)} skills')
