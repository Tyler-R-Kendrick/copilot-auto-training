from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_SOURCES_PATH = REPO_ROOT / ".github" / "plugin" / "plugin-sources.json"
MARKETPLACE_PATH = REPO_ROOT / ".github" / "plugin" / "marketplace.json"
PLUGINS_DIR = REPO_ROOT / "plugins"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _plugin_definition() -> dict[str, object]:
    return _load_json(PLUGIN_SOURCES_PATH)["plugin"]


def _load_plugin_links_module():
    module_path = REPO_ROOT / ".github" / "hooks" / "sync-plugin-links.py"
    spec = importlib.util.spec_from_file_location("test_cli_plugins_sync_plugin_links", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules.setdefault("test_cli_plugins_sync_plugin_links", module)
    spec.loader.exec_module(module)
    return module


def _relative_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
            continue
        files.append(relative)
    return sorted(files)


def test_marketplace_manifest_lists_existing_plugin():
    plugin = _plugin_definition()
    payload = _load_json(MARKETPLACE_PATH)
    source_dir = REPO_ROOT / plugin["directory"]
    manifest = _load_json(source_dir / "plugin.json")

    assert payload["name"] == "copilot-training"
    assert payload["metadata"]["version"] == "0.1.0"
    assert payload["plugins"] == [
        {
            "name": manifest["name"],
            "description": manifest["description"],
            "version": manifest["version"],
            "source": plugin["directory"],
        }
    ]
    assert source_dir.is_dir()
    assert (source_dir / "plugin.json").is_file()


def test_plugin_manifest_matches_marketplace_entry():
    plugin = _plugin_definition()
    marketplace = _load_json(MARKETPLACE_PATH)
    marketplace_plugin = marketplace["plugins"][0]
    manifest = _load_json(REPO_ROOT / plugin["directory"] / "plugin.json")

    assert manifest["name"] == marketplace_plugin["name"]
    assert manifest["description"] == marketplace_plugin["description"]
    assert manifest["version"] == marketplace_plugin["version"]
    assert manifest["license"] == "MIT"
    assert manifest["repository"] == "https://github.com/Tyler-R-Kendrick/copilot-apo"


def test_plugin_source_config_matches_marketplace_entry():
    plugin = _plugin_definition()
    marketplace = _load_json(MARKETPLACE_PATH)
    manifest = _load_json(REPO_ROOT / plugin["directory"] / "plugin.json")

    assert marketplace["plugins"] == [
        {
            "name": manifest["name"],
            "description": manifest["description"],
            "version": manifest["version"],
            "source": plugin["directory"],
        }
    ]


def test_plugin_linked_components_match_canonical_sources():
    module = _load_plugin_links_module()
    plugin = _plugin_definition()
    plugin_root = REPO_ROOT / plugin["directory"]
    desired_links = module.desired_plugin_links(REPO_ROOT)

    for relative_path, source_path in desired_links.items():
        plugin_path = plugin_root / relative_path

        assert source_path.exists()
        assert plugin_path.is_symlink()
        assert plugin_path.resolve() == source_path.resolve()

        if source_path.is_dir():
            assert _relative_files(plugin_path) == _relative_files(source_path)
        else:
            assert plugin_path.read_bytes() == source_path.read_bytes()

    assert not (plugin_root / "agents" / ".trainer-workspace").exists()
    assert not (plugin_root / "hooks" / "__pycache__").exists()


def test_only_single_plugin_directory_exists():
    plugin = _plugin_definition()
    assert sorted(path.name for path in PLUGINS_DIR.iterdir()) == [Path(plugin["directory"]).name]