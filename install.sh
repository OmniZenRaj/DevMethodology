#!/usr/bin/env bash
# Install the dev methodology kit for Claude Code, Codex and other agent tools,
# plus optional VS Code settings, keybindings, extensions and the Claude Code
# terminal launcher.
#
# Usage:
#   ./install.sh                 link skills, agent, command, scripts (default)
#   ./install.sh --vscode        also merge VS Code settings and keybindings
#   ./install.sh --extensions    also install the core VS Code extensions
#   ./install.sh --patch         also patch the Claude Code extension (keeps its terminal open after /exit)
#   ./install.sh --all           all of the above
#   ./install.sh --extra <dir>   also link skills, agents and commands from another kit
#                                folder with the same layout (repeatable), e.g. a work repo
#   ./install.sh --dry-run ...   show what would change, change nothing
#
# Existing files are never overwritten. A target that already exists and is not
# a link into this kit is skipped and reported.
set -euo pipefail

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY=0; VSCODE=0; EXT=0; PATCH=0; EXTRAS=()
while [ $# -gt 0 ]; do
  a="$1"; shift
  case "$a" in
    --dry-run) DRY=1 ;;
    --vscode) VSCODE=1 ;;
    --extensions) EXT=1 ;;
    --patch) PATCH=1 ;;
    --all) VSCODE=1; EXT=1; PATCH=1 ;;
    --extra)
      [ $# -gt 0 ] || { echo "--extra needs a folder" >&2; exit 2; }
      [ -d "$1" ] || { echo "Not a folder: $1" >&2; exit 2; }
      EXTRAS+=("$(cd "$1" && pwd)"); shift ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
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

install_from() {  # install_from <kit folder>
  local src="$1"
  echo; echo "Claude Code ($src)"
  for s in "$src"/skills/*/; do [ -d "$s" ] || continue; s="${s%/}"; link "$s" "$HOME/.claude/skills/$(basename "$s")"; done
  for f in "$src"/agents/*.md; do [ -e "$f" ] || continue; link "$f" "$HOME/.claude/agents/$(basename "$f")"; done
  for f in "$src"/commands/*.md; do [ -e "$f" ] || continue; link "$f" "$HOME/.claude/commands/$(basename "$f")"; done
  echo; echo "Other agent tools ($src; only folders that already exist)"
  for dir in "$HOME/.codex/skills" "$HOME/.agents/skills" "$HOME/.cursor/skills"; do
    if [ -d "$dir" ]; then
      for s in "$src"/skills/*/; do [ -d "$s" ] || continue; s="${s%/}"; link "$s" "$dir/$(basename "$s")"; done
    else
      echo "  none    $dir (tool not set up; create the folder and re-run to link)"
    fi
  done
}

install_from "$KIT"
for x in ${EXTRAS[@]+"${EXTRAS[@]}"}; do install_from "$x"; done

echo; echo "Scripts"
link "$KIT/scripts/patch-claude-vscode" "$HOME/.local/bin/patch-claude-vscode"
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

if [ "$PATCH" = 1 ]; then
  echo; echo "Claude Code extension patch"
  run python3 "$KIT/scripts/patch-claude-vscode"
  echo "  Reload the VS Code window afterwards. Re-run after every Claude Code extension update."
fi

echo; echo "Done. Restart Claude Code (and reload VS Code) to pick up the changes."
