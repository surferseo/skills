"""Check the committed plugin package beyond the Agent Skills reference validator."""

import json
import re
import subprocess
import sys
import tarfile
from io import BytesIO
from pathlib import PurePosixPath

import yaml

from build_plugin import PACKAGE_PATHS, ROOT

MCP_URL = "https://mcp.surferseo.com/mcp"
INTERFACE_FIELDS = ("display_name", "short_description", "default_prompt")


def load_package() -> dict[str, bytes]:
    """Read the same committed resources selected by the ZIP builder."""
    data = subprocess.check_output(
        ["git", "archive", "--format=tar", "HEAD", *PACKAGE_PATHS], cwd=ROOT
    )
    files = {}
    with tarfile.open(fileobj=BytesIO(data)) as archive:
        for entry in archive:
            if entry.isdir():
                continue
            if not entry.isfile():
                raise ValueError(
                    f"Package resource must be a regular file: {entry.name}"
                )
            files[entry.name] = archive.extractfile(entry).read()
    return files


def check_plugin(files: dict[str, bytes], skills: list[str]) -> list[str]:
    """Check plugin metadata, skill entry points, and packaged asset references."""
    try:
        manifest = json.loads(files["plugin.json"].decode("utf-8"))
        json.loads(files["mcp.json"].decode("utf-8"))
        name, version = manifest["name"], manifest["version"]
        interface = manifest["extensions"]["com.openai"]["interface"]
        subtitle = interface["shortDescription"]
    except (KeyError, TypeError, ValueError) as error:
        return [f"Cannot read plugin metadata: {error}"]

    failures = []
    if (
        not isinstance(name, str)
        or len(name) > 64
        or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)
    ):
        failures.append(
            "Plugin name must be lowercase kebab-case, at most 64 characters"
        )
    if not isinstance(version, str) or not re.fullmatch(
        r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.+-]+)?", version
    ):
        failures.append("Plugin version must be safe for a versioned ZIP filename")
    if not isinstance(subtitle, str) or len(subtitle) > 30:
        failures.append("Plugin subtitle must be a string of at most 30 characters")
    for field in ("logo", "composerIcon", "logoDark", "composerIconDark"):
        if field in interface:
            asset = interface[field]
            if not isinstance(asset, str) or str(PurePosixPath(asset)) not in files:
                failures.append(f"{field} must refer to a packaged asset: {asset}")

    if not skills:
        failures.append("No committed skills found")
    for skill in skills:
        if f"skills/{skill}/SKILL.md" not in files:
            failures.append(f"Missing SKILL.md for {skill}")
    return failures


def check_metadata(files: dict[str, bytes], path: str) -> list[str]:
    """Check OpenAI metadata, which the Agent Skills spec does not cover."""
    try:
        metadata = yaml.safe_load(files[path].decode("utf-8"))
    except (KeyError, UnicodeError, yaml.YAMLError) as error:
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


def check_license(files: dict[str, bytes], path: str, root_license: bytes) -> list[str]:
    """Each skill carries its own license when installed separately."""
    if files.get(path) != root_license:
        return [f"{path}: must exist and match the root LICENSE byte for byte"]
    return []


def main() -> int:
    try:
        files = load_package()
        root_license = files["LICENSE"]
    except (
        OSError,
        ValueError,
        KeyError,
        tarfile.TarError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"Cannot read committed package: {error}", file=sys.stderr)
        return 1

    skills = sorted(
        {path.split("/")[1] for path in files if path.startswith("skills/")}
    )
    failures = check_plugin(files, skills)
    for skill in skills:
        failures.extend(check_metadata(files, f"skills/{skill}/agents/openai.yaml"))
        failures.extend(check_license(files, f"skills/{skill}/LICENSE", root_license))

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1

    print(f"Checked committed package, metadata and licenses for {len(skills)} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
