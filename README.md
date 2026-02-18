# Restart Claude Code Skill

A Claude Code skill that restarts your session to reload MCP servers or apply config changes — without leaving your terminal window.

## What It Does

When Claude Code needs a restart (MCP server changes, config updates, broken session), this skill handles the full cycle automatically:

1. Kills the current Claude Code process (Ctrl+C)
2. Types the `claude --resume` command to restart with your session intact
3. Waits for Claude Code to fully load
4. Submits a continuation message so Claude picks up where you left off

Everything happens in the **same terminal window**. No new windows, no new tabs, no manual intervention.

## Requirements

- **macOS** (uses AppleScript + System Events for keyboard simulation)
- **Terminal.app** (the script targets Terminal specifically)
- **Claude Code** running in interactive mode
- **Accessibility permissions** for Terminal (System Settings > Privacy > Accessibility)

## Installation

Clone this repo and copy the skill into your Claude Code skills directory:

```bash
git clone https://github.com/ntguion/restart-claude-skill.git
cp -r restart-claude-skill/restart-claude ~/.claude/skills/
```

## Usage

From within a Claude Code session, invoke the skill:

```
/restart-claude
```

Or run the script directly:

```bash
python3 ~/.claude/skills/restart-claude/restart.py
```

## How It Works

The script is ~30 lines of Python. It:

1. Finds the current session ID by looking for the most recently modified `.jsonl` file in `~/.claude/projects/`
2. Launches a **detached** AppleScript (`start_new_session=True`) that survives Claude's death
3. The AppleScript simulates exactly what you'd do manually:
   - `Ctrl+C` twice to exit Claude Code
   - Waits for the shell prompt
   - Types the resume command and presses Enter
   - Waits 12 seconds for Claude Code to fully load (MCP servers, etc.)
   - Types a continuation message and presses Enter

The detached AppleScript is the key trick. It runs independently of Claude Code, so it keeps going after Claude dies. System Events keystrokes go to the front Terminal window, exactly like physical key presses.

## Configuration

The script has two timing values you may want to adjust in `restart.py`:

| Delay | Default | Purpose |
|-------|---------|---------|
| `delay 4` | 4s | Time after Ctrl+C for shell prompt to appear |
| `delay 12` | 12s | Time for Claude Code to fully load (MCP servers, etc.) |

If you have many MCP servers, bump `delay 12` to `delay 15` or higher.

## Gotchas

- **Terminal must be focused** — the AppleScript sends keystrokes to the front Terminal window. If another app is focused, keystrokes go to the wrong place.
- **Port conflicts** — if an MCP WebSocket server port is already bound from the old session, the new one will fail. Kill stale ports with `lsof -ti:<port> | xargs kill -9`.
- **macOS only** — relies on AppleScript and System Events. No Linux/Windows support.

## License

MIT License — see [LICENSE](LICENSE) for details.
