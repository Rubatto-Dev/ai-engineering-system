from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_engineering_os.jarvis import JarvisEngine


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a full Jarvis cycle")
    parser.add_argument("--project", required=True)
    parser.add_argument("--cycle", type=int, default=1)
    parser.add_argument("--mode", default="autopilot_safe")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    engine = JarvisEngine(repo_root)

    outputs = [
        engine.handle(f"JARVIS: START project={args.project}"),
        engine.handle(f"JARVIS: PLAN cycle={args.cycle}"),
        engine.handle(f"JARVIS: EXEC cycle={args.cycle} mode={args.mode}"),
        engine.handle("JARVIS: AUDIT repo=current tests_ok=true security_ok=true sonar_ok=true"),
    ]
    print(json.dumps(outputs, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
