#!/usr/bin/env bash
# Claude Code hook: append one JSON line per event, tagged with the tmux pane.
printf '{"pane":"%s","state":"%s"}\n' "$TMUX_PANE" "$1" >> "$HOME/projects/agentpad/events.jsonl"
