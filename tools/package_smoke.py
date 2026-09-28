from __future__ import annotations

import json
import os
import subprocess
import sys
import tarfile
import tempfile
import venv
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="werewolf-package-") as directory:
        workspace = Path(directory)
        dist = workspace / "dist"
        build = run(
            [
                sys.executable,
                "-m",
                "build",
                "--no-isolation",
                "--outdir",
                str(dist),
                str(ROOT),
            ],
            ROOT,
        )
        artifacts = sorted(path.name for path in dist.glob("*"))
        if build.returncode != 0:
            print(
                json.dumps(
                    {
                        "passed": False,
                        "stage": "build",
                        "stderr": build.stderr,
                    },
                    indent=2,
                )
            )
            return 1

        wheel = next(dist.glob("*.whl"), None)
        source = next(dist.glob("*.tar.gz"), None)
        if wheel is None or source is None:
            print(
                json.dumps(
                    {
                        "passed": False,
                        "stage": "artifacts",
                        "artifacts": artifacts,
                    },
                    indent=2,
                )
            )
            return 1

        with zipfile.ZipFile(wheel) as archive:
            wheel_members = archive.namelist()
        with tarfile.open(source, mode="r:gz") as archive:
            source_members = archive.getnames()
        prohibited_suffixes = (".bin", ".img", ".bm", ".png", ".gif", ".mp4")
        prohibited_parts = (
            "Finished Animations",
            "Working But Not Finished Animations",
            "Single File WiFi Board Bins",
            "One File Linux",
        )
        undeclared = [
            member
            for member in [*wheel_members, *source_members]
            if member.endswith(prohibited_suffixes)
            or any(part in member for part in prohibited_parts)
        ]
        if undeclared:
            print(
                json.dumps(
                    {
                        "passed": False,
                        "stage": "artifact_contents",
                        "undeclared": undeclared,
                    },
                    indent=2,
                )
            )
            return 1

        environment = workspace / "venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(environment)
        scripts = environment / ("Scripts" if os.name == "nt" else "bin")
        python = scripts / ("python.exe" if os.name == "nt" else "python")
        executable = scripts / ("werewolf.exe" if os.name == "nt" else "werewolf")

        install = run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--no-deps",
                str(wheel),
            ],
            workspace,
        )
        check = run([str(executable), "check"], workspace)
        version = run([str(executable), "--version"], workspace)
        uninstall = run(
            [
                str(python),
                "-m",
                "pip",
                "uninstall",
                "-y",
                "talking-sasquach-werewolf",
            ],
            workspace,
        )
        passed = all(
            result.returncode == 0
            for result in (install, check, version, uninstall)
        )
        report: dict[str, Any] = {
            "passed": passed,
            "artifacts": artifacts,
            "undeclared_assets": undeclared,
            "installed_check": (
                json.loads(check.stdout) if check.returncode == 0 else None
            ),
            "version": version.stdout.strip(),
            "install_return_code": install.returncode,
            "check_return_code": check.returncode,
            "uninstall_return_code": uninstall.returncode,
        }
        if not passed:
            report["errors"] = {
                "install": install.stderr,
                "check": check.stderr,
                "version": version.stderr,
                "uninstall": uninstall.stderr,
            }
        print(json.dumps(report, indent=2))
        return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
