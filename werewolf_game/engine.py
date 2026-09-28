from __future__ import annotations

from dataclasses import dataclass
from time import time
from typing import Callable, Iterable

from .models import AttackAlert, DeviceClass, GameMode, GameState, NearbyDevice


HUNT_TARGETS = {
    DeviceClass.FLIPPER,
    DeviceClass.PWNAGOTCHI,
    DeviceClass.BJORN,
    DeviceClass.TAMAFI,
}

ENERGY_SOURCES = {
    DeviceClass.PINEAPPLE: 30,
    DeviceClass.PHONES64: 24,
    DeviceClass.WIFI7: 20,
    DeviceClass.NANO: 16,
    DeviceClass.SHARKBITE: 26,
}

ENERGY_CAP = 100
SHIELD_CAP = 60
MAX_EVENT_LOG = 500
MAX_BEACON_LIFETIME_SECONDS = 300
MAX_ALERT_REPLAY_IDS = 1_024
MAX_RESOLVED_ALERT_REPLAY_IDS = 1_024


@dataclass(frozen=True)
class ScanResult:
    accepted: tuple[NearbyDevice, ...]
    ignored: tuple[NearbyDevice, ...]
    rejection_reasons: dict[str, str]


class AssistantSuite:
    """Deterministic local advisors; they send no data off-device."""

    def advise(
        self,
        state: GameState,
        nearby: Iterable[NearbyDevice],
        *,
        rejected_count: int = 0,
    ) -> dict[str, str]:
        devices = tuple(nearby)
        sources = [d for d in devices if d.device_class in ENERGY_SOURCES]

        if state.mode is GameMode.DORMANT:
            guardian = "Dormant. The defensive layer activates only on an attack alert."
        elif state.energy < 20 and sources:
            best = max(sources, key=lambda d: ENERGY_SOURCES[d.device_class])
            guardian = (
                f"Attack active. Use the {best.device_class.value} game beacon "
                "to reinforce defence."
            )
        elif state.shield < 15:
            guardian = "Attack active. Isolate the session and raise the defence shield."
        else:
            guardian = "Guard mode: block and isolate the alerted session."

        privacy = (
            f"Ignored {rejected_count} invalid, replayed, expired, or non-consenting beacon(s)."
            if rejected_count
            else "All observed game beacons passed consent and authenticity checks."
        )
        return {
            "guardian": guardian,
            "privacy_sentinel": privacy,
            "update_guide": "No firmware update is active.",
        }


class GameEngine:
    def __init__(
        self,
        state: GameState | None = None,
        *,
        clock: Callable[[], float] = time,
    ) -> None:
        self.state = state or GameState()
        self.assistants = AssistantSuite()
        self._clock = clock
        self._seen_beacons: dict[str, int] = {}
        self._seen_alerts: dict[str, None] = {}
        self._resolved_alerts: dict[str, None] = {}
        self._active_alert: AttackAlert | None = None

    def report_attack(self, alert: AttackAlert) -> bool:
        valid = (
            alert.trusted
            and bool(alert.alert_id.strip())
            and bool(alert.detector.strip())
            and bool(alert.target_device_id.strip())
            and bool(alert.reason.strip())
            and 1 <= alert.severity <= 5
            and alert.alert_id not in self._seen_alerts
        )
        if not valid:
            self.state.metrics.invalid_alerts += 1
            self._event("alert_rejected", alert_id=alert.alert_id)
            return False

        self._active_alert = alert
        self._remember_replay_id(
            self._seen_alerts,
            alert.alert_id,
            MAX_ALERT_REPLAY_IDS,
        )
        self.state.metrics.attacks_detected += 1
        if self.state.mode is GameMode.DORMANT:
            self.state.metrics.guard_mode_entries += 1
        self.state.mode = GameMode.GUARD
        self.state.skin = "full_moon"
        self.state.last_target = alert.target_device_id
        self._event(
            "guard_mode",
            alert_id=alert.alert_id,
            detector=alert.detector,
            reason=alert.reason,
            severity=alert.severity,
            target_device_id=alert.target_device_id,
        )
        self.state.assistant_messages = self.assistants.advise(self.state, ())
        return True

    def clear_incident(self) -> None:
        self._active_alert = None
        self.state.mode = GameMode.DORMANT
        self.state.skin = "werewolf"
        self.state.last_target = None
        self._event("incident_cleared")
        self.state.assistant_messages = self.assistants.advise(self.state, ())

    def scan(self, devices: Iterable[NearbyDevice]) -> ScanResult:
        nearby = tuple(devices)
        accepted: list[NearbyDevice] = []
        ignored: list[NearbyDevice] = []
        rejection_reasons: dict[str, str] = {}
        metrics = self.state.metrics
        metrics.scans += 1
        metrics.devices_seen += len(nearby)
        now = int(self._clock())
        self._prune_expired_beacons(now)

        for device in nearby:
            reason = self._validate_beacon(device, now)
            if reason is None:
                accepted.append(device)
                self._seen_beacons[device.beacon_id or ""] = (
                    device.expires_at if device.expires_at is not None else now
                )
            else:
                ignored.append(device)
                rejection_reasons[device.device_id] = reason
                if reason == "expired":
                    metrics.expired_beacons += 1
                elif reason == "replayed":
                    metrics.replayed_beacons += 1
                else:
                    metrics.invalid_beacons += 1

        accepted_tuple = tuple(accepted)
        ignored_tuple = tuple(ignored)
        metrics.opted_in_devices += len(accepted_tuple)
        metrics.ignored_devices += len(ignored_tuple)

        for device in accepted_tuple:
            name = device.device_class.value
            metrics.detections_by_class[name] = metrics.detections_by_class.get(name, 0) + 1

        for source in (
            d
            for d in accepted_tuple
            if self._active_alert is not None and d.device_class in ENERGY_SOURCES
        ):
            gained = min(ENERGY_SOURCES[source.device_class], ENERGY_CAP - self.state.energy)
            self.state.energy += gained
            metrics.energy_collected += gained
            self._event(
                "energy_collected",
                device_id=source.device_id,
                device_class=source.device_class.value,
                amount=gained,
            )

        self.state.assistant_messages = self.assistants.advise(
            self.state,
            accepted_tuple,
            rejected_count=len(ignored_tuple),
        )
        self._assert_invariants()
        return ScanResult(
            accepted=accepted_tuple,
            ignored=ignored_tuple,
            rejection_reasons=rejection_reasons,
        )

    def charge_shield(self, energy: int) -> int:
        if self._active_alert is None:
            raise ValueError("Shield charging requires an active trusted alert")
        requested = max(0, energy)
        transferred = min(requested, self.state.energy, SHIELD_CAP - self.state.shield)
        self.state.energy -= transferred
        self.state.shield += transferred
        if transferred:
            self.state.skin = "shielded"
            self._event("shield_charged", amount=transferred)
        self._assert_invariants()
        return transferred

    def defend(self, opponent: NearbyDevice) -> str:
        if (
            self._active_alert is None
            or self._active_alert.target_device_id != opponent.device_id
        ):
            raise ValueError("Defence requires an attack alert from the host firmware")
        if self._active_alert.alert_id in self._resolved_alerts:
            raise ValueError("This attack alert has already been resolved")
        if opponent.device_class not in HUNT_TARGETS:
            raise ValueError("This device class is not a recognized defensive profile")

        self.state.mode = GameMode.DEFENCE
        self.state.last_target = opponent.device_id
        self.state.metrics.defence_actions += 1

        initiative = 10 if opponent.connected_first else 20
        protection = self.state.energy + self.state.shield + initiative
        threat = opponent.battle_power + (20 if opponent.connected_first else 0)
        shield_spent = min(self.state.shield, max(0, threat - self.state.energy))
        self.state.shield -= shield_spent
        if shield_spent:
            self.state.metrics.shields_used += 1

        if protection >= threat:
            outcome = "blocked"
            self.state.metrics.attacks_blocked += 1
            self.state.metrics.protected_sessions += 1
            self.state.score += 100 + self.state.streak * 25
            self.state.streak += 1
            self.state.skin = "secured"
        else:
            outcome = "defence_failed"
            self.state.metrics.defence_failures += 1
            self.state.streak = 0
            self.state.skin = "wounded"

        self.state.energy = max(0, self.state.energy - 15)
        self.state.mode = GameMode.GUARD
        self._remember_replay_id(
            self._resolved_alerts,
            self._active_alert.alert_id,
            MAX_RESOLVED_ALERT_REPLAY_IDS,
        )
        self._event(
            "defence",
            opponent_id=opponent.device_id,
            opponent_class=opponent.device_class.value,
            opponent_connected_first=opponent.connected_first,
            outcome=outcome,
            response="block_and_isolate",
        )
        self.state.assistant_messages["guardian"] = (
            "Attack blocked. Session isolated and protected."
            if outcome == "blocked"
            else "Defence failed. Disconnect, preserve logs, and alert the owner."
        )
        self._assert_invariants()
        return outcome

    def _validate_beacon(self, device: NearbyDevice, now: int) -> str | None:
        if (
            not device.opted_in
            or not device.game_beacon_valid
            or not device.beacon_id
            or device.issued_at is None
            or device.expires_at is None
            or device.expires_at < device.issued_at
            or device.expires_at - device.issued_at > MAX_BEACON_LIFETIME_SECONDS
            or device.issued_at > now
        ):
            return "invalid"
        if device.expires_at < now:
            return "expired"
        if device.beacon_id in self._seen_beacons:
            return "replayed"
        return None

    def _prune_expired_beacons(self, now: int) -> None:
        self._seen_beacons = {
            beacon_id: expires_at
            for beacon_id, expires_at in self._seen_beacons.items()
            if expires_at >= now
        }

    def _remember_replay_id(
        self,
        replay_ids: dict[str, None],
        replay_id: str,
        limit: int,
    ) -> None:
        replay_ids[replay_id] = None
        protected_id = (
            self._active_alert.alert_id if self._active_alert is not None else None
        )
        while len(replay_ids) > limit:
            oldest_id = next(
                candidate for candidate in replay_ids if candidate != protected_id
            )
            del replay_ids[oldest_id]

    def _assert_invariants(self) -> None:
        if not 0 <= self.state.energy <= ENERGY_CAP:
            raise RuntimeError("Energy invariant violated")
        if not 0 <= self.state.shield <= SHIELD_CAP:
            raise RuntimeError("Shield invariant violated")
        if self.state.mode is not GameMode.DORMANT and self._active_alert is None:
            raise RuntimeError("Active defence mode requires a trusted alert")
        if self.state.mode is GameMode.DORMANT and self.state.skin != "werewolf":
            raise RuntimeError("Dormant mode requires the werewolf skin")
        if self.state.metrics.attacks_blocked > self.state.metrics.defence_actions:
            raise RuntimeError("Blocked attacks cannot exceed defence actions")

    def _event(self, event_type: str, **details: object) -> None:
        self.state.event_log.append({"type": event_type, **details})
        if len(self.state.event_log) > MAX_EVENT_LOG:
            del self.state.event_log[:-MAX_EVENT_LOG]
