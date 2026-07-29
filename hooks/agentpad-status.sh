#!/usr/bin/env bash
# Claude Code statusLine command.
#
# Two jobs:
#   1. Print the status line text shown under the prompt.
#   2. Record this session's context-window usage, tagged with its tmux pane, so the
#      Agent Pad daemon can drive the LED bar graph.
#
# The statusLine payload is the only place Claude Code exposes context_window
# usage, and it inherits $TMUX_PANE inside a tmux window (verified), which is what
# lets us attribute a percentage to the right agent.
payload=$(cat)
pct=$(printf '%s' "$payload" | jq -r '.context_window.used_percentage // empty' 2>/dev/null)

if [ -n "$TMUX_PANE" ] && [ -n "$pct" ]; then
  printf '{"pane":"%s","pct":%s}\n' "$TMUX_PANE" "$pct" \
    >> "${AGENTPAD_DIR:-$HOME/github/agentpad}/context.jsonl"
fi

# Keep the visible status line short.
model=$(printf '%s' "$payload" | jq -r '.model.display_name // ""' 2>/dev/null)
printf '%s%s' "$model" "${pct:+  ctx ${pct}%}"
