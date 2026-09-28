# External Research and Source Directives

Use these packets with other AI models or human researchers. Each directive is
independent so results can be compared instead of allowing one assumption to
propagate through every report.

## Required submission format

Save each result under `research/inbox/` using the suggested filename. Every
claim must include:

```text
Claim:
Status: verified | contradicted | unknown
Primary source:
Source version/date:
Exact evidence:
Reproduction steps:
Observed output:
Compatibility impact:
Security impact:
Licensing impact:
Confidence: high | medium | low
Open questions:
```

Do not paste secrets, credentials, personal data, copyrighted source not
licensed for redistribution, or instructions for attacking third-party
systems. A model must label inference as inference and must not edit production
code based only on an unverified claim.

## Directive 01: firmware binary provenance

**Suggested output:** `research/inbox/01-firmware-provenance.md`

```text
Audit every .bin under "Single File WiFi Board Bins". Find the authoritative
source repository, exact commit/tag, build configuration, ESP-IDF/Arduino
toolchain version, partition table, flash offsets, board definition, license,
and published checksum for each artifact. Prefer primary repository releases
and build files. Do not infer compatibility from filenames. Return one evidence
record per binary and mark anything not independently reproducible unknown.
```

## Directive 02: ESP hardware matrix

**Suggested output:** `research/inbox/02-esp-hardware-matrix.md`

```text
Build an evidence-based matrix for ESP32 WROOM, WROVER, S2, S3, and boards sold
as Flipper Zero WiFi development boards. Record exact chip, flash size, PSRAM,
USB/UART method, boot pins, voltage, partition constraints, and safe flashing
requirements. Map repository binaries only where primary evidence proves a
match. Flag ambiguous marketing names and hardware revisions.
```

## Directive 03: dual-boot architecture

**Suggested output:** `research/inbox/03-dual-boot-layout.md`

```text
Research the exact dual-boot mechanism expected by the repository binaries.
Identify bootloader source, partition selection, recovery path, supported image
sizes, update procedure, rollback behavior, and failure modes. Require primary
source code or maintainer documentation. Produce a non-destructive validation
plan using owned test hardware; do not recommend flashing an unverified image.
```

## Directive 04: Marauder compatibility

**Suggested output:** `research/inbox/04-marauder-compatibility.md`

```text
Identify the Marauder project/release represented by each repository artifact.
Compare supported boards, display/GPS features, partition tables, configuration
migrations, and known incompatibilities. Cite exact releases and source
commits. Produce build and validation steps that can generate matching hashes,
or explain precisely why matching is impossible.
```

## Directive 05: Flipper GUI patch compatibility

**Suggested output:** `research/inbox/05-flipper-gui-compatibility.md`

```text
Compare every "Battery Only Top Status Bar" gui.c file against official Flipper
firmware and relevant custom firmware histories. Locate the closest source
commit, identify changed symbols and APIs, determine compatible version ranges,
and prepare a minimal patch rather than a whole-file replacement. Include build
and emulator/device validation steps and applicable licenses.
```

## Directive 06: animation pipeline

**Suggested output:** `research/inbox/06-animation-pipeline.md`

```text
Research the authoritative Flipper animation meta.txt and .bm formats. Verify
field semantics, frame encoding, limits, active/passive behavior, bubble slots,
and firmware-version differences. Identify maintained conversion tools and
licenses. Propose a reproducible PNG-to-BM pipeline with fixed tool versions,
manifest fields, checksums, and automated metadata/frame consistency checks.
```

## Directive 07: asset provenance and licensing

**Suggested output:** `research/inbox/07-asset-provenance.md`

```text
Inventory all PNG, GIF, MP4, ZIP, BM, BIN, IMG, and C assets. Determine which
files are original source, derived output, previews, or release artifacts.
Record creator/provenance and redistribution license using primary evidence.
Do not assume repository presence grants redistribution rights. Flag assets
that cannot be safely included in packaged releases.
```

## Directive 08: One File Linux image

**Suggested output:** `research/inbox/08-linux-image.md`

```text
Determine the intended target hardware and build provenance of
"One File Linux/OneFileLinux.img". Identify partition/filesystem layout, kernel,
initramfs, userspace, architecture, boot process, license obligations, default
credentials, network services, SBOM, and reproducible build recipe. Perform
only offline read-only inspection unless explicit authorization and an isolated
test environment are available.
```

## Directive 09: desktop platform validation

**Suggested output:** `research/inbox/09-python-platform-matrix.md`

```text
Run the Python package quality gate and package smoke test on supported Python
versions 3.10 through 3.14 across Windows, Linux, and macOS where available.
Record OS version, architecture, Python source/version, commands, exit codes,
artifact hashes, durations, failures, and logs. Do not mark a platform verified
without actual execution.
```

## Directive 10: defensive threat model review

**Suggested output:** `research/inbox/10-threat-model.md`

```text
Review the desktop reference using STRIDE or an equivalent documented method.
Focus on authenticated alert ingestion, beacon replay, clock manipulation,
resource exhaustion, unsafe adapters, audit integrity, update supply chain, and
assistant authority. Separate current prototype risks from future hardware
risks. Recommend defensive mitigations and tests only; exclude retaliation or
remote destructive behavior.
```

## Integration rule

Research findings enter code decisions only after:

1. primary sources are accessible and versioned;
2. reproduction steps succeed or limitations are explicit;
3. licensing and security impacts are reviewed;
4. conflicting findings are resolved or recorded;
5. the accepted claim is linked to a requirement and test.

