import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from werewolf_game import __version__
from werewolf_game.application import InputError, load_scenario
from werewolf_game.cli import (
    EXIT_INPUT_ERROR,
    EXIT_SUCCESS,
    EXIT_WRITE_ERROR,
    main,
)
from werewolf_game.config import AppConfig


class ApplicationTests(unittest.TestCase):
    def test_secure_configuration_rejects_remote_actions(self) -> None:
        with self.assertRaisesRegex(ValueError, "Remote actions are prohibited"):
            AppConfig(allow_remote_actions=True)

    def test_load_scenario_enforces_size_limit(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "large.json"
            path.write_text('{"devices":[]}', encoding="utf-8")
            with self.assertRaisesRegex(InputError, "byte limit"):
                load_scenario(path, AppConfig(max_scenario_bytes=2))

    def test_check_reports_capabilities_and_limitations(self) -> None:
        with patch("sys.stdout", new_callable=io.StringIO) as output:
            exit_code = main(["check"])

        report = json.loads(output.getvalue())
        self.assertEqual(exit_code, EXIT_SUCCESS)
        self.assertEqual(report["version"], __version__)
        self.assertTrue(report["dry_run"])
        self.assertFalse(report["remote_actions"])
        self.assertIn("no_hardware_integration", report["limitations"])

    def test_invalid_json_is_clean_input_error_without_traceback(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text("{", encoding="utf-8")
            with patch("sys.stderr", new_callable=io.StringIO) as error:
                exit_code = main(["run", str(path)])

        self.assertEqual(exit_code, EXIT_INPUT_ERROR)
        self.assertTrue(error.getvalue().startswith("error: Invalid scenario:"))
        self.assertNotIn("Traceback", error.getvalue())

    def test_report_writes_state(self) -> None:
        with TemporaryDirectory() as directory:
            output_path = Path(directory) / "report.json"
            with patch("sys.stdout", new_callable=io.StringIO):
                exit_code = main(
                    [
                        "report",
                        "examples/werewolf-hunt.json",
                        "--output",
                        str(output_path),
                    ]
                )

            state = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, EXIT_SUCCESS)
        self.assertEqual(state["mode"], "guard")
        self.assertEqual(state["skin"], "secured")

    def test_report_write_failure_has_distinct_exit_code(self) -> None:
        with TemporaryDirectory() as directory:
            directory_path = Path(directory)
            with patch("sys.stderr", new_callable=io.StringIO) as error:
                exit_code = main(
                    [
                        "report",
                        "examples/werewolf-hunt.json",
                        "--output",
                        str(directory_path),
                    ]
                )

        self.assertEqual(exit_code, EXIT_WRITE_ERROR)
        self.assertIn("cannot write report", error.getvalue())


if __name__ == "__main__":
    unittest.main()
