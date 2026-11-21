#!/usr/bin/env bash
# Install the dev methodology kit for Claude Code, Codex and other agent tools,
# plus optional VS Code settings, keybindings, extensions and the Claude Code
# terminal launcher.
#
# Usage:
#   ./install.sh                 link skills, agent, command, scripts (default)
#   ./install.sh --vscode        also merge VS Code settings and keybindings
#   ./install.sh --extensions    also install the core VS Code extensions
#   ./install.sh --all           all of the above
#   ./install.sh --dry-run ...   show what would change, change nothing
#
# Existing files are never overwritten. A target that already exists and is not
# a link into this kit is skipped and reported.
set -euo pipefail

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY=0; VSCODE=0; EXT=0
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    --vscode) VSCODE=1 ;;
    --extensions) EXT=1 ;;
    --all) VSCODE=1; EXT=1 ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "Unknown option: $a" >&2; exit 2 ;;
  esac
done

run() { if [ "$DRY" = 1 ]; then echo "  would run: $*"; else "$@"; fi; }

link() {  # link <source> <target>
  local src="$1" dst="$2"
  if [ -L "$dst" ]; then
    if [ "$(readlink "$dst")" = "$src" ]; then echo "  ok      $dst"; return; fi
    echo "  SKIP    $dst (links elsewhere: $(readlink "$dst"))"; return
  fi
  if [ -e "$dst" ]; then echo "  SKIP    $dst (already exists)"; return; fi
  run mkdir -p "$(dirname "$dst")"
  run ln -s "$src" "$dst"
  echo "  linked  $dst"
}

echo "Kit: $KIT"
[ "$DRY" = 1 ] && echo "(dry run: nothing will change)"

echo; echo "Kit home"
link "$KIT" "$HOME/.devmethodology"

echo; echo "Claude Code"
for s in "$KIT"/skills/*/; do s="${s%/}"; link "$s" "$HOME/.claude/skills/$(basename "$s")"; done
for f in "$KIT"/agents/*.md; do link "$f" "$HOME/.claude/agents/$(basename "$f")"; done
for f in "$KIT"/commands/*.md; do link "$f" "$HOME/.claude/commands/$(basename "$f")"; done

echo; echo "Other agent tools (only folders that already exist)"
for dir in "$HOME/.codex/skills" "$HOME/.agents/skills" "$HOME/.cursor/skills"; do
  if [ -d "$dir" ]; then
    for s in "$KIT"/skills/*/; do s="${s%/}"; link "$s" "$dir/$(basename "$s")"; done
  else
    echo "  none    $dir (tool not set up; create the folder and re-run to link)"
  fi
done

echo; echo "Scripts"
link "$KIT/scripts/claude-code.command" "$HOME/Applications/Claude Code.command"

VSU="$HOME/Library/Application Support/Code/User"
if [ "$VSCODE" = 1 ]; then
  echo; echo "VS Code settings and keybindings"
  if [ ! -d "$VSU" ]; then
    echo "  SKIP    VS Code user folder not found: $VSU"
  else
    DRY="$DRY" KIT="$KIT" VSU="$VSU" python3 - <<'PY'
import json, os, re, shutil, time
from pathlib import Path

dry = os.environ["DRY"] == "1"
kit, vsu = Path(os.environ["KIT"]), Path(os.environ["VSU"])
stamp = time.strftime("%Y%m%d-%H%M%S")

def load(p):
    if not p.exists() or not p.read_text().strip():
        return None
    text = re.sub(r"^\s*//.*$", "", p.read_text(), flags=re.M)   # drop // comment lines
    text = re.sub(r",(\s*[}\]])", r"\1", text)                     # drop trailing commas
    return json.loads(text)

def save(p, data):
    if p.exists():
        shutil.copy2(p, p.with_name(p.name + f".pre-devmethodology-{stamp}"))
    p.write_text(json.dumps(data, indent=2) + "\n")

ours = json.loads((kit / "vscode/settings.json").read_text().replace("__HOME__", str(Path.home())))
sp = vsu / "settings.json"
cur = load(sp) or {}
added = [k for k in ours if k not in cur]
differ = [k for k in ours if k in cur and cur[k] != ours[k]]
for k in added:
    cur[k] = ours[k]
print(f"  settings: {len(added)} to add, {len(differ)} already set differently (left as they are)")
for k in differ:
    print(f"    kept existing: {k}")
if added and not dry:
    save(sp, cur)

kb = json.loads((kit / "vscode/keybindings.json").read_text())
kp = vsu / "keybindings.json"
curk = load(kp) or []
new = [b for b in kb if b not in curk]
print(f"  keybindings: {len(new)} to add")
if new and not dry:
    save(kp, curk + new)
PY
  fi
fi

if [ "$EXT" = 1 ]; then
  echo; echo "VS Code extensions (core list)"
  if ! command -v code >/dev/null; then
    echo "  SKIP    'code' command not on PATH (VS Code: Shell Command: Install 'code' command in PATH)"
  else
    have="$(code --list-extensions | tr 'A-Z' 'a-z')"
    grep -vE '^\s*(#|$)' "$KIT/vscode/extensions.txt" | while read -r id; do
      if echo "$have" | grep -qx "$(echo "$id" | tr 'A-Z' 'a-z')"; then echo "  ok      $id"
      else run code --install-extension "$id" >/dev/null && echo "  added   $id"; fi
    done
  fi
fi

echo; echo "Done. Restart Claude Code (and reload VS Code) to pick up the changes."
