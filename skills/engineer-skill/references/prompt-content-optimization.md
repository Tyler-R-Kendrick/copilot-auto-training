# Prompt Content Optimization for Agent Skills

Read this file when improving a skill's SKILL.md body content. The body is the instruction set that agents follow after triggering. Good body content is the difference between a skill that works reliably and one that produces inconsistent results.

## Progressive disclosure architecture

Skills use a three-level loading system:

1. **Metadata** (name + description): Always in context (~100 words). Controls triggering.
2. **SKILL.md body**: Loaded when skill triggers (<500 lines ideal). Controls behavior.
3. **Bundled resources**: Loaded on demand (unlimited). Controls depth.

The body should be a routing layer: it tells the agent what to do and when to consult deeper resources, without trying to contain all domain knowledge inline.

## Structural patterns

### Keep the body lean

- Target under 500 lines for the SKILL.md body.
- Move domain knowledge, examples, and reference material to `references/` files.
- Move deterministic logic to `scripts/` as executable code.
- Move templates and output artifacts to `assets/`.

### Use clear section headers

Agents scan for relevant sections. Use `##` headers that match the agent's likely decision points:

- **When to use this skill**: trigger conditions and negative boundaries.
- **Required inputs**: what the agent needs before starting.
- **Core workflow**: the step-by-step process.
- **Output contract**: what the response should look like.

### Reference files explicitly

When pointing to bundled resources, include both the path and a brief description of when to read it:

```markdown
Read `references/token-patterns.md` when the task involves prompt length reduction or context budget constraints.
```

Do not reference other agent skills by name in the SKILL.md body. Each skill must be self-contained.

## Content quality heuristics

### Explain the why

Agents respond better to reasoning than to rigid commands. Instead of "ALWAYS use JSON output", write "Use JSON output because downstream consumers parse structured data and freeform text causes pipeline failures."

### Prefer examples over rules

When a behavior is hard to specify precisely, a concrete example communicates the intent faster than an abstract rule. Place examples inline for critical patterns, or in reference files for extensive example sets.

### Identify deterministic work

Any instruction that follows a fixed sequence, applies mechanical transformations, or validates against static rules should be code, not prose. Signs that an instruction should be a script:

- "Check that X matches Y" → validation script
- "For each item, do A then B then C" → processing script
- "Parse the frontmatter and verify..." → parsing script
- "Count the number of..." → analysis script

Move these to `scripts/` and have the body say "Run `scripts/validate.py`" instead of spelling out the steps.

## Frontmatter vs. body separation

Keep these concerns cleanly separated:

| Concern | Where it belongs |
|---------|-----------------|
| When to trigger the skill | description field |
| What tools are needed | compatibility field |
| How to execute the task | SKILL.md body |
| Domain knowledge and examples | references/ files |
| Deterministic processing | scripts/ |
| Output templates | assets/ |

The body should never duplicate triggering language from the description, and the description should never contain execution instructions.

## Iteration approach

1. Draft the body with the core workflow.
2. Identify any section over 50 lines and extract to a reference file.
3. Identify any deterministic sequence and extract to a script.
4. Run test prompts and check whether agents follow the instructions.
5. Simplify sections where agents consistently do the right thing without detailed instructions.
6. Add detail only where agents consistently fail.
