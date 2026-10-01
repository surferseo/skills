"""Check packaging details beyond the Agent Skills reference validator."""

import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

import yaml

from build_plugin import PACKAGE_PATHS, ROOT

MCP_URL = "https://mcp.surferseo.com/mcp"
INTERFACE_FIELDS = ("display_name", "short_description", "default_prompt")


def validate_plugin() -> None:
    """Check plugin metadata and the tracked resources selected for packaging."""
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z", "--", *PACKAGE_PATHS], cwd=ROOT, text=True
    )
    files = set(filter(None, tracked.split("\0")))
    for filename in files:
        source = ROOT / filename
        if (
            source.is_symlink()
            or not source.is_file()
            or not source.resolve().is_relative_to(ROOT)
        ):
            raise ValueError(
                f"Package resource must be a contained regular file: {filename}"
            )

    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    json.loads((ROOT / "mcp.json").read_text(encoding="utf-8"))
    name, version = manifest["name"], manifest["version"]
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        raise ValueError(
            "Plugin name must be lowercase kebab-case, at most 64 characters"
        )
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.+-]+)?", version):
        raise ValueError("Plugin version must be safe for a versioned ZIP filename")

    skill_names = {
        PurePosixPath(filename).parts[1]
        for filename in files
        if filename.startswith("skills/")
    }
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


def check_metadata(path: Path) -> list[str]:
    """Check OpenAI metadata, which the Agent Skills spec does not cover."""
    try:
        metadata = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        return [f"{path}: cannot read YAML: {error}"]

    if not isinstance(metadata, dict):
        return [f"{path}: expected a YAML mapping"]

    failures = []
    interface = metadata.get("interface")
    if not isinstance(interface, dict):
        failures.append(f"{path}: interface must be a mapping")
    else:
        for field in INTERFACE_FIELDS:
            value = interface.get(field)
            if not isinstance(value, str) or not value.strip():
                failures.append(f"{path}: interface.{field} must be a non-empty string")

    dependencies = metadata.get("dependencies")
    tools = dependencies.get("tools") if isinstance(dependencies, dict) else None
    if not isinstance(tools, list):
        failures.append(f"{path}: dependencies.tools must be a list")
    elif not any(
        isinstance(tool, dict)
        and tool.get("type") == "mcp"
        and tool.get("transport") == "streamable_http"
        and tool.get("url") == MCP_URL
        for tool in tools
    ):
        failures.append(
            f"{path}: dependencies.tools must include the streamable_http "
            f"MCP server at {MCP_URL}"
        )

    return failures


def check_license(path: Path, root_license: bytes) -> list[str]:
    """Each skill carries its own license when installed separately."""
    try:
        license_bytes = path.read_bytes()
    except OSError as error:
        return [f"{path}: cannot read license: {error}"]

    if license_bytes != root_license:
        return [f"{path}: must match the root LICENSE byte for byte"]

    return []


def main() -> int:
    try:
        validate_plugin()
        root_license = (ROOT / "LICENSE").read_bytes()
        skills = sorted(path for path in (ROOT / "skills").iterdir() if path.is_dir())
    except (
        OSError,
        UnicodeError,
        ValueError,
        KeyError,
        TypeError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"Cannot read or validate package: {error}", file=sys.stderr)
        return 1

    if not skills:
        print("No skill directories found", file=sys.stderr)
        return 1

    failures = []
    for skill in skills:
        failures.extend(check_metadata(skill / "agents" / "openai.yaml"))
        failures.extend(check_license(skill / "LICENSE", root_license))

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1

    print(f"Checked plugin packaging, metadata and licenses for {len(skills)} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
