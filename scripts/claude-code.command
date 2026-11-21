#!/bin/zsh
# Runs Claude Code inside an interactive zsh, so quitting Claude drops back
# to a shell prompt instead of closing the terminal.
trap "" INT
[ -f "$HOME/.zshrc" ] && source "$HOME/.zshrc"
CLAUDE_BIN="$HOME/.local/bin/claude"
[ -x "$CLAUDE_BIN" ] || CLAUDE_BIN="claude"
"$CLAUDE_BIN" "$@"
exec zsh -il
