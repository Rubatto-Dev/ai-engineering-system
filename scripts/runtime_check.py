from __future__ import annotations

import json
from pathlib import Path

from ai_engineering_os.external_runtime import evaluate_runtime_readiness


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    result = evaluate_runtime_readiness(repo_root)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
