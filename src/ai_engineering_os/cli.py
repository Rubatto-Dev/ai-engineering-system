from __future__ import annotations

import argparse
import json
from pathlib import Path

from .jarvis import JarvisEngine


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Jarvis command protocol")
    parser.add_argument("command", nargs="+", help="Command text, e.g. JARVIS: START project=demo")
    parser.add_argument("--repo", default=".", help="Repository root path")
    args = parser.parse_args()

    command_text = " ".join(args.command)
    engine = JarvisEngine(Path(args.repo).resolve())
    result = engine.handle(command_text)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
