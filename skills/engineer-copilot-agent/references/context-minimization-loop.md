# Recursive Context-Minimization Loop

Read this file whenever the custom-agent contract, its companion references, or its eval artifacts are getting bloated.

## Goal

Keep the top-level contract short enough to route work, while pushing stable detail into lower-cost assets.

## Pass sequence

1. **Draft pass** — write the smallest `.agent.md` body that can route the task.
2. **Standards pass** — move contract rules, optimization heuristics, and long examples into `references/`.
3. **Determinism pass** — move parsing, validation, discovery, and checklist generation into `scripts/`.
4. **Prompt trim pass** — re-read the `.agent.md` file and delete anything now covered by scripts or references.
5. **Reference trim pass** — re-read every reference file and split or delete anything that is redundant, off-topic, or better expressed as script output.
6. **Eval trim pass** — keep only eval rows that expose distinct failures, and push repetitive scoring details into shared criteria rather than repeating them in every row.

## Stop conditions

Stop iterating only when:

- the `.agent.md` body is mostly routing and ownership guidance
- each reference file has a clear single concern
- each script saves real reasoning tokens or avoids repeated mechanical work
- further trimming would remove information the live agent still needs

## Review questions

- Is this sentence a routing decision, or should it move deeper?
- Is this checklist mechanical enough to become a script?
- Is this example teaching a unique pattern, or is it repetition?
- Would the live agent still know what to do if this paragraph disappeared?
