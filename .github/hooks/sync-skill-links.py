#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import time


DEFAULT_REPO_SOURCE_ROOTS = (
    "skills",
    ".agents/skills",
    ".claude/skills",
)
DEFAULT_EXTERNAL_ROOTS = (
    "~/skills",
    "~/.agents/skills",
)


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_repo_root(value: str | Path) -> Path:
    return Path(value).expanduser().resolve()


def resolve_repo_path(repo_root: Path, value: str | Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = repo_root / path
    return path.resolve()


def configured_external_roots(explicit_roots: list[str] | None) -> list[str]:
    if explicit_roots:
        return explicit_roots
    override = os.getenv("SKILL_LINK_EXTERNAL_ROOTS")
    if override is not None:
        return [part for part in override.split(os.pathsep) if part.strip()]
    return []


def iter_source_roots(repo_root: Path, external_roots: list[str]) -> list[tuple[str, Path]]:
    roots: list[tuple[str, Path]] = []
    for rel_path in DEFAULT_REPO_SOURCE_ROOTS:
        path = resolve_repo_path(repo_root, rel_path)
        if path.is_dir():
            roots.append((rel_path, path))
    for spec in external_roots:
        path = Path(spec).expanduser().resolve()
        if path.is_dir():
            roots.append((spec, path))
    return roots


def iter_skill_dirs(root: Path) -> list[Path]:
    skill_dirs: list[Path] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if (child / "SKILL.md").is_file():
            skill_dirs.append(child.resolve())
    return skill_dirs


def _root_skill_dirs(root: Path, mirror_root: Path) -> list[Path]:
    skill_dirs: list[Path] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if root == mirror_root and child.is_symlink():
            continue
        if (child / "SKILL.md").is_file():
            skill_dirs.append(child.resolve())
    return skill_dirs


def desired_skill_links(repo_root: Path, external_roots: list[str], *, mirror_root: str | Path = ".agents/skills") -> tuple[dict[str, Path], dict[str, list[str]], list[str]]:
    resolved_mirror_root = resolve_repo_path(repo_root, mirror_root)
    links: dict[str, Path] = {}
    duplicates: dict[str, list[str]] = {}
    source_labels: list[str] = []
    for label, root in iter_source_roots(repo_root, external_roots):
        source_labels.append(label)
        for skill_dir in _root_skill_dirs(root, resolved_mirror_root):
            skill_name = skill_dir.name
            if skill_name in links:
                duplicates.setdefault(skill_name, []).append(skill_dir.as_posix())
                continue
            links[skill_name] = skill_dir
    return links, duplicates, source_labels


def link_target(repo_root: Path, link_path: Path, source_path: Path) -> str:
    resolved_source = source_path.resolve()
    try:
        resolved_source.relative_to(repo_root)
    except ValueError:
        return resolved_source.as_posix()
    return os.path.relpath(resolved_source, start=link_path.parent)


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    if path.exists():
        shutil.rmtree(path)


def write_mirror_gitignore(
    repo_root: Path,
    mirror_root: Path,
    desired_links: dict[str, Path],
    external_roots: list[str] | None,
) -> None:
    resolved_external_roots = [Path(spec).expanduser().resolve() for spec in configured_external_roots(external_roots)]
    lines = [
        "# Managed by .github/hooks/sync-skill-links.py.",
        "# Ignore unmanaged local additions while keeping canonical links and in-place source dirs visible.",
        "*",
        "!.gitignore",
    ]
    for skill_name, source_path in sorted(desired_links.items()):
        if any(source_path == root or root in source_path.parents for root in resolved_external_roots):
            continue
        in_place_dir = source_path.parent == mirror_root.resolve() and not (mirror_root / skill_name).is_symlink()
        lines.append(f"!{skill_name}/" if in_place_dir else f"!{skill_name}")
    (mirror_root / ".gitignore").write_text("\n".join(lines) + "\n", encoding="utf-8")


def sync_skill_links(
    repo_root: Path,
    *,
    mirror_root: str | Path = ".agents/skills",
    external_roots: list[str] | None = None,
    prune: bool = True,
) -> dict[str, object]:
    resolved_repo_root = repo_root.resolve()
    resolved_mirror_root = resolve_repo_path(resolved_repo_root, mirror_root)
    resolved_mirror_root.mkdir(parents=True, exist_ok=True)

    desired_links, duplicates, source_labels = desired_skill_links(
        resolved_repo_root,
        configured_external_roots(external_roots),
        mirror_root=resolved_mirror_root,
    )

    created: list[str] = []
    updated: list[str] = []
    unchanged: list[str] = []
    removed: list[str] = []

    for skill_name, source_path in sorted(desired_links.items()):
        link_path = resolved_mirror_root / skill_name
        if link_path.exists() and not link_path.is_symlink() and link_path.resolve() == source_path.resolve():
            unchanged.append(skill_name)
            continue
        target_value = link_target(resolved_repo_root, link_path, source_path)
        existed = link_path.exists() or link_path.is_symlink()

        if link_path.is_symlink():
            try:
                if link_path.resolve() == source_path.resolve():
                    unchanged.append(skill_name)
                    continue
            except OSError:
                pass

        if existed:
            remove_path(link_path)
            updated.append(skill_name)
        else:
            created.append(skill_name)

        link_path.symlink_to(target_value, target_is_directory=True)

    write_mirror_gitignore(resolved_repo_root, resolved_mirror_root, desired_links, external_roots)

    if prune:
        for child in sorted(resolved_mirror_root.iterdir()):
            if child.name.startswith("."):
                continue
            if child.name in desired_links:
                continue
            remove_path(child)
            removed.append(child.name)

    return {
        "repo_root": resolved_repo_root.as_posix(),
        "mirror_root": resolved_mirror_root.as_posix(),
        "source_roots": source_labels,
        "created": created,
        "updated": updated,
        "unchanged": unchanged,
        "removed": removed,
        "duplicates": duplicates,
    }


def check_skill_links(
    repo_root: Path,
    *,
    mirror_root: str | Path = ".agents/skills",
    external_roots: list[str] | None = None,
    prune: bool = True,
) -> tuple[bool, dict[str, object]]:
    resolved_repo_root = repo_root.resolve()
    resolved_mirror_root = resolve_repo_path(resolved_repo_root, mirror_root)
    desired_links, duplicates, source_labels = desired_skill_links(
        resolved_repo_root,
        configured_external_roots(external_roots),
        mirror_root=resolved_mirror_root,
    )

    missing: list[str] = []
    non_symlink: list[str] = []
    wrong_target: list[str] = []
    extra: list[str] = []
    accepted_extra: list[str] = []

    for skill_name, source_path in sorted(desired_links.items()):
        link_path = resolved_mirror_root / skill_name
        if not (link_path.exists() or link_path.is_symlink()):
            missing.append(skill_name)
            continue
        if not link_path.is_symlink():
            try:
                if link_path.resolve() == source_path.resolve():
                    continue
            except OSError:
                pass
            non_symlink.append(skill_name)
            continue
        try:
            if link_path.resolve() != source_path.resolve():
                wrong_target.append(skill_name)
        except OSError:
            wrong_target.append(skill_name)

    if prune and resolved_mirror_root.is_dir():
        for child in sorted(resolved_mirror_root.iterdir()):
            if child.name.startswith("."):
                continue
            if child.name not in desired_links:
                if child.is_symlink():
                    try:
                        resolved = child.resolve()
                        if resolved.is_dir() and (resolved / "SKILL.md").is_file():
                            accepted_extra.append(child.name)
                            continue
                    except OSError:
                        pass
                extra.append(child.name)

    is_clean = not any((missing, non_symlink, wrong_target, extra, duplicates))
    return is_clean, {
        "repo_root": resolved_repo_root.as_posix(),
        "mirror_root": resolved_mirror_root.as_posix(),
        "source_roots": source_labels,
        "missing": missing,
        "non_symlink": non_symlink,
        "wrong_target": wrong_target,
        "accepted_extra": accepted_extra,
        "extra": extra,
        "duplicates": duplicates,
        "status": "ok" if is_clean else "drift",
    }


def watch_skill_links(
    repo_root: Path,
    *,
    mirror_root: str | Path = ".agents/skills",
    external_roots: list[str] | None = None,
    prune: bool = True,
    interval_seconds: float = 2.0,
    quiet: bool = False,
) -> int:
    while True:
        payload = sync_skill_links(
            repo_root,
            mirror_root=mirror_root,
            external_roots=external_roots,
            prune=prune,
        )
        changed = any(payload[key] for key in ("created", "updated", "removed"))
        if changed and not quiet:
            print(json.dumps(payload, indent=2), flush=True)
        time.sleep(interval_seconds)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize .agents/skills into a symlink mirror of the configured skill roots.")
    parser.add_argument("--repo-root", default=default_repo_root().as_posix())
    parser.add_argument("--mirror-root", default=".agents/skills")
    parser.add_argument("--external-root", action="append")
    parser.add_argument("--no-prune", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--interval-seconds", type=float, default=2.0)
    parser.add_argument("--quiet", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.watch:
        try:
            return watch_skill_links(
                resolve_repo_root(args.repo_root),
                mirror_root=args.mirror_root,
                external_roots=args.external_root,
                prune=not args.no_prune,
                interval_seconds=args.interval_seconds,
                quiet=args.quiet,
            )
        except KeyboardInterrupt:
            return 0

    if args.check:
        is_clean, payload = check_skill_links(
            resolve_repo_root(args.repo_root),
            mirror_root=args.mirror_root,
            external_roots=args.external_root,
            prune=not args.no_prune,
        )
        if not args.quiet:
            print(json.dumps(payload, indent=2))
        return 0 if is_clean else 1

    payload = sync_skill_links(
        resolve_repo_root(args.repo_root),
        mirror_root=args.mirror_root,
        external_roots=args.external_root,
        prune=not args.no_prune,
    )
    if not args.quiet:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())