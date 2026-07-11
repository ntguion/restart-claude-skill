---
name: restart-claude
description: Restart the current Claude Code session in the same macOS Terminal.app tab after MCP or startup configuration changes. Use only when the user explicitly asks to restart Claude Code or a restart is necessary to apply configuration.
metadata:
  version: "2.1"
  last_updated: "2026-07-11"
---

# Restart Claude Code

Restart Claude Code in the originating Terminal.app tab and continue the most recent conversation for the current working directory.

## Before restarting

1. Tell the user that the restart will interrupt the current interactive process.
2. Make sure Terminal.app is allowed under **System Settings > Privacy & Security > Accessibility**.
3. Run a dry run and inspect the command:

```bash
python3 ~/.claude/skills/restart-claude/restart.py --dry-run
```

Do not enable permission bypass unless the user explicitly requests it and the environment is appropriately isolated.

## Restart

```bash
python3 ~/.claude/skills/restart-claude/restart.py
```

The default behavior:

1. Finds the originating Terminal tab by its controlling TTY.
2. Sends `Ctrl+C` twice to stop the current Claude Code process.
3. Runs `claude --continue` with normal permission checks.
4. Waits for Claude Code to start.
5. Submits a short continuation message.

Use `--session-id UUID` to resume a specific session. Use `--startup-delay SECONDS` when MCP servers take longer than twelve seconds to load. Use `--no-message` when a continuation message should not be submitted automatically.

## Boundaries

- Supports macOS Terminal.app only.
- Relies on keyboard automation and fixed delays.
- Interrupting Claude Code can discard unsaved interactive input.
- Does not resolve stale processes or port conflicts.
- Never add `--dangerously-skip-permissions` implicitly.

Run `python3 ~/.claude/skills/restart-claude/restart.py --help` for the complete option list.
