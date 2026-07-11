#!/usr/bin/env python3
"""Restart a Claude Code session in the current macOS Terminal tab."""

from __future__ import annotations

import argparse
import math
import os
import shlex
import shutil
import subprocess
import sys
import uuid

DEFAULT_MESSAGE = "Restart successful. Please continue where we left off."

APPLESCRIPT = r'''
on run argv
    set resumeCommand to item 1 of argv
    set continuationMessage to item 2 of argv
    set targetTTY to item 3 of argv
    set shellDelay to (item 4 of argv) as real
    set startupDelay to (item 5 of argv) as real

    set targetWindow to missing value
    set targetTab to missing value

    tell application "Terminal"
        repeat with terminalWindow in windows
            repeat with terminalTab in tabs of terminalWindow
                if (tty of terminalTab as text) is targetTTY then
                    set targetWindow to terminalWindow
                    set targetTab to terminalTab
                    exit repeat
                end if
            end repeat
            if targetTab is not missing value then exit repeat
        end repeat

        if targetTab is missing value then error "Could not find the originating Terminal tab."
        set selected tab of targetWindow to targetTab
        set index of targetWindow to 1
        activate
    end tell

    delay 0.2

    tell application "System Events"
        if UI elements enabled is false then error "Accessibility access is not enabled."
        tell process "Terminal"
            keystroke "c" using control down
            delay 0.3
            keystroke "c" using control down
            delay shellDelay
            keystroke resumeCommand
            delay 0.5
            key code 36
            delay startupDelay
            if continuationMessage is not "" then
                keystroke continuationMessage
                delay 1
                key code 36
            end if
        end tell
    end tell
end run
'''


def non_negative_float(value: str) -> float:
    """Parse a non-negative command-line delay."""
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise argparse.ArgumentTypeError("delay must be a finite number zero or greater")
    return number


def session_uuid(value: str) -> str:
    """Validate and normalize a Claude session UUID."""
    try:
        return str(uuid.UUID(value))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("session ID must be a UUID") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Restart Claude Code in the originating macOS Terminal tab."
    )
    parser.add_argument(
        "--session-id",
        type=session_uuid,
        help="resume this exact session UUID instead of the most recent session in the current directory",
    )
    parser.add_argument(
        "--dangerously-skip-permissions",
        action="store_true",
        help="opt in to Claude Code's permission-bypass mode",
    )
    parser.add_argument(
        "--shell-delay",
        type=non_negative_float,
        default=4.0,
        help="seconds to wait for the shell after Ctrl+C (default: 4)",
    )
    parser.add_argument(
        "--startup-delay",
        type=non_negative_float,
        default=12.0,
        help="seconds to wait for Claude Code to start (default: 12)",
    )
    message_group = parser.add_mutually_exclusive_group()
    message_group.add_argument(
        "--message",
        default=DEFAULT_MESSAGE,
        help="message to submit after Claude Code restarts",
    )
    message_group.add_argument(
        "--no-message",
        action="store_true",
        help="restart without submitting a continuation message",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show the restart command and timing without sending keystrokes",
    )
    return parser


def build_resume_command(
    session_id: str | None, dangerously_skip_permissions: bool
) -> str:
    """Build a shell-safe Claude Code resume command."""
    command = ["claude"]
    if dangerously_skip_permissions:
        command.append("--dangerously-skip-permissions")
    if session_id:
        command.extend(["--resume", session_id])
    else:
        command.append("--continue")
    return shlex.join(command)


def controlling_tty() -> str:
    """Return the controlling TTY even when standard input is captured."""
    try:
        descriptor = os.open("/dev/tty", os.O_RDONLY)
    except OSError as exc:
        raise RuntimeError("No controlling terminal was found.") from exc
    try:
        return os.ttyname(descriptor)
    finally:
        os.close(descriptor)


def check_environment() -> None:
    """Fail before sending keystrokes when the supported environment is absent."""
    if sys.platform != "darwin":
        raise RuntimeError("This utility supports macOS only.")
    if os.environ.get("TERM_PROGRAM") != "Apple_Terminal":
        raise RuntimeError("Run this utility from Terminal.app.")
    for executable in ("claude", "osascript"):
        if shutil.which(executable) is None:
            raise RuntimeError(f"Required executable not found: {executable}")

    result = subprocess.run(
        [
            "osascript",
            "-e",
            'tell application "System Events" to get UI elements enabled',
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or result.stdout.strip().lower() != "true":
        raise RuntimeError(
            "Terminal needs Accessibility access in System Settings > "
            "Privacy & Security > Accessibility."
        )


def schedule_restart(
    command: str,
    message: str,
    tty: str,
    shell_delay: float,
    startup_delay: float,
) -> None:
    """Launch the detached AppleScript that survives the current Claude process."""
    subprocess.Popen(
        [
            "osascript",
            "-e",
            APPLESCRIPT,
            command,
            message,
            tty,
            str(shell_delay),
            str(startup_delay),
        ],
        start_new_session=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    message = "" if args.no_message else args.message
    command = build_resume_command(
        args.session_id, args.dangerously_skip_permissions
    )

    if args.dry_run:
        print(f"Command: {command}")
        print(f"Shell delay: {args.shell_delay:g}s")
        print(f"Startup delay: {args.startup_delay:g}s")
        print(f"Continuation message: {message or '(disabled)'}")
        return 0

    try:
        check_environment()
        tty = controlling_tty()
    except RuntimeError as exc:
        print(f"restart-claude: {exc}", file=sys.stderr)
        return 1

    schedule_restart(command, message, tty, args.shell_delay, args.startup_delay)
    print(f"Restart scheduled in {tty}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
