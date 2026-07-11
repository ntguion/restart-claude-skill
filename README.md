# Restart Claude Code Skill

A small macOS utility that restarts Claude Code in the same Terminal.app tab. It is useful after changing MCP server configuration or other settings that are loaded at startup.

The script automates the same sequence a user would perform manually: interrupt Claude Code, return to the shell, run `claude --continue`, wait for startup, and submit a continuation message.

## Supported environment

- macOS
- Terminal.app
- Claude Code in an interactive terminal session
- Python 3.9 or newer
- Accessibility access for Terminal in **System Settings > Privacy & Security > Accessibility**

Other terminal applications are not currently supported. The script sends keyboard input, so review the behavior and run a dry run before using it in an important session.

## Installation

Clone the repository and copy the skill directory into your Claude Code skills directory:

```bash
git clone https://github.com/ntguion/restart-claude-skill.git
cp -R restart-claude-skill/restart-claude ~/.claude/skills/
```

No third-party Python packages are required.

## Usage

From Claude Code, invoke:

```text
/restart-claude
```

To inspect the default behavior without sending keystrokes:

```bash
python3 ~/.claude/skills/restart-claude/restart.py --dry-run
```

To run the script directly:

```bash
python3 ~/.claude/skills/restart-claude/restart.py
```

By default, the restarted process uses `claude --continue`, which continues the most recent conversation for the current working directory with normal permission checks.

### Exact session

Pass a UUID when the current directory has multiple sessions and you need to select one explicitly:

```bash
python3 ~/.claude/skills/restart-claude/restart.py \
  --session-id 123e4567-e89b-12d3-a456-426614174000
```

### Timing and continuation message

Slow MCP startup can require a longer delay:

```bash
python3 ~/.claude/skills/restart-claude/restart.py --startup-delay 20
```

The continuation message can be changed or disabled:

```bash
python3 ~/.claude/skills/restart-claude/restart.py --message "Continue the previous task."
python3 ~/.claude/skills/restart-claude/restart.py --no-message
```

Run `python3 restart.py --help` for all options.

## Safety defaults

Permission checks remain enabled by default. The script supports Claude Code's `--dangerously-skip-permissions` flag only as an explicit opt-in:

```bash
python3 ~/.claude/skills/restart-claude/restart.py \
  --dangerously-skip-permissions
```

That mode bypasses Claude Code permission checks and should be limited to appropriately isolated environments. It is not required for this utility to work.

The script also:

- passes dynamic values to AppleScript as arguments instead of interpolating them into executable AppleScript source;
- selects the originating Terminal tab by its controlling TTY before sending keyboard input;
- validates exact session IDs as UUIDs; and
- checks the supported platform, required executables, and Accessibility access before scheduling the restart.

## How it works

1. Python identifies the controlling TTY for the process that invoked the skill.
2. It starts a detached AppleScript process so the automation survives the current Claude Code process exiting.
3. AppleScript finds and focuses the Terminal.app tab with the matching TTY.
4. System Events sends `Ctrl+C` twice, waits for the shell, and types the resume command.
5. After the configured startup delay, it optionally submits a continuation message.

The default delays are four seconds for the shell to return and twelve seconds for Claude Code to start. Both are configurable.

## Limitations

- Keyboard automation depends on Terminal.app focus and macOS Accessibility APIs. A dry run verifies configuration, but it cannot guarantee the timing of a real restart.
- `--continue` selects the most recent conversation for the current working directory. Use `--session-id` when that is not specific enough.
- Startup is delay-based; the script does not inspect Claude Code's UI to determine readiness.
- The utility does not kill stale MCP server processes or resolve port conflicts.
- Unsaved interactive input can be lost when `Ctrl+C` is sent.

If the restart command is typed but not accepted, increase `--shell-delay`. If the continuation message arrives too early, increase `--startup-delay` or use `--no-message`.

## Development

Run the standard-library test suite:

```bash
python3 -m unittest discover -s tests -v
```

The tests validate command construction, input validation, dry-run behavior, and the detached AppleScript invocation without sending keystrokes.

## License

MIT License. See [LICENSE](LICENSE).
