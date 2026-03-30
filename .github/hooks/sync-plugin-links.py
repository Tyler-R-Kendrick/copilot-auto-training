#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import time


COMPONENT_DIRS = {
    "skills": "skills",
    "agents": "agents",
    "mcps": "mcps",
    "hooks": "hooks",
}
CONFIG_PATH = Path(".github/plugin/plugin-sources.json")
MARKETPLACE_PATH = Path(".github/plugin/marketplace.json")


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_repo_root(value: str | Path) -> Path:
    return Path(value).expanduser().resolve()


def load_plugin_config(repo_root: Path) -> dict[str, object]:
    return json.loads((repo_root / CONFIG_PATH).read_text(encoding="utf-8"))


def plugin_definition(repo_root: Path) -> dict[str, object]:
    config = load_plugin_config(repo_root)
    plugin = config.get("plugin")
    if not isinstance(plugin, dict):
        raise ValueError("plugin-sources.json field 'plugin' must be an object")
    return plugin


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    if path.exists():
        shutil.rmtree(path)


def link_target(link_path: Path, source_path: Path) -> str:
    return os.path.relpath(source_path.resolve(), start=link_path.parent.resolve())


def plugin_root(repo_root: Path) -> Path:
    plugin = plugin_definition(repo_root)
    directory = plugin.get("directory")
    if not isinstance(directory, str) or not directory.strip():
        raise ValueError("plugin-sources.json field 'plugin.directory' must be a non-empty string")
    return (repo_root / directory).resolve()


def _iter_root_entries(root_path: Path, excluded_names: set[str]) -> list[Path]:
    entries: list[Path] = []
    for child in sorted(root_path.iterdir()):
        if child.name.startswith("."):
            continue
        if child.name in excluded_names:
            continue
        entries.append(child)
    return entries


def _component_specs(repo_root: Path, component_name: str, raw_values: object) -> list[tuple[str, str, Path]]:
    component_dir = COMPONENT_DIRS[component_name]
    if not isinstance(raw_values, list):
        raise ValueError(f"Plugin field 'components.{component_name}' must be an array")

    specs: list[tuple[str, str, Path]] = []
    for raw_value in raw_values:
        if isinstance(raw_value, str) and raw_value.strip():
            source_path = (repo_root / raw_value).resolve()
            specs.append((component_dir, Path(raw_value).name, source_path))
            continue

        if isinstance(raw_value, dict):
            root_value = raw_value.get("root")
            if not isinstance(root_value, str) or not root_value.strip():
                raise ValueError(f"Plugin field 'components.{component_name}' object entries require a non-empty 'root'")
            excluded_raw = raw_value.get("exclude", [])
            if not isinstance(excluded_raw, list) or any(not isinstance(item, str) for item in excluded_raw):
                raise ValueError(f"Plugin field 'components.{component_name}.exclude' must be an array of strings")
            root_path = (repo_root / root_value).resolve()
            if not root_path.is_dir():
                raise FileNotFoundError(f"Plugin component root not found: {root_value}")
            for child in _iter_root_entries(root_path, set(excluded_raw)):
                specs.append((component_dir, child.name, child.resolve()))
            continue

        raise ValueError(f"Plugin field 'components.{component_name}' contains an invalid entry")

    return specs


def desired_plugin_links(repo_root: Path) -> dict[str, Path]:
    plugin = plugin_definition(repo_root)
    components = plugin.get("components", {})
    if not isinstance(components, dict):
        raise ValueError("plugin-sources.json field 'plugin.components' must be an object")

    plugin_links: dict[str, Path] = {}
    for component_name in COMPONENT_DIRS:
        for component_dir, entry_name, source_path in _component_specs(repo_root, component_name, components.get(component_name, [])):
            if not source_path.exists():
                raise FileNotFoundError(f"Plugin source path not found: {source_path.as_posix()}")
            plugin_links[f"{component_dir}/{entry_name}"] = source_path
    return plugin_links


def build_marketplace_definition(repo_root: Path) -> dict[str, object]:
    config = load_plugin_config(repo_root)
    marketplace = config.get("marketplace")
    if not isinstance(marketplace, dict):
        raise ValueError("plugin-sources.json field 'marketplace' must be an object")
    plugin = plugin_definition(repo_root)
    plugin_dir = plugin_root(repo_root)
    manifest_path = plugin_dir / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    return {
        "name": marketplace["name"],
        "owner": marketplace["owner"],
        "metadata": marketplace["metadata"],
        "plugins": [
            {
                "name": manifest["name"],
                "description": manifest["description"],
                "version": manifest["version"],
                "source": str(plugin_dir.relative_to(repo_root).as_posix()),
            }
        ],
    }


def sync_plugin_links(repo_root: Path, *, prune: bool = True) -> dict[str, object]:
    resolved_repo_root = repo_root.resolve()
    desired = desired_plugin_links(resolved_repo_root)
    plugin = plugin_definition(resolved_repo_root)
    plugin_name = plugin.get("name")
    if not isinstance(plugin_name, str) or not plugin_name.strip():
        raise ValueError("plugin-sources.json field 'plugin.name' must be a non-empty string")
    plugin_root_path = plugin_root(resolved_repo_root)
    plugins_dir = (resolved_repo_root / "plugins").resolve()

    created: list[str] = []
    updated: list[str] = []
    unchanged: list[str] = []
    removed: list[str] = []

    plugin_root_path.mkdir(parents=True, exist_ok=True)

    if prune and plugins_dir.is_dir():
        for child in sorted(plugins_dir.iterdir()):
            if child.resolve() == plugin_root_path:
                continue
            remove_path(child)
            removed.append(child.relative_to(plugins_dir).as_posix())

    for component_dir in COMPONENT_DIRS.values():
        component_root = plugin_root_path / component_dir
        if any(key.startswith(f"{component_dir}/") for key in desired):
            component_root.mkdir(parents=True, exist_ok=True)
        elif prune and component_root.exists():
            remove_path(component_root)
            removed.append(f"{plugin_name}:{component_dir}")

    for relative_path, source_path in sorted(desired.items()):
        link_path = plugin_root_path / relative_path
        link_path.parent.mkdir(parents=True, exist_ok=True)
        existed = link_path.exists() or link_path.is_symlink()

        if link_path.is_symlink():
            try:
                if link_path.resolve() == source_path.resolve():
                    unchanged.append(f"{plugin_name}:{relative_path}")
                    continue
            except OSError:
                pass
        elif link_path.exists():
            try:
                if link_path.resolve() == source_path.resolve():
                    unchanged.append(f"{plugin_name}:{relative_path}")
                    continue
            except OSError:
                pass

        if existed:
            remove_path(link_path)
            updated.append(f"{plugin_name}:{relative_path}")
        else:
            created.append(f"{plugin_name}:{relative_path}")

        link_path.symlink_to(link_target(link_path, source_path), target_is_directory=source_path.is_dir())

    if prune:
        allowed_paths = {Path(key) for key in desired}
        for component_dir in COMPONENT_DIRS.values():
            component_root = plugin_root_path / component_dir
            if not component_root.is_dir():
                continue
            for child in sorted(component_root.iterdir()):
                relative_child = child.relative_to(plugin_root_path)
                if relative_child in allowed_paths:
                    continue
                remove_path(child)
                removed.append(f"{plugin_name}:{relative_child.as_posix()}")

    marketplace_payload = build_marketplace_definition(resolved_repo_root)
    marketplace_path = resolved_repo_root / MARKETPLACE_PATH
    rendered_marketplace = json.dumps(marketplace_payload, indent=2) + "\n"
    current_marketplace = marketplace_path.read_text(encoding="utf-8") if marketplace_path.exists() else None
    marketplace_updated = current_marketplace != rendered_marketplace
    if marketplace_updated:
        marketplace_path.write_text(rendered_marketplace, encoding="utf-8")

    return {
        "repo_root": resolved_repo_root.as_posix(),
        "config_file": (resolved_repo_root / CONFIG_PATH).as_posix(),
        "created": created,
        "updated": updated,
        "unchanged": unchanged,
        "removed": removed,
        "marketplace_updated": marketplace_updated,
    }


def check_plugin_links(repo_root: Path, *, prune: bool = True) -> tuple[bool, dict[str, object]]:
    resolved_repo_root = repo_root.resolve()
    desired = desired_plugin_links(resolved_repo_root)
    plugin = plugin_definition(resolved_repo_root)
    plugin_name = plugin.get("name")
    if not isinstance(plugin_name, str) or not plugin_name.strip():
        raise ValueError("plugin-sources.json field 'plugin.name' must be a non-empty string")
    plugin_root_path = plugin_root(resolved_repo_root)
    plugins_dir = (resolved_repo_root / "plugins").resolve()

    missing: list[str] = []
    non_symlink: list[str] = []
    wrong_target: list[str] = []
    extra: list[str] = []

    for relative_path, source_path in sorted(desired.items()):
        link_path = plugin_root_path / relative_path
        label = f"{plugin_name}:{relative_path}"
        if not (link_path.exists() or link_path.is_symlink()):
            missing.append(label)
            continue
        if not link_path.is_symlink():
            non_symlink.append(label)
            continue
        try:
            if link_path.resolve() != source_path.resolve():
                wrong_target.append(label)
        except OSError:
            wrong_target.append(label)

    if prune:
        allowed_paths = {Path(key) for key in desired}
        for component_dir in COMPONENT_DIRS.values():
            component_root = plugin_root_path / component_dir
            if not component_root.is_dir():
                continue
            for child in sorted(component_root.iterdir()):
                relative_child = child.relative_to(plugin_root_path)
                if relative_child not in allowed_paths:
                    extra.append(f"{plugin_name}:{relative_child.as_posix()}")
        if plugins_dir.is_dir():
            for child in sorted(plugins_dir.iterdir()):
                if child.resolve() != plugin_root_path:
                    extra.append(child.relative_to(plugins_dir).as_posix())

    expected_marketplace = json.dumps(build_marketplace_definition(resolved_repo_root), indent=2) + "\n"
    marketplace_path = resolved_repo_root / MARKETPLACE_PATH
    marketplace_in_sync = marketplace_path.exists() and marketplace_path.read_text(encoding="utf-8") == expected_marketplace

    is_clean = not any((missing, non_symlink, wrong_target, extra)) and marketplace_in_sync
    return is_clean, {
        "repo_root": resolved_repo_root.as_posix(),
        "config_file": (resolved_repo_root / CONFIG_PATH).as_posix(),
        "missing": missing,
        "non_symlink": non_symlink,
        "wrong_target": wrong_target,
        "extra": extra,
        "marketplace_in_sync": marketplace_in_sync,
        "status": "ok" if is_clean else "drift",
    }


def watch_plugin_links(
    repo_root: Path,
    *,
    prune: bool = True,
    interval_seconds: float = 2.0,
    quiet: bool = False,
) -> int:
    while True:
        payload = sync_plugin_links(repo_root, prune=prune)
        changed = any(payload[key] for key in ("created", "updated", "removed")) or payload["marketplace_updated"]
        if changed and not quiet:
            print(json.dumps(payload, indent=2), flush=True)
        time.sleep(interval_seconds)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize plugin component links and regenerate marketplace.json.")
    parser.add_argument("--repo-root", default=default_repo_root().as_posix())
    parser.add_argument("--no-prune", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--interval-seconds", type=float, default=2.0)
    parser.add_argument("--quiet", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = resolve_repo_root(args.repo_root)

    if args.watch:
        try:
            return watch_plugin_links(
                repo_root,
                prune=not args.no_prune,
                interval_seconds=args.interval_seconds,
                quiet=args.quiet,
            )
        except KeyboardInterrupt:
            return 0

    if args.check:
        is_clean, payload = check_plugin_links(repo_root, prune=not args.no_prune)
        if not args.quiet:
            print(json.dumps(payload, indent=2))
        return 0 if is_clean else 1

    payload = sync_plugin_links(repo_root, prune=not args.no_prune)
    if not args.quiet:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())