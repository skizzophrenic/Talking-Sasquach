from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


def _boolean(value: dict[str, Any], field_name: str) -> bool:
    parsed = value.get(field_name, False)
    if type(parsed) is not bool:
        raise ValueError(f"{field_name} must be a boolean")
    return parsed


class DeviceClass(str, Enum):
    FLIPPER = "flipper"
    PWNAGOTCHI = "pwnagotchi"
    BJORN = "bjorn"
    TAMAFI = "tamafi"
    PINEAPPLE = "pineapple"
    PHONES64 = "phones64"
    WIFI7 = "wifi7"
    NANO = "nano"
    SHARKBITE = "sharkbite"
    OTHER = "other"


class GameMode(str, Enum):
    DORMANT = "dormant"
    GUARD = "guard"
    DEFENCE = "defence"


@dataclass(frozen=True)
class AttackAlert:
    alert_id: str
    detector: str
    target_device_id: str
    reason: str
    severity: int
    trusted: bool = False

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "AttackAlert":
        return cls(
            alert_id=str(value["alert_id"]),
            detector=str(value["detector"]),
            target_device_id=str(value["target_device_id"]),
            reason=str(value["reason"]),
            severity=int(value["severity"]),
            trusted=_boolean(value, "trusted"),
        )


@dataclass(frozen=True)
class NearbyDevice:
    device_id: str
    device_class: DeviceClass
    signal_dbm: int
    opted_in: bool = False
    game_beacon_valid: bool = False
    battle_power: int = 0
    connected_first: bool = False
    beacon_id: str | None = None
    issued_at: int | None = None
    expires_at: int | None = None

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "NearbyDevice":
        return cls(
            device_id=str(value["device_id"]),
            device_class=DeviceClass(value.get("device_class", "other")),
            signal_dbm=int(value.get("signal_dbm", -100)),
            opted_in=_boolean(value, "opted_in"),
            game_beacon_valid=_boolean(value, "game_beacon_valid"),
            battle_power=max(0, int(value.get("battle_power", 0))),
            connected_first=_boolean(value, "connected_first"),
            beacon_id=(
                str(value["beacon_id"]) if value.get("beacon_id") is not None else None
            ),
            issued_at=(
                int(value["issued_at"]) if value.get("issued_at") is not None else None
            ),
            expires_at=(
                int(value["expires_at"]) if value.get("expires_at") is not None else None
            ),
        )


@dataclass
class Metrics:
    scans: int = 0
    devices_seen: int = 0
    opted_in_devices: int = 0
    ignored_devices: int = 0
    invalid_beacons: int = 0
    expired_beacons: int = 0
    replayed_beacons: int = 0
    invalid_alerts: int = 0
    attacks_detected: int = 0
    guard_mode_entries: int = 0
    energy_collected: int = 0
    defence_actions: int = 0
    attacks_blocked: int = 0
    defence_failures: int = 0
    shields_used: int = 0
    protected_sessions: int = 0
    detections_by_class: dict[str, int] = field(default_factory=dict)


@dataclass
class GameState:
    mode: GameMode = GameMode.DORMANT
    skin: str = "werewolf"
    energy: int = 20
    shield: int = 0
    score: int = 0
    streak: int = 0
    last_target: str | None = None
    assistant_messages: dict[str, str] = field(
        default_factory=lambda: {
            "guardian": "Dormant. The defensive layer activates only on an attack alert.",
            "privacy_sentinel": "No privacy warning.",
            "update_guide": "No firmware update is active.",
        }
    )
    metrics: Metrics = field(default_factory=Metrics)
    event_log: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
