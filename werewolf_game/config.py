from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    max_scenario_bytes: int = 1_048_576
    dry_run: bool = True
    allow_remote_actions: bool = False

    def __post_init__(self) -> None:
        if self.max_scenario_bytes <= 0:
            raise ValueError("max_scenario_bytes must be positive")
        if not self.dry_run:
            raise ValueError("This reference application supports dry-run mode only")
        if self.allow_remote_actions:
            raise ValueError("Remote actions are prohibited")

