import io
import random
import unittest
from unittest.mock import patch

from werewolf_game import AttackAlert, DeviceClass, GameEngine, NearbyDevice
from werewolf_game.cli import EXIT_INPUT_ERROR, EXIT_SUCCESS, main
from werewolf_game.engine import (
    ENERGY_CAP,
    MAX_ALERT_REPLAY_IDS,
    MAX_EVENT_LOG,
    MAX_RESOLVED_ALERT_REPLAY_IDS,
    SHIELD_CAP,
)


NOW = 1_000


def device(
    device_id: str,
    device_class: DeviceClass,
    *,
    opted_in: bool = True,
    valid: bool = True,
    power: int = 0,
    first: bool = False,
    beacon_id: str | None = None,
    issued_at: int = NOW - 10,
    expires_at: int = NOW + 10,
) -> NearbyDevice:
    return NearbyDevice(
        device_id=device_id,
        device_class=device_class,
        signal_dbm=-40,
        opted_in=opted_in,
        game_beacon_valid=valid,
        battle_power=power,
        connected_first=first,
        beacon_id=beacon_id or f"beacon-{device_id}",
        issued_at=issued_at,
        expires_at=expires_at,
    )


def alert(
    target: str = "target",
    *,
    alert_id: str = "alert-1",
    trusted: bool = True,
    severity: int = 4,
) -> AttackAlert:
    return AttackAlert(
        alert_id=alert_id,
        detector="host-integrity-monitor",
        target_device_id=target,
        reason="unauthorized protected-route access",
        severity=severity,
        trusted=trusted,
    )


class GameEngineTests(unittest.TestCase):
    def make_engine(self) -> GameEngine:
        return GameEngine(clock=lambda: NOW)

    def test_untrusted_devices_are_ignored(self) -> None:
        engine = self.make_engine()
        result = engine.scan(
            [device("unknown", DeviceClass.FLIPPER, opted_in=False, valid=False)]
        )

        self.assertEqual(result.accepted, ())
        self.assertEqual(result.rejection_reasons["unknown"], "invalid")
        self.assertEqual(engine.state.mode.value, "dormant")
        self.assertEqual(engine.state.metrics.ignored_devices, 1)
        self.assertIn("Ignored 1", engine.state.assistant_messages["privacy_sentinel"])

    def test_nearby_target_without_host_alert_stays_dormant(self) -> None:
        engine = self.make_engine()
        engine.scan([device("pwny", DeviceClass.PWNAGOTCHI)])

        self.assertEqual(engine.state.mode.value, "dormant")
        self.assertEqual(engine.state.skin, "werewolf")
        self.assertEqual(engine.state.metrics.attacks_detected, 0)

    def test_trusted_alert_activates_full_moon_guard_mode(self) -> None:
        engine = self.make_engine()

        self.assertTrue(engine.report_attack(alert("pwny")))
        self.assertEqual(engine.state.mode.value, "guard")
        self.assertEqual(engine.state.skin, "full_moon")
        self.assertEqual(engine.state.metrics.guard_mode_entries, 1)
        self.assertIn("isolate", engine.state.assistant_messages["guardian"].lower())

    def test_untrusted_invalid_and_replayed_alerts_fail_closed(self) -> None:
        engine = self.make_engine()

        self.assertFalse(engine.report_attack(alert(trusted=False)))
        self.assertFalse(engine.report_attack(alert(severity=8, alert_id="alert-2")))
        self.assertTrue(engine.report_attack(alert()))
        self.assertFalse(engine.report_attack(alert()))
        self.assertEqual(engine.state.metrics.attacks_detected, 1)
        self.assertEqual(engine.state.metrics.invalid_alerts, 3)

    def test_power_source_requires_active_alert(self) -> None:
        engine = self.make_engine()
        engine.scan([device("fruit", DeviceClass.PINEAPPLE)])

        self.assertEqual(engine.state.energy, 20)
        with self.assertRaisesRegex(ValueError, "active trusted alert"):
            engine.charge_shield(10)

    def test_cli_allows_default_zero_charge_without_alert(self) -> None:
        scenario = {"current_time": NOW, "devices": []}

        with (
            patch("sys.argv", ["werewolf_game", "scenario.json"]),
            patch("werewolf_game.cli.run_file") as run_file,
            patch("sys.stdout", new_callable=io.StringIO) as output,
        ):
            from werewolf_game.application import RunResult

            run_file.return_value = RunResult(
                state={"mode": "dormant"},
                accepted_devices=0,
                ignored_devices=0,
            )
            exit_code = main()

        self.assertEqual(exit_code, EXIT_SUCCESS)
        self.assertIn('"mode": "dormant"', output.getvalue())

    def test_cli_rejects_nonzero_charge_without_alert(self) -> None:
        from pathlib import Path
        from tempfile import TemporaryDirectory

        scenario = '{"current_time":1000,"devices":[],"shield_charge":1}'
        with TemporaryDirectory() as directory:
            path = Path(directory) / "scenario.json"
            path.write_text(scenario, encoding="utf-8")
            with (
                patch("sys.stderr", new_callable=io.StringIO) as error,
            ):
                exit_code = main(["run", str(path)])

        self.assertEqual(exit_code, EXIT_INPUT_ERROR)
        self.assertIn("active trusted alert", error.getvalue())

    def test_json_boolean_fields_require_actual_booleans(self) -> None:
        alert_value = {
            "alert_id": "alert",
            "detector": "detector",
            "target_device_id": "target",
            "reason": "reason",
            "severity": 1,
            "trusted": "false",
        }
        with self.assertRaisesRegex(ValueError, "trusted must be a boolean"):
            AttackAlert.from_dict(alert_value)

        base_device = {
            "device_id": "device",
            "device_class": "nano",
            "signal_dbm": -40,
        }
        for field_name in ("opted_in", "game_beacon_valid", "connected_first"):
            with self.subTest(field_name=field_name):
                with self.assertRaisesRegex(
                    ValueError, rf"{field_name} must be a boolean"
                ):
                    NearbyDevice.from_dict(
                        {**base_device, field_name: "false"}
                    )

    def test_power_source_adds_energy_during_incident(self) -> None:
        engine = self.make_engine()
        engine.report_attack(alert("attacker"))
        engine.scan([device("fruit", DeviceClass.PINEAPPLE)])

        self.assertEqual(engine.state.energy, 50)
        self.assertEqual(engine.charge_shield(25), 25)
        self.assertEqual(engine.state.energy, 25)
        self.assertEqual(engine.state.shield, 25)

    def test_replayed_beacon_cannot_add_energy_twice(self) -> None:
        engine = self.make_engine()
        engine.report_attack(alert("attacker"))
        source = device("fruit", DeviceClass.PINEAPPLE)

        engine.scan([source])
        result = engine.scan([source])

        self.assertEqual(engine.state.energy, 50)
        self.assertEqual(result.rejection_reasons["fruit"], "replayed")
        self.assertEqual(engine.state.metrics.replayed_beacons, 1)

    def test_beacon_replay_tracking_expires_with_beacon(self) -> None:
        now = [NOW]
        engine = GameEngine(clock=lambda: now[0])
        original = device("nano", DeviceClass.NANO, expires_at=NOW + 1)

        self.assertEqual(engine.scan([original]).accepted, (original,))
        now[0] = NOW + 1
        self.assertEqual(
            engine.scan([original]).rejection_reasons["nano"],
            "replayed",
        )
        now[0] = NOW + 2
        replacement = device(
            "nano",
            DeviceClass.NANO,
            issued_at=NOW + 2,
            expires_at=NOW + 12,
        )
        self.assertEqual(engine.scan([replacement]).accepted, (replacement,))
        self.assertEqual(len(engine._seen_beacons), 1)

    def test_beacon_replay_tracking_stays_bounded_under_load(self) -> None:
        now = [NOW]
        engine = GameEngine(clock=lambda: now[0])

        for batch in range(20):
            engine.scan(
                [
                    device(
                        f"nano-{batch}-{index}",
                        DeviceClass.NANO,
                        issued_at=now[0],
                        expires_at=now[0] + 1,
                    )
                    for index in range(100)
                ]
            )
            now[0] += 2

        engine.scan([])
        self.assertEqual(engine._seen_beacons, {})

    def test_expired_future_and_overlong_beacons_are_rejected(self) -> None:
        engine = self.make_engine()
        result = engine.scan(
            [
                device("expired", DeviceClass.NANO, expires_at=NOW - 1),
                device("future", DeviceClass.NANO, issued_at=NOW + 1),
                device(
                    "overlong",
                    DeviceClass.NANO,
                    issued_at=NOW - 1,
                    expires_at=NOW + 400,
                ),
            ]
        )

        self.assertEqual(result.rejection_reasons["expired"], "expired")
        self.assertEqual(result.rejection_reasons["future"], "invalid")
        self.assertEqual(result.rejection_reasons["overlong"], "invalid")

    def test_defence_blocks_and_isolates_alerted_target(self) -> None:
        engine = self.make_engine()
        target = device("flip", DeviceClass.FLIPPER, power=30)
        engine.report_attack(alert("flip"))
        engine.scan([target])

        self.assertEqual(engine.defend(target), "blocked")
        self.assertEqual(engine.state.metrics.attacks_blocked, 1)
        self.assertEqual(engine.state.event_log[-1]["response"], "block_and_isolate")
        with self.assertRaisesRegex(ValueError, "already been resolved"):
            engine.defend(target)

    def test_first_connection_changes_defence_advantage(self) -> None:
        target = device("bjorn", DeviceClass.BJORN, power=25, first=True)
        engine = self.make_engine()
        engine.report_attack(alert("bjorn"))
        engine.scan([target])

        self.assertEqual(engine.defend(target), "defence_failed")
        self.assertEqual(engine.state.skin, "wounded")

    def test_defence_rejects_wrong_or_unalerted_target(self) -> None:
        engine = self.make_engine()
        engine.report_attack(alert("flip"))

        with self.assertRaisesRegex(ValueError, "requires an attack alert"):
            engine.defend(device("other", DeviceClass.FLIPPER))
        with self.assertRaisesRegex(ValueError, "recognized defensive profile"):
            engine.defend(device("flip", DeviceClass.NANO))

    def test_clear_incident_returns_to_dormant(self) -> None:
        engine = self.make_engine()
        engine.report_attack(alert("flip"))

        engine.clear_incident()

        self.assertEqual(engine.state.mode.value, "dormant")
        self.assertEqual(engine.state.skin, "werewolf")
        with self.assertRaisesRegex(ValueError, "requires an attack alert"):
            engine.defend(device("flip", DeviceClass.FLIPPER))

    def test_event_log_is_bounded(self) -> None:
        engine = self.make_engine()

        for index in range(MAX_EVENT_LOG + 50):
            engine.report_attack(
                alert(
                    target=f"target-{index}",
                    alert_id=f"untrusted-{index}",
                    trusted=False,
                )
            )

        self.assertEqual(len(engine.state.event_log), MAX_EVENT_LOG)

    def test_alert_replay_tracking_is_bounded_and_current_alert_fails_closed(
        self,
    ) -> None:
        engine = self.make_engine()

        for index in range(MAX_ALERT_REPLAY_IDS + 100):
            current = alert(
                target=f"target-{index}",
                alert_id=f"alert-{index}",
            )
            self.assertTrue(engine.report_attack(current))

        self.assertLessEqual(len(engine._seen_alerts), MAX_ALERT_REPLAY_IDS)
        self.assertFalse(engine.report_attack(current))

    def test_resolved_alert_tracking_is_bounded_and_current_alert_fails_closed(
        self,
    ) -> None:
        engine = self.make_engine()

        for index in range(MAX_RESOLVED_ALERT_REPLAY_IDS + 100):
            target = device(f"target-{index}", DeviceClass.FLIPPER)
            self.assertTrue(
                engine.report_attack(
                    alert(target.device_id, alert_id=f"resolved-{index}")
                )
            )
            engine.defend(target)

        self.assertLessEqual(
            len(engine._resolved_alerts),
            MAX_RESOLVED_ALERT_REPLAY_IDS,
        )
        with self.assertRaisesRegex(ValueError, "already been resolved"):
            engine.defend(target)

    def test_deterministic_adversarial_sequence_preserves_invariants(self) -> None:
        rng = random.Random(2025)
        engine = self.make_engine()

        for index in range(2_000):
            operation = rng.randrange(5)
            if operation == 0:
                engine.report_attack(
                    alert(
                        target=f"target-{rng.randrange(8)}",
                        alert_id=f"alert-{index}",
                        trusted=bool(rng.randrange(2)),
                        severity=rng.randrange(0, 7),
                    )
                )
            elif operation == 1:
                engine.clear_incident()
            elif operation == 2:
                try:
                    engine.charge_shield(rng.randrange(-100, 200))
                except ValueError:
                    self.assertEqual(engine.state.mode.value, "dormant")
            elif operation == 3:
                source_class = rng.choice(list(DeviceClass))
                engine.scan(
                    [
                        device(
                            f"device-{index}",
                            source_class,
                            valid=bool(rng.randrange(2)),
                            issued_at=NOW + rng.randrange(-400, 100),
                            expires_at=NOW + rng.randrange(-100, 401),
                        )
                    ]
                )
            else:
                engine.scan([])

            self.assertGreaterEqual(engine.state.energy, 0)
            self.assertLessEqual(engine.state.energy, ENERGY_CAP)
            self.assertGreaterEqual(engine.state.shield, 0)
            self.assertLessEqual(engine.state.shield, SHIELD_CAP)
            self.assertLessEqual(len(engine.state.event_log), MAX_EVENT_LOG)


if __name__ == "__main__":
    unittest.main()
