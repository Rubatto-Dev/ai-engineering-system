from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_engineering_os.template_pack import initialize_client_template_packet


def main() -> int:
    parser = argparse.ArgumentParser(description="Create standardized client template packet.")
    parser.add_argument("--client", default="cliente_demo", help="Client name")
    parser.add_argument("--project", default="projeto_demo", help="Project name")
    parser.add_argument("--owner", default="equipe", help="Owner or account manager")
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        help="Output folder relative to repo root. Default: proposals/packets/<client>_<project>",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite files if they already exist.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    result = initialize_client_template_packet(
        repo_root,
        client_name=args.client,
        project_name=args.project,
        owner_name=args.owner,
        output_dir=args.output_dir,
        overwrite=args.overwrite,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
