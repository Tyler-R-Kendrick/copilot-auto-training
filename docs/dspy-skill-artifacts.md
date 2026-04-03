# DSPy to `SKILL.md` for Agent Skills

Use this pattern when you want DSPy to optimize skill instructions but still check a stable Markdown artifact into an agent-skills repository.

## What is realistic

DSPy works best when you describe behavior as code and let an optimizer improve the prompting strategy around that code. In practice, that usually means:

1. Define a DSPy signature or module for the skill behavior.
2. Compile it with an optimizer such as `MIPROv2`.
3. Save the optimized program for reuse or debugging.
4. Export the optimized instructions into a checked-in `SKILL.md`.

Treat DSPy as the optimizer and your exporter as the packaging step.

## Recommended approach

Prefer instruction-only optimization when the goal is a clean `SKILL.md` artifact.

Why:

- optimizing both instructions and demos can improve runtime quality, but often produces a less reusable standalone skill prompt
- setting demo counts to zero biases the result toward a single instruction artifact
- deterministic templating gives you cleaner diffs and a more stable repository contract

## Suggested layout

```text
agent-skills/
  my-skill/
    SKILL.md
    export_skill_prompt.py
    trainset.jsonl
    evals/
```

## Minimal DSPy pattern

```python
from pathlib import Path

import dspy
from dspy.teleprompt import MIPROv2


class SkillWriter(dspy.Signature):
    """Generate the final instructions for an agent skill."""

    skill_name = dspy.InputField(desc="Name of the skill")
    skill_description = dspy.InputField(desc="What the skill should do")
    operating_constraints = dspy.InputField(desc="Hard rules and boundaries")
    inputs_available = dspy.InputField(desc="Tools, files, and context available")
    desired_outputs = dspy.InputField(desc="What successful execution should produce")
    draft_notes = dspy.InputField(desc="Extra implementation notes")

    instruction_body = dspy.OutputField(
        desc="Instruction body that will be wrapped into a deterministic SKILL.md template"
    )


class SkillProgram(dspy.Module):
    def __init__(self):
        super().__init__()
        self.write_skill = dspy.Predict(SkillWriter)

    def forward(
        self,
        skill_name,
        skill_description,
        operating_constraints,
        inputs_available,
        desired_outputs,
        draft_notes,
    ):
        return self.write_skill(
            skill_name=skill_name,
            skill_description=skill_description,
            operating_constraints=operating_constraints,
            inputs_available=inputs_available,
            desired_outputs=desired_outputs,
            draft_notes=draft_notes,
        )


def render_skill_md(name: str, description: str, instruction_body: str) -> str:
    return f"""---
name: {name}
description: {description}
---

## When to use
Use this skill when the request matches the description and the required inputs are available.

## Instructions
{instruction_body.strip()}

## Output
Return the requested artifact or result in the format requested by the user.
"""


def skill_metric(example, pred, trace=None):
    text = pred.instruction_body.lower()
    checks = [
        "do not" in text,
        "return" in text,
        "when" in text or "use this skill" in text,
        len(pred.instruction_body.strip()) > 300,
    ]
    return sum(checks) / len(checks)


lm = dspy.LM("openai/gpt-4o-mini")
dspy.configure(lm=lm)

program = SkillProgram()
trainset = [
    dspy.Example(
        skill_name="summarize-spec",
        skill_description="Summarize product specification docs into implementation notes.",
        operating_constraints="Do not invent requirements. Cite exact source passages when available.",
        inputs_available="Markdown specs, PRDs, architecture notes.",
        desired_outputs="A concise implementation summary and open questions.",
        draft_notes="Favor actionable sections over prose.",
        instruction_body="""Read the provided source material carefully.
Extract requirements, constraints, risks, and open questions.
Do not invent missing requirements.
Call out ambiguity explicitly.""",
    ).with_inputs(
        "skill_name",
        "skill_description",
        "operating_constraints",
        "inputs_available",
        "desired_outputs",
        "draft_notes",
    ),
]

optimizer = MIPROv2(metric=skill_metric, auto="light")
optimized_program = optimizer.compile(
    student=program.deepcopy(),
    trainset=trainset,
    max_bootstrapped_demos=0,
    max_labeled_demos=0,
)

optimized_program.save("skill_program_optimized.json")

result = optimized_program(
    skill_name="agent-skills-prompt-author",
    skill_description="Generate and refine SKILL.md files for agent skills.",
    operating_constraints=(
        "Keep instructions explicit and testable. "
        "Do not claim tools or files that are not actually available."
    ),
    inputs_available=(
        "A task description, optional examples, optional repo context, "
        "and optional evaluation criteria."
    ),
    desired_outputs="A production-ready SKILL.md with YAML front matter and clear instructions.",
    draft_notes="Optimize for reliability, low ambiguity, and straightforward artifact generation.",
)

final_md = render_skill_md(
    name="agent-skills-prompt-author",
    description="Generate and refine SKILL.md files for agent skills.",
    instruction_body=result.instruction_body,
)

Path("SKILL.md").write_text(final_md, encoding="utf-8")
print("Wrote SKILL.md")
```

## Why the export layer matters

Asking DSPy to generate the full file can work, but wrapping the optimized body in a deterministic renderer is usually better when your runtime expects a stable `SKILL.md` contract.

Use full-file generation when:

- formatting variance is acceptable
- your evals strongly enforce the expected shape
- you want maximum prompt flexibility

Use deterministic wrapping when:

- you want stable front matter and section layout
- you care about readable diffs in Git
- your runtime expects a predictable skill structure

## How to evaluate the generated skill

Check for:

- valid YAML front matter
- explicit trigger conditions
- concrete instructions
- a clear output contract
- forbidden behaviors and boundary conditions
- compatibility with the actual tools and files available at runtime

If you already maintain downstream skill evals, prefer those over string-only checks.

## How this fits this repository

This repository's checked-in artifact should still be the final Markdown prompt file. If you use DSPy outside the built-in Agent Lightning workflow, keep the export step separate and commit the resulting `SKILL.md`, evals, and datasets like any other prompt artifact in this repo.
