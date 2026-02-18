#!/usr/bin/env python3
"""Restart Claude Code in the current terminal. Simulates exactly what a user would do."""
import glob, os, subprocess, sys

# Find session ID
files = glob.glob(os.path.expanduser("~/.claude/projects/**/*.jsonl"), recursive=True)
if not files:
    sys.exit("No session files found")
session_id = os.path.basename(max(files, key=os.path.getmtime)).replace(".jsonl", "")

# AppleScript: Ctrl+C twice to kill Claude, type resume cmd, wait, type msg, submit
applescript = f'''
tell application "Terminal" to activate
tell application "System Events"
    tell process "Terminal"
        keystroke "c" using control down
        delay 0.3
        keystroke "c" using control down
        delay 4
        keystroke "claude --dangerously-skip-permissions --resume {session_id}"
        delay 0.5
        key code 36
        delay 12
        keystroke "Restart successful, please continue where we left off."
        delay 1
        key code 36
    end tell
end tell
'''

subprocess.Popen(
    ["osascript", "-e", applescript],
    start_new_session=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
