from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from time import time
from typing import Any, Callable

from .config import AppConfig
from .engine import GameEngine
from .models import AttackAlert, NearbyDevice


class ApplicationError(Exception):
    """Expected application failure safe to display without a traceback."""


class InputError(ApplicationError):
    """Scenario input is missing, malformed, or violates the contract."""


@dataclass(frozen=True)
class RunResult:
    state: dict[str, Any]
    accepted_devices: int
    ignored_devices: int


def load_scenario(path: Path, config: AppConfig) -> dict[str, Any]:
    try:
        size = path.stat().st_size
    except OSError as error:
        raise InputError(f"Cannot read scenario: {error}") from error
    if size > config.max_scenario_bytes:
        raise InputError(
            f"Scenario exceeds the {config.max_scenario_bytes}-byte limit"
        )
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise InputError(f"Invalid scenario: {error}") from error
    if not isinstance(value, dict) or not isinstance(value.get("devices"), list):
        raise InputError("Scenario must be an object containing a devices array")
    return value


def run_scenario(
    scenario: dict[str, Any],
    *,
    clock: Callable[[], float] = time,
) -> RunResult:
    try:
        devices = tuple(
            NearbyDevice.from_dict(item) for item in scenario["devices"]
        )
        current_time = scenario.get("current_time")
        engine = GameEngine(
            clock=(lambda: float(current_time))
            if current_time is not None
            else clock
        )
        if scenario.get("attack_alert") is not None:
            alert = AttackAlert.from_dict(scenario["attack_alert"])
            if not engine.report_attack(alert):
                raise InputError("Scenario attack alert was rejected")
        scan_result = engine.scan(devices)
        shield_charge = int(scenario.get("shield_charge", 0))
        if shield_charge:
            engine.charge_shield(shield_charge)

        attacker_id = scenario.get("attacker_device_id")
        if attacker_id is not None:
            opponent = next(
                (device for device in devices if device.device_id == attacker_id),
                None,
            )
            if opponent is None:
                raise InputError(
                    "attacker_device_id must reference a detected device"
                )
            engine.defend(opponent)
    except InputError:
        raise
    except (KeyError, TypeError, ValueError) as error:
        raise InputError(str(error)) from error

    return RunResult(
        state=engine.state.to_dict(),
        accepted_devices=len(scan_result.accepted),
        ignored_devices=len(scan_result.ignored),
    )


def run_file(path: Path, config: AppConfig) -> RunResult:
    return run_scenario(load_scenario(path, config))

