#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python_bin="$repo_root/.venv/bin/python"
sync_helper="$repo_root/.github/hooks/sync-skill-links.py"
mirror_root="$repo_root/.agents/skills"
runtime_dir="${XDG_RUNTIME_DIR:-/tmp}"
pid_file="$runtime_dir/copilot-training-skill-link-watcher-$UID.pid"

"$python_bin" "$sync_helper" \
  --repo-root "$repo_root" \
  --mirror-root "$mirror_root" \
  --external-root "$HOME/skills" \
  --external-root "$HOME/.agents/skills" \
  --quiet

desired_watcher_pid=""
existing_watchers="$(pgrep -u "$UID" -f "$sync_helper .*--watch" || true)"
for watcher_pid in $existing_watchers; do
  [[ -n "$watcher_pid" ]] || continue
  cmdline="$(tr '\0' ' ' < "/proc/$watcher_pid/cmdline" 2>/dev/null || true)"
  if [[ "$cmdline" == *"--mirror-root"* ]] && [[ "$cmdline" == *"$mirror_root"* ]]; then
    desired_watcher_pid="$watcher_pid"
    continue
  fi
  kill "$watcher_pid" 2>/dev/null || true
done

if [[ -n "$desired_watcher_pid" ]] && kill -0 "$desired_watcher_pid" 2>/dev/null; then
  echo "$desired_watcher_pid" > "$pid_file"
  exit 0
fi

rm -f "$pid_file"

nohup "$python_bin" "$sync_helper" \
  --repo-root "$repo_root" \
  --mirror-root "$mirror_root" \
  --external-root "$HOME/skills" \
  --external-root "$HOME/.agents/skills" \
  --watch \
  --quiet \
  >/dev/null 2>&1 &

echo "$!" > "$pid_file"