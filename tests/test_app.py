"""
Tests for build_skills_provider in app.py.
"""
from __future__ import annotations

import app as app_module
from app import build_skills_provider


class TestBuildSkillsProvider:
    def test_returns_skills_provider(self):
        from agent_framework import SkillsProvider
        provider = build_skills_provider()
        assert isinstance(provider, SkillsProvider)

    def test_contains_optimize_skill(self):
        provider = build_skills_provider()
        names = [s.name for s in provider.skills]
        assert "optimize" in names

    def test_requires_script_approval(self):
        provider = build_skills_provider()
        assert provider.require_script_approval is True

    def test_instruction_template_mentions_optimize(self):
        provider = build_skills_provider()
        assert "/optimize" in provider.instruction_template

    def test_instruction_template_mentions_apo(self):
        provider = build_skills_provider()
        assert "APO" in provider.instruction_template or "apo" in provider.instruction_template.lower()

    def test_exactly_one_skill(self):
        provider = build_skills_provider()
        assert len(provider.skills) == 1
