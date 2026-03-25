from __future__ import annotations

from agent_framework import SkillsProvider

from optimize_skill import optimize_skill


def build_skills_provider() -> SkillsProvider:
    return SkillsProvider(
        skills=[optimize_skill],
        require_script_approval=True,
        instruction_template=(
            "You have skills available:\n{skills}\n\n"
            "{runner_instructions}\n\n"
            "If the user starts the message with /optimize, load the optimize skill. "
            "Prefer APO for markdown prompt optimization."
        ),
    )


if __name__ == "__main__":
    provider = build_skills_provider()
    provider.run()
