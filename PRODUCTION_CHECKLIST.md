# Desktop Python Application Production Checklist

This document is the source of truth for turning the Werewolf reference
prototype into an externally testable desktop Python application.

## Straight status

The current code is a working **reference prototype**, not a complete desktop
product. On 2026-09-28 the Gate 2 quality run compiled the package, passed all
27 tests, completed the reference scenario, built wheel and source artifacts,
installed the wheel in a clean environment, executed the installed command,
and uninstalled it. That verifies the implemented Python behavior and
packaging only. It does not verify real hardware integration, production
cryptography, operating-system containment, or a graphical interface.

## Completion rule

An item may be checked only when all applicable evidence exists:

- implementation is present and reviewed;
- a minimal public code example runs outside the test suite;
- positive, boundary, and failure-path tests pass;
- the machine-readable quality gate includes the module;
- expected inputs, outputs, errors, and limitations are documented;
- a clean environment can reproduce the result using documented commands;
- security-sensitive behavior fails closed and has a rollback path.

Code that merely imports, compiles, is mocked without testing the contract, or
has no reproducible evidence remains incomplete.

## Evidence commands

Create an isolated environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
```

Run the current reference application:

```powershell
.\.venv\Scripts\python -m werewolf_game .\examples\werewolf-hunt.json
```

Run the complete current quality gate:

```powershell
.\.venv\Scripts\python .\tools\quality_gate.py --output .\quality-report.json
```

The command must exit with code `0` and the report must contain
`"passed": true`. Generated reports are test evidence, not source files, and
should not be committed.

## Phase 0: verified baseline

- [x] Separate trusted host alerts from nearby-device observations.
- [x] Keep proximity-only scenarios dormant.
- [x] Require actual JSON booleans at security and consent boundaries.
- [x] Reject invalid, future, expired, overlong, and replayed beacons.
- [x] Bound beacon, alert, resolved-alert, and event-log memory.
- [x] Bind a defence action to its trusted alert and target.
- [x] Prevent one alert from being resolved repeatedly.
- [x] Enforce energy, shield, mode, and skin invariants.
- [x] Provide structured metrics and deterministic local guidance.
- [x] Exercise 2,000 deterministic adversarial state transitions.
- [x] Provide one end-to-end JSON scenario.
- [x] Produce a machine-readable quality report.
- [ ] Tag a baseline release after this checklist is reviewed.

## Phase 1: product contract and repository standards

- [ ] Freeze the desktop MVP scope and explicitly list excluded functionality.
- [ ] Define supported Python and Windows versions.
- [ ] Define latency, memory, retention, availability, and startup targets.
- [ ] Define the threat model, trust boundaries, assets, actors, and abuse cases.
- [ ] Define privacy collection, retention, export, and erase requirements.
- [ ] Define accessibility and text fallback requirements for every skin/state.
- [ ] Add a contribution guide and coding/testing conventions.
- [ ] Add change-log and semantic-versioning policies.
- [ ] Add a requirement-to-test traceability table.
- [ ] Review and sign off the contract before expanding implementation.

**Gate:** every requested feature maps to a measurable acceptance criterion and
at least one planned verification method.

## Phase 2: installable application package

- [x] Add `pyproject.toml` with package metadata and supported Python version.
- [x] Add a versioned `werewolf` console entry point.
- [x] Separate domain, application, configuration, and presentation modules.
- [x] Add typed configuration with secure defaults.
- [x] Add `--version`, `--help`, `check`, `run`, and `report` commands.
- [x] Return documented process exit codes for success and each failure class.
- [x] Prevent stack traces for expected user-input failures.
- [x] Add clean-environment installation and uninstall tests.
- [x] Build wheel and source artifacts without undeclared assets.
- [x] Add an offline, isolated smoke test for installed artifacts.

**Gate:** a tester can create a clean virtual environment, install the wheel,
run `werewolf check`, execute the example, and uninstall it using only the
release instructions.

**Verified environment:** Windows with Python 3.14.6. The package declares
Python 3.10+, but the remaining Python/OS matrix is a research directive and
must not be described as verified yet.

**Exit codes:** `0` success, `2` expected input/contract error, `3` report-write
failure. Argument parser usage failures also use `2`.

## Phase 3: versioned input and configuration contracts

- [ ] Publish a versioned JSON Schema for scenarios, alerts, and beacons.
- [ ] Reject unknown schema versions.
- [ ] Reject unknown security-critical fields unless explicitly allowed.
- [ ] Validate numeric ranges before constructing domain objects.
- [ ] Define UTC/monotonic-clock handling and clock-skew limits.
- [ ] Define duplicate device and duplicate alert behavior.
- [ ] Add valid, invalid, boundary, and migration fixtures.
- [ ] Add parser fuzzing and oversized-input limits.
- [ ] Emit field-specific errors without leaking secrets.
- [ ] Add schema compatibility tests to the quality gate.

**Gate:** every accepted document validates against the published schema, and
every malformed fixture fails with the documented error and nonzero exit code.

## Phase 4: authenticated detector and beacon interfaces

- [ ] Replace caller-provided `trusted` state with a verifier result.
- [ ] Define a detector adapter interface with explicit authentication failure.
- [ ] Define a beacon verifier interface with expiry and replay metadata.
- [ ] Use reviewed standard cryptography; do not invent a cipher.
- [ ] Keep signing/private keys outside application configuration and logs.
- [ ] Bind signatures to schema version, issuer, target, nonce, and expiry.
- [ ] Add key rotation, revocation, and unknown-key behavior.
- [ ] Add published cryptographic test vectors.
- [ ] Add tampering, wrong-key, replay, expiry, and clock-skew tests.
- [ ] Keep a deterministic fake verifier for safe external testing.

**Gate:** raw input cannot mark itself trusted; only a configured verifier can
produce an authenticated domain alert or beacon.

## Phase 5: safe desktop containment adapters

- [ ] Define a capability-limited containment interface.
- [ ] Implement a default dry-run adapter that changes no system state.
- [ ] Implement a sandbox adapter using resources owned by the test process.
- [ ] Require explicit authorization before any real local policy change.
- [ ] Scope actions to the alerted local session or owned test interface.
- [ ] Prohibit outbound retaliation and remote-system modification.
- [ ] Record requested, authorized, completed, rolled-back, and failed actions.
- [ ] Make every applied local change idempotent and reversible.
- [ ] Add partial-failure and rollback tests.
- [ ] Add platform-specific integration tests in isolated test environments.

**Gate:** the dry-run and sandbox adapters prove the full workflow without
requiring administrator privileges or touching another device.

## Phase 6: durable audit and state storage

- [ ] Define versioned state and audit schemas.
- [ ] Use bounded durable storage with configured retention limits.
- [ ] Add integrity hashes or signatures to exported audit records.
- [ ] Redact credentials, payloads, and stable unnecessary identifiers.
- [ ] Handle duplicate, corrupt, truncated, and future-version records.
- [ ] Make writes atomic and recover from interrupted writes.
- [ ] Add storage-full and permission-denied behavior.
- [ ] Add export, verification, retention, and erase commands.
- [ ] Document chain-of-custody procedures and their limitations.
- [ ] Add restart/recovery and migration tests.

**Gate:** an interrupted process restarts without inventing state, losing a
confirmed record, or silently accepting corrupted evidence.

## Phase 7: desktop user interface

- [ ] Select and document a maintained Python desktop UI framework.
- [ ] Display dormant, guard, defence, secured, and wounded states.
- [ ] Provide text/icon equivalents for every animation and color.
- [ ] Display the evidence and rule behind every assistant recommendation.
- [ ] Display current metrics, limits, retention, and verifier status.
- [ ] Add clear incident acknowledgement and recovery controls.
- [ ] Add explicit confirmation for policy or containment changes.
- [ ] Keep the UI responsive during scanning, verification, and export.
- [ ] Add keyboard navigation, scaling, contrast, and screen-reader labels.
- [ ] Add view-model tests and automated UI smoke tests.

**Gate:** a tester can complete the reference incident and recovery workflow
without the terminal, while all states remain understandable with animations
disabled.

## Phase 8: observability and operational reliability

- [ ] Add structured application logs with correlation IDs.
- [ ] Separate operational logs from protected audit evidence.
- [ ] Add health, readiness, storage, verifier, and adapter status.
- [ ] Add configurable metrics export with privacy-safe defaults.
- [ ] Define warning/error messages and operator remediation.
- [ ] Add bounded queues and backpressure.
- [ ] Add safe cancellation and shutdown.
- [ ] Add startup recovery and stale-lock handling.
- [ ] Add fault injection for clocks, storage, adapters, and verifiers.
- [ ] Add automated backup and restore verification where state requires it.

**Gate:** every injected dependency failure produces a documented state,
actionable error, bounded resource use, and safe recovery.

## Phase 9: hard testing

- [ ] Expand unit tests to full branch coverage of security decisions.
- [ ] Add property-based tests for all state-machine invariants.
- [ ] Add coverage-guided fuzzing for JSON and persisted records.
- [ ] Add concurrency and race-condition tests.
- [ ] Add memory and file-descriptor leak tests.
- [ ] Add sustained-load and 24-hour soak tests.
- [ ] Add startup, processing, and shutdown performance budgets.
- [ ] Add dependency and static-analysis checks.
- [ ] Add secret scanning and software-composition analysis.
- [ ] Commission an independent security review and resolve findings.

**Gate:** no unresolved critical/high defects, no unexplained resource growth,
and every published performance/security claim links to reproducible evidence.

## Phase 10: release engineering and external verification

- [ ] Pin and review runtime/build dependencies.
- [ ] Generate an SBOM.
- [ ] Produce reproducible wheel and desktop artifacts.
- [ ] Sign release artifacts and publish checksums.
- [ ] Run clean-machine installation tests.
- [ ] Run upgrade, rollback, and uninstall tests.
- [ ] Publish known limitations and unsupported scenarios.
- [ ] Publish a release evidence bundle with quality-report results.
- [ ] Provide a minimal external tester guide and issue template.
- [ ] Require release approval against this checklist.

**Gate:** an external tester can verify artifact identity, install without the
source tree, reproduce the documented workflows, obtain the expected outputs,
and report a failure with enough diagnostic evidence to investigate it.

## Required public code samples

Each completed module must provide a small executable sample. The current
engine sample is:

```python
from werewolf_game import AttackAlert, GameEngine

engine = GameEngine(clock=lambda: 1_000)
accepted = engine.report_attack(
    AttackAlert(
        alert_id="external-test-1",
        detector="test-detector",
        target_device_id="test-target",
        reason="authorized external test",
        severity=3,
        trusted=True,
    )
)

assert accepted
assert engine.state.mode.value == "guard"
print(engine.state.to_dict())
```

This demonstrates the current domain contract only. Phase 4 must replace direct
construction of `trusted=True` with an authenticated verifier before the
application can make a production security claim.

## Release decision

Current decision: **prototype verified, production release blocked**.

Release remains blocked until Phases 1-10 pass their gates. Any unchecked item
must be reported as incomplete rather than implied, simulated, or described as
working production functionality.
