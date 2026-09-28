from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from . import __version__
from .application import ApplicationError, run_file
from .config import AppConfig


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2
EXIT_WRITE_ERROR = 3
COMMANDS = {"check", "run", "report"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="werewolf",
        description="Run the defensive-only Werewolf desktop reference",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "check",
        help="Print installed capabilities and secure-default status",
    )
    run_parser = subparsers.add_parser("run", help="Run a JSON scenario")
    run_parser.add_argument("scenario", type=Path)

    report_parser = subparsers.add_parser(
        "report", help="Run a scenario and write its JSON report"
    )
    report_parser.add_argument("scenario", type=Path)
    report_parser.add_argument("--output", type=Path, required=True)
    return parser


def _normalized_args(argv: Sequence[str]) -> list[str]:
    values = list(argv)
    if values and values[0] not in COMMANDS and not values[0].startswith("-"):
        return ["run", *values]
    return values


def _json(value: object) -> str:
    return json.dumps(value, indent=2)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(_normalized_args(argv or sys.argv[1:]))
    config = AppConfig()
    try:
        if args.command == "check":
            print(
                _json(
                    {
                        "application": "talking-sasquach-werewolf",
                        "version": __version__,
                        "status": "ready",
                        "dry_run": config.dry_run,
                        "remote_actions": config.allow_remote_actions,
                        "capabilities": [
                            "scenario_validation",
                            "defensive_state_simulation",
                            "structured_metrics",
                        ],
                        "limitations": [
                            "no_hardware_integration",
                            "no_production_authentication",
                            "no_operating_system_containment",
                            "no_graphical_interface",
                        ],
                    }
                )
            )
            return EXIT_SUCCESS

        result = run_file(args.scenario, config)
        output = _json(result.state)
        if args.command == "report":
            try:
                args.output.write_text(output + "\n", encoding="utf-8")
            except OSError as error:
                print(f"error: cannot write report: {error}", file=sys.stderr)
                return EXIT_WRITE_ERROR
            print(
                _json(
                    {
                        "status": "written",
                        "output": str(args.output),
                        "accepted_devices": result.accepted_devices,
                        "ignored_devices": result.ignored_devices,
                    }
                )
            )
        else:
            print(output)
        return EXIT_SUCCESS
    except ApplicationError as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_INPUT_ERROR


def console_main() -> None:
    raise SystemExit(main())

