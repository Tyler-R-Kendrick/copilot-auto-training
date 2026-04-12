# Engineering Review: trainer-train-skill

## Overview

`trainer-train-skill` is a specialization of the trainer-train orchestration loop targeting `SKILL.md` files in the agentskills.io format. It owns workspace initialization, two-concern separation (frontmatter vs. body), spec-compliance validation, and write-back gating for skill-type targets.

## Strengths

1. **Two-concern separation.** Separating frontmatter (triggering) from body (execution) is architecturally sound and prevents the optimizer from confusing these two independent concerns.
2. **Spec-compliance gate.** Running spec validation before optimization (not just before write-back) gives the optimizer accurate context about what is already broken.
3. **Name preservation rule.** Explicitly requiring the `name` field to remain unchanged prevents a common regression where optimization renames a skill mid-loop.
4. **Progressive disclosure enforcement.** The 500-line body limit and reference extraction requirement are well-defined and testable.

## Gaps and recommendations

1. **Frontmatter vs. body priority decision.** Step 8 says "pass the improvement focus" but does not specify what happens when both frontmatter and body need improvement and the caller did not prioritize. Add a default: fix spec violations first, then frontmatter, then body.
2. **evals/evals.json realism check.** Step 5 mentions checking that `evals.json` has realistic prompts but does not define what "realistic" means in this context. Specify at minimum: prompts must read like actual user requests, not label strings.
3. **Cross-reference isolation.** The skill references `evals/evals.json` and `references/skill-loop-contract.md` but does not warn that SKILL.md body text must not name other skill directories. Add a note that the spec-compliance check includes this constraint.
4. **Election criteria for skill targets.** Define a preference rule for the elector stage: prefer the candidate with the highest llm_judge score; break ties by smallest frontmatter change when triggering was the primary concern.

## Verdict

Ready for optimization loop. Priority improvements: (1) default priority ordering when both concerns need work, (2) evals realism definition, (3) election preference rule for skill targets.
