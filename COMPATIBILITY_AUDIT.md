# Capability, Asset, and Hardware Compatibility Audit

## Verification labels

- **Verified:** reproduced by an automated command in the current environment.
- **Supported by design:** covered by a documented interface but not reproduced
  on every target.
- **Unverified:** evidence, source, hardware, or reproducible instructions are
  missing.
- **Out of scope:** deliberately excluded from the desktop Gate 2 package.

No narrative claim is treated as compatibility evidence.

## Desktop application capability matrix

| Capability | Status | Evidence or limitation |
|---|---|---|
| Python source compilation | Verified | `tools/quality_gate.py` |
| Domain/state engine | Verified | Unit and adversarial tests |
| JSON scenario execution | Verified | `examples/werewolf-hunt.json` |
| Clean expected-input errors | Verified | CLI tests; no traceback |
| Console `check`, `run`, `report` | Verified | Source and installed-command tests |
| Wheel and source distribution | Verified | `tools/package_smoke.py` |
| Clean virtual-environment install | Verified | Built wheel installed outside source tree |
| Installed console entry point | Verified | `werewolf check` and `werewolf --version` |
| Uninstall | Verified | Clean-environment smoke test |
| Python 3.14.6 on Windows | Verified | Gate 2 development environment |
| Python 3.10-3.13 | Supported by design | Declared, but CI matrix is not yet present |
| Linux/macOS | Supported by design | Pure Python, but not yet executed there |
| Production alert authentication | Unverified | Gate 4; current trusted alert is a test contract |
| OS/network containment | Out of scope | Gate 5; current package is dry-run only |
| Durable audit storage | Out of scope | Gate 6 |
| Graphical desktop interface | Out of scope | Gate 7 |
| AI/ML model | Out of scope | Current assistants are deterministic local rules |

## Repository asset matrix

| Asset class | Observed format/target | Compatibility status | Weakness |
|---|---|---|---|
| Finished animations | `.bm` plus `meta.txt`, 128x64 | Partially evidenced | No reproducible conversion tool/version or canonical source mapping |
| Animation source/previews | `.png`, `.gif`, `.mp4`, `.zip` | Unverified | Mixed source/derived assets with no manifest or checksums |
| Status-bar modifications | `gui.c`, Flipper firmware tree | Unverified | No exact upstream commit, patch, build log, or supported firmware range |
| Marauder images | WROOM, S3, Flipper/WROVER `.bin` | Unverified | No source commit, build recipe, board revision matrix, hash, or signature |
| Dual-boot images | ESP32 S3, Flipper/WROVER `.bin` | Unverified | Partition layout and bootloader compatibility are undocumented |
| Evil Portal images | WROOM, WiFi Board/S2 `.bin` | Unverified | Source and flash offsets are undocumented |
| One File Linux | `.img` | Unverified | No kernel/initramfs manifest, build recipe, target hardware, or checksum |

These assets are intentionally excluded from the Python distribution until
their provenance, license, target, and reproduction evidence are known.

## Pinpointed weaknesses

### Critical evidence gaps

1. Firmware binaries and the Linux image cannot be reproduced from this
   repository.
2. Board names do not identify exact modules, flash sizes, PSRAM, partition
   layouts, bootloaders, flash offsets, or minimum hardware revisions.
3. No checksums, signatures, release manifest, source commit, toolchain version,
   or build log accompanies binary artifacts.
4. A filename is currently the only mapping between firmware and hardware.

### High product gaps

1. The Python alert trust decision is still supplied by test input; it is not
   authenticated.
2. The package performs simulation only and has no operating-system
   containment capability.
3. Only Windows/Python 3.14.6 has been executed; the declared Python range and
   other desktop systems need CI evidence.
4. State and audit evidence are in memory only.
5. There is no graphical desktop interface.

### Asset pipeline gaps

1. Animation source-of-truth files are not identified.
2. Conversion/export tools and exact parameters are missing.
3. Metadata/frame consistency is not checked automatically.
4. Archives may duplicate extracted content without a canonical relationship.
5. Narrative device-performance claims do not include versioned evidence.

## Gate 2 alignment decision

The Python package is compatible with its verified desktop simulation scope.
It makes no hardware compatibility claim and ships none of the unverified
binary, image, animation, or GUI-patch assets. Hardware integration stays
blocked until the research directives produce reproducible evidence.

