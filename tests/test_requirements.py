from __future__ import annotations

from pathlib import Path


def test_requirements_include_poml_for_agentlightning_apo_runtime():
    requirements = Path("requirements.txt").read_text(encoding="utf-8").splitlines()
    normalized = [line.strip().lower() for line in requirements if line.strip() and not line.startswith("#")]
    assert any(line.startswith("poml") for line in normalized)