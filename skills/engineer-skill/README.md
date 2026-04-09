# Engineer Skill

Improve agent skills by validating structure, optimizing YAML frontmatter for triggering accuracy, and refining SKILL.md prompt content for reliable agent behavior.

## Overview

This skill treats skill improvement as two separate, composable concerns:

1. **Frontmatter optimization** — improving the YAML metadata (especially the description field) that controls when agents discover and invoke the skill.
2. **Body content optimization** — improving the markdown instructions that control what agents do after triggering, including extracting deterministic logic to scripts and domain knowledge to reference files.

## Directory structure

```
engineer-skill/
├── SKILL.md                                  # Skill instructions
├── README.md                                 # This file
├── scripts/
│   ├── __init__.py
│   ├── validate_skill.py                     # Spec compliance validator
│   └── analyze_skill_body.py                 # Body analysis and recommendations
├── references/
│   ├── frontmatter-optimization.md           # Frontmatter improvement guide
│   ├── prompt-content-optimization.md        # Body content improvement guide
│   └── skill-structure-spec.md               # Directory layout spec
├── assets/                                   # Reserved for templates
└── evals/
    └── evals.json                            # Evaluation manifest
```

## Scripts

### validate_skill.py

Validates a skill directory against the agentskills.io specification. Checks frontmatter fields, naming conventions, directory structure, cross-skill references, and description quality.

```bash
python scripts/validate_skill.py <skill-path>
python scripts/validate_skill.py <skill-path> --json
```

### analyze_skill_body.py

Analyzes the SKILL.md body and produces actionable improvement recommendations. Identifies oversized sections, deterministic content that should be scripts, and reference extraction candidates.

```bash
python scripts/analyze_skill_body.py <skill-path>
python scripts/analyze_skill_body.py <skill-path> --json
```
