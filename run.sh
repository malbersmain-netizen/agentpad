#!/usr/bin/env bash
# Start Agent Pad. Run from anywhere:  ~/projects/agentpad/run.sh
#
# Checks the board is actually there before starting, and refuses to run a second
# daemon -- two processes fighting over one serial port is the confusing failure
# ("serial noise or corruption") that reads like a hardware fault.
set -u
cd "$(dirname "$0")" || exit 1

PORT=/dev/cu.usbserial-0001

if [ ! -e "$PORT" ]; then
  echo "No board at $PORT."
  echo
  echo "  - is the USB cable plugged in at both ends?"
  echo "  - is it a DATA cable? a charge-only cable powers the board but never enumerates"
  echo "  - ls /dev/cu.*   to see what the Mac can see"
  exit 1
fi

if pgrep -f "python daemon.py" >/dev/null; then
  echo "A daemon is already running (pid $(pgrep -f 'python daemon.py' | tr '\n' ' '))."
  read -r -p "Stop it and start fresh? [y/N] " a
  case "$a" in
    y|Y) pkill -f "python daemon.py"; sleep 2 ;;
    *)   echo "Leaving it alone."; exit 0 ;;
  esac
fi

echo "Board:   $PORT"
echo "Attach:  tmux attach -t agentpad     (in another terminal)"
echo "Stop:    ctrl-c"
echo
exec mise exec -- python daemon.py
