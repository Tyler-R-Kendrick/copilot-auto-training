# Agent Skills Structure Specification

Read this file when you need the complete directory layout and file conventions for a well-formed agent skill.

## Directory layout

```
skill-name/
├── SKILL.md          # Required: frontmatter + instructions
├── README.md         # Optional: human-facing documentation
├── scripts/          # Optional: executable code for deterministic tasks
│   ├── __init__.py
│   └── *.py
├── references/       # Optional: docs loaded into context as needed
│   └── *.md
├── assets/           # Optional: templates, icons, output artifacts
│   └── *
└── evals/            # Optional: evaluation manifest and test files
    ├── evals.json
    └── files/
```

## SKILL.md format

The file must start with YAML frontmatter delimited by `---`:

```yaml
---
name: skill-name
description: What the skill does and when to use it.
license: MIT
compatibility: Python 3.11+
metadata:
  author: team-name
  version: "0.1.0"
---
```

The markdown body follows the closing `---` delimiter.

## Naming conventions

- Directory name must match the `name` frontmatter field exactly.
- Names use kebab-case: lowercase letters, digits, hyphens.
- No leading, trailing, or consecutive hyphens.
- Maximum 64 characters.

## Cross-skill references

Skills must not reference other agent skills by name in their SKILL.md body. Each skill is self-contained. If functionality from another skill is needed, the agent orchestrator handles routing between skills.

## Eval manifest format

The `evals/evals.json` file follows this structure:

```json
{
  "skill_name": "skill-name",
  "evals": [
    {
      "id": 1,
      "prompt": "A realistic user request",
      "expected_output": "Description of a successful response",
      "assertions": ["Objectively verifiable statement"],
      "files": ["evals/files/sample.txt"]
    }
  ]
}
```

- `prompt`: reads like an actual user request, not a label.
- `expected_output`: describes success characteristics, not brittle exact text.
- `assertions`: objectively verifiable predicates only.
- `files`: paths relative to the skill root.

## Scripts conventions

- Scripts in `scripts/` should be runnable with `python -m scripts.<name>` from the skill root, or directly with `python scripts/<name>.py`.
- Include `__init__.py` for package-style imports.
- Scripts handle deterministic work that would otherwise be specified as prose in the SKILL.md body.
- Test scripts with standard pytest conventions.
