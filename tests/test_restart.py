from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "restart-claude" / "restart.py"
SPEC = importlib.util.spec_from_file_location("restart_claude", SCRIPT)
assert SPEC and SPEC.loader
restart_claude = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(restart_claude)


class RestartClaudeTests(unittest.TestCase):
    def test_default_command_continues_without_bypassing_permissions(self) -> None:
        command = restart_claude.build_resume_command(None, False)
        self.assertEqual(command, "claude --continue")

    def test_exact_session_and_permission_bypass_are_explicit(self) -> None:
        session_id = "123e4567-e89b-12d3-a456-426614174000"
        command = restart_claude.build_resume_command(session_id, True)
        self.assertEqual(
            command,
            "claude --dangerously-skip-permissions --resume " + session_id,
        )

    def test_session_id_must_be_a_uuid(self) -> None:
        parser = restart_claude.build_parser()
        with (
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit),
        ):
            parser.parse_args(["--session-id", "not-a-session-id"])

    def test_apple_script_receives_values_as_arguments(self) -> None:
        command = "claude --continue"
        message = 'Continue with "quoted" text.'
        with mock.patch.object(restart_claude.subprocess, "Popen") as popen:
            restart_claude.schedule_restart(command, message, "/dev/ttys001", 4, 12)

        argv = popen.call_args.args[0]
        self.assertEqual(argv[0:2], ["osascript", "-e"])
        self.assertEqual(argv[3:8], [command, message, "/dev/ttys001", "4", "12"])
        self.assertNotIn(command, restart_claude.APPLESCRIPT)
        self.assertNotIn(message, restart_claude.APPLESCRIPT)
        self.assertTrue(popen.call_args.kwargs["start_new_session"])

    def test_dry_run_does_not_check_environment_or_launch(self) -> None:
        output = io.StringIO()
        with (
            mock.patch.object(restart_claude, "check_environment") as environment,
            mock.patch.object(restart_claude, "schedule_restart") as schedule,
            contextlib.redirect_stdout(output),
        ):
            result = restart_claude.main(["--dry-run", "--no-message"])

        self.assertEqual(result, 0)
        self.assertIn("claude --continue", output.getvalue())
        self.assertIn("(disabled)", output.getvalue())
        environment.assert_not_called()
        schedule.assert_not_called()

    def test_negative_delay_is_rejected(self) -> None:
        parser = restart_claude.build_parser()
        with (
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit),
        ):
            parser.parse_args(["--startup-delay", "-1"])

    def test_non_finite_delay_is_rejected(self) -> None:
        parser = restart_claude.build_parser()
        with (
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit),
        ):
            parser.parse_args(["--startup-delay", "nan"])


if __name__ == "__main__":
    unittest.main()
