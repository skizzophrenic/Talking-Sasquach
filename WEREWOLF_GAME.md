# Werewolf Proximity Game Prototype

This prototype models a defensive layer that protects people during opt-in hack-game play. It does **not** initiate contact because a device is nearby, retaliate, exploit devices, modify firmware, or damage eMMC storage. The werewolf remains dormant until the host firmware reports an attack.

## Non-negotiable core principles

These requirements are part of the product contract and must survive every refactor:

1. **Defence without retaliation:** eliminate unauthorized access paths, never people or remote hardware.
2. **Evidence before action:** proximity, names, addresses, intuition, and a single untrusted signal cannot activate guard mode. A trusted host detector must provide a unique alert, reason, severity, and target.
3. **Immediate, proportionate containment:** verified incidents may fail closed, isolate the affected local session, revoke local credentials, preserve evidence, and alert the owner.
4. **Continuity for legitimate users:** containment stays scoped to the affected session or interface; redundancy and recovery should prevent visible disruption.
5. **Consent and privacy:** reinforcement requires an authenticated, unexpired, single-use opt-in beacon. No payload capture, stable identity retention, or inference of consent.
6. **Open and verifiable engine:** state transitions, algorithms, metrics, interfaces, tests, and limitations remain inspectable and reproducible.
7. **Protected security implementation:** deployment secrets, live detection signatures, threat intelligence, credentials, and anti-tamper details may remain proprietary, but security must not depend on obscurity.
8. **Standard cryptography:** use reviewed authenticated encryption, hardware-backed keys, short-lived authorization, replay protection, and threshold controls rather than custom ciphers or character transformations.
9. **Bounded AI authority:** assistants explain recommendations and cite state; they cannot retrieve core secrets, authorize themselves, change policy, or perform destructive actions.
10. **Fail closed and recover cleanly:** invalid input is rejected explicitly, failures are visible, logs are bounded, changes are reversible, and known-good recovery remains available.
11. **Auditability:** security-relevant events use structured records suitable for signed, timestamped, access-controlled audit storage and documented chain of custody.
12. **Quality without shortcuts:** measurable invariants, adversarial testing, failure injection, independent review, transparent limitations, and continuous improvement define completion.

## Game loop

- **Dormant:** nearby devices alone do nothing; the default werewolf skin quietly watches host security signals.
- **Guard mode:** an attack alert associated with a Flipper, Pwnagotchi, Bjorn, or Tamafi profile triggers the `full_moon` skin.
- **Power reinforcement:** during an active incident only, opted-in Pineapple, Phones64, WiFi7, Nano, and Sharkbite game beacons grant simulated defensive energy.
- **Defence:** energy can be banked in a shield before battle.
- **Attack response:** first-connect timing affects threat level. The layer blocks and isolates the game session, preserves an event record, and alerts the owner; it never attacks the other device.
- **Skins:** `werewolf`, `full_moon`, `shielded`, `secured`, and `wounded` expose each defensive state for future 128x64 animation packs.
- **Assistants:** an entirely local rules-based suite provides Guardian response advice, Privacy Sentinel consent/authenticity warnings, and Update Guide status. The prototype does not claim that these deterministic rules are an ML model.

## Full metrics

The JSON report contains scan counts, devices seen, accepted and ignored devices, detections by class, attacks detected, guard-mode entries, collected energy, defence actions, blocked attacks, defence failures, shield uses, protected sessions, score, streak, current mode and skin, guidance from all three assistants, and a structured event log.

Run the included scenario with Python 3.10 or newer:

```powershell
python -m werewolf_game .\examples\werewolf-hunt.json --report .\werewolf-report.json
```

Run the tests:

```powershell
python -m unittest discover -s .\tests -v
```

## Firmware integration contract

A future firmware implementation should replace scenario JSON with a scanner that emits only privacy-preserving game records:

```json
{
  "device_id": "rotating-game-id",
  "device_class": "flipper",
  "signal_dbm": -43,
  "opted_in": true,
  "game_beacon_valid": true,
  "battle_power": 70,
  "connected_first": false,
  "beacon_id": "single-use-random-id",
  "issued_at": 1000,
  "expires_at": 1120
}
```

Attack state comes from a separate `AttackAlert`, never from a nearby device record:

```json
{
  "alert_id": "unique-host-alert",
  "detector": "session-integrity-monitor",
  "target_device_id": "rotating-game-id",
  "reason": "unauthorized protected-route access",
  "severity": 4,
  "trusted": true
}
```

Only the host integration may set `trusted` after authenticating the detector. Use rotating identifiers, authenticated game beacons, replay protection, rate limits, an obvious off switch, and no passive identity retention. Never derive participation from an ordinary SSID, Bluetooth name, MAC address, or unrelated network traffic. Defensive integration may deny or terminate the local session, but must never send destructive commands to another device.

## Hard-testing standard

The suite exercises trust-boundary separation, invalid alerts, duplicate alerts, expired/future/overlong beacons, replayed reinforcement, inactive-incident behavior, single-resolution alerts, target binding, first-connect disadvantage, bounded logs, recovery to dormant state, and 2,000 deterministic adversarial state transitions. Production integration must add authenticated-detector tests, cryptographic test vectors, rate-limit/load tests, power-loss and rollback injection, storage exhaustion, malformed transport fuzzing, concurrency tests, hardware-in-the-loop tests, and independent security review.

In-memory beacon replay entries expire with their validated beacon lifetime. Alert and resolved-alert replay stores retain the newest 1,024 IDs while always preserving the active alert; production deployments that require a longer replay window should replace these stores with bounded persistent storage and an explicit retention policy.

Run the reproducible quality gate and produce machine-readable evidence:

```powershell
python .\tools\quality_gate.py --output .\quality-report.json
```
