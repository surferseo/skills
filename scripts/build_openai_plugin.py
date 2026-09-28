#!/usr/bin/env python3
"""Build a reproducible portable plugin ZIP from the canonical tracked skills."""

import argparse
import hashlib
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXED_FILES = {
    "plugin.json": ROOT / "plugin.json",
    "mcp.json": ROOT / "mcp.json",
    "LICENSE": ROOT / "LICENSE",
    "README.md": ROOT / "docs" / "openai-plugin.md",
}


def package_files() -> dict[str, Path]:
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z", "--", "skills"], cwd=ROOT
    ).decode().split("\0")
    files = dict(FIXED_FILES)
    for name in filter(None, tracked):
        source = ROOT / name
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"Tracked skill resource must be a regular file: {name}")
        files[name] = source

    skill_roots = {Path(name).parts[1] for name in files if name.startswith("skills/")}
    if not skill_roots:
        raise ValueError("No tracked skills found")
    for skill in skill_roots:
        if f"skills/{skill}/SKILL.md" not in files:
            raise ValueError(f"Missing SKILL.md for {skill}")
    for name, source in files.items():
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"Package file must be a regular file: {name}")
    return files


def build(output: Path) -> None:
    files = package_files()
    payloads = {name: source.read_bytes() for name, source in files.items()}
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w") as archive:
        for name, data in sorted(payloads.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    with zipfile.ZipFile(output) as archive:
        if archive.namelist() != sorted(payloads) or archive.testzip() is not None:
            raise ValueError("Archive contents or CRC check failed")
        for name, data in payloads.items():
            if archive.read(name) != data:
                raise ValueError(f"Archive differs from source: {name}")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(f"{output} ({len(payloads)} files, SHA-256 {digest})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="ZIP destination")
    build(parser.parse_args().output.resolve())
