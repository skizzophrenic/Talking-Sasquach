from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def run_check(name: str, command: list[str]) -> dict[str, Any]:
    started = time.monotonic()
    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "name": name,
        "passed": result.returncode == 0,
        "return_code": result.returncode,
        "duration_ms": round((time.monotonic() - started) * 1000),
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the reproducible Werewolf prototype quality gate"
    )
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    args = parser.parse_args()

    checks = [
        run_check(
            "compile",
            [
                sys.executable,
                "-m",
                "compileall",
                "-q",
                "werewolf_game",
                "tests",
                "tools",
            ],
        ),
        run_check(
            "tests",
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-v",
            ],
        ),
        run_check(
            "reference_scenario",
            [
                sys.executable,
                "-m",
                "werewolf_game",
                "examples/werewolf-hunt.json",
            ],
        ),
        run_check(
            "package_smoke",
            [
                sys.executable,
                "tools/package_smoke.py",
            ],
        ),
    ]
    report = {
        "schema_version": 1,
        "passed": all(check["passed"] for check in checks),
        "checks": checks,
    }
    output = json.dumps(report, indent=2)
    print(output)
    if args.output:
        output_path = args.output if args.output.is_absolute() else ROOT / args.output
        output_path.write_text(output + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
