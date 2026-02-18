---
name: restart-claude
description: Restart the current Claude Code session to reload MCP servers or apply config changes. Kills Claude, resumes the session, and auto-submits a continuation message — all in the same terminal window.
metadata:
  version: "2.0"
  last_updated: "2026-02-17"
---

# Restart Claude Code

Use when you need to reload MCP servers, apply config changes, or recover from a broken session.

## Usage

```bash
python3 ~/.claude/skills/restart-claude/restart.py
```

The script simulates exactly what a user would do:
1. Finds the current session ID (most recently modified `.jsonl` in `~/.claude/projects/`)
2. Launches a detached AppleScript that:
   - Sends Ctrl+C twice to kill Claude in the current terminal
   - Types the `claude --resume` command and presses Enter
   - Waits for Claude to load
   - Types a continuation message and presses Enter

Everything happens in the **same terminal window** — no new windows or tabs.

## Gotchas

- **Port conflicts**: If an MCP WebSocket server is already bound, the new process will fail to start. Kill stale port holders with `lsof -ti:<port> | xargs kill -9` first.
- **Terminal focus**: The script targets the front Terminal window. Make sure it's focused when running.
- **Load time**: Claude has 12s to load before the message is typed. If MCPs are heavy, bump `delay 12` in restart.py.
