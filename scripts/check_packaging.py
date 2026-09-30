"""Check packaging details beyond the Agent Skills reference validator."""

import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MCP_URL = "https://mcp.surferseo.com/mcp"
INTERFACE_FIELDS = ("display_name", "short_description", "default_prompt")


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
        root_license = (ROOT / "LICENSE").read_bytes()
        skills = sorted(path for path in (ROOT / "skills").iterdir() if path.is_dir())
    except OSError as error:
        print(f"Cannot read skills or root LICENSE: {error}", file=sys.stderr)
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

    print(f"Checked metadata and licenses for {len(skills)} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
