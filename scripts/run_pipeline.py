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
    parser.add_argument("--proposal-file", dest="proposal_file")
    parser.add_argument("--strict-external", action="store_true")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    engine = JarvisEngine(repo_root)
    start_command = f"JARVIS: START project={args.project}"
    if args.proposal_file:
        start_command += f" proposal_file={args.proposal_file}"

    audit_command = "JARVIS: AUDIT repo=current tests_ok=true security_ok=true sonar_ok=true"
    if args.strict_external:
        audit_command += " strict_external=true"

    outputs = [
        engine.handle(start_command),
        engine.handle(f"JARVIS: PLAN cycle={args.cycle}"),
        engine.handle(f"JARVIS: EXEC cycle={args.cycle} mode={args.mode}"),
        engine.handle(audit_command),
    ]
    print(json.dumps(outputs, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
