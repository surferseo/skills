"""Build a versioned plugin ZIP from the committed resources in HEAD."""

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_PATHS = ("plugin.json", "mcp.json", "LICENSE", "README.md", "skills", "assets")


def build(output_dir: Path) -> Path:
    metadata = subprocess.check_output(
        ["git", "show", "HEAD:plugin.json"], cwd=ROOT, text=True, encoding="utf-8"
    )
    manifest = json.loads(metadata)
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{manifest['name']}-{manifest['version']}.zip"
    command = ["git", "archive", "--format=zip", f"--prefix={manifest['name']}/"]
    command.extend([f"--output={output}", "HEAD", *PACKAGE_PATHS])
    subprocess.run(command, cwd=ROOT, check=True)
    print(output)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "dist",
        help="ZIP destination directory",
    )
    build(parser.parse_args().output_dir.resolve())
