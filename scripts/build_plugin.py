"""Build a reproducible plugin ZIP from the repository's tracked resources."""

import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
FIXED_FILES = {"plugin.json", "mcp.json", "LICENSE", "README.md"}


def build(output_dir: Path) -> Path:
    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    json.loads((ROOT / "mcp.json").read_text(encoding="utf-8"))
    name = manifest["name"]
    version = manifest["version"]
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        raise ValueError("Plugin name must be lowercase kebab-case, at most 64 characters")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.+-]+)?", version):
        raise ValueError("Plugin version must be safe for a versioned ZIP filename")

    tracked = subprocess.check_output(
        ["git", "ls-files", "-z", "--", "skills", "assets", ".codex-plugin"],
        cwd=ROOT,
    ).decode().split("\0")
    files = FIXED_FILES | set(filter(None, tracked))
    skill_names = {PurePosixPath(file).parts[1] for file in files if file.startswith("skills/")}
    if not skill_names:
        raise ValueError("No tracked skills found")
    for skill in skill_names:
        if f"skills/{skill}/SKILL.md" not in files:
            raise ValueError(f"Missing SKILL.md for {skill}")

    interface = manifest["extensions"]["com.openai"]["interface"]
    if len(interface["shortDescription"]) > 30:
        raise ValueError("Plugin subtitle exceeds 30 characters")
    for field in ("logo", "composerIcon", "logoDark", "composerIconDark"):
        if field in interface:
            asset = PurePosixPath(interface[field])
            if asset.is_absolute() or ".." in asset.parts or str(asset) not in files:
                raise ValueError(f"{field} must refer to a packaged asset: {asset}")

    payloads = {}
    for file in sorted(files):
        source = ROOT / file
        if source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(ROOT):
            raise ValueError(f"Package resource must be a contained regular file: {file}")
        payloads[f"{name}/{file}"] = source.read_bytes()

    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{name}-{version}.zip"
    with zipfile.ZipFile(output, "w") as archive:
        for file, data in payloads.items():
            entry = zipfile.ZipInfo(file, date_time=(1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    with zipfile.ZipFile(output) as archive:
        if archive.namelist() != list(payloads) or archive.testzip() is not None:
            raise ValueError("Archive contents or CRC check failed")
        for file, data in payloads.items():
            if archive.read(file) != data:
                raise ValueError(f"Archive differs from source: {file}")

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(f"{output} ({len(skill_names)} skills, {len(payloads)} files, SHA-256 {digest})")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist", help="ZIP destination directory")
    args = parser.parse_args()
    build(args.output_dir.resolve())
