---
name: trainer-research
description: Research public datasets, benchmarks, documentation, and source material for official skill eval cases. Use this skill whenever a prompt or skill needs grounded public examples, authoritative dataset references, or a primary-source brief before synthesis or optimization.
license: MIT
compatibility: Requires Python 3.11+. Produces standalone research briefs, ranked source shortlists, and eval-authoring notes for this repository.
metadata:
  author: Tyler Kendrick
  version: "0.1.0"

---

# Research

Use this skill to research source material and produce a standalone research dossier before generating official skill eval cases.

Work primary-source-first. Resolve the task boundary and missing constraints before searching. End with approved sources and mapping notes, not guessed eval rows.

## When to use this skill

- The optimizer or evaluation workflow needs grounded eval cases, but no suitable local source material exists yet.
- The user wants grounded public examples instead of purely simulated rows.
- The agent needs a ranked shortlist of public datasets, benchmarks, or documentation sources that match a prompt task.
- The user needs explicit judgment about source quality, data reliability, annotation quality, licensing, provenance, or leakage risk before authoring eval data.
- The workflow needs to know whether no acceptable public source exists, so synthesis should stop instead of guessing.

If the source material is already known and the job is to convert it into eval rows, use `trainer-synthesize` instead.

## Inputs

- `prompt_file`: target markdown prompt
- `task_description`: short description of the real task the prompt should solve
- `scoring_rule`: expected answer format or evaluation rule
- Optional constraints such as domain, language, geography or jurisdiction, recency, licensing, privacy, label taxonomy, or excluded source types

## Resolve Before Searching

Resolve these inputs before recommending sources:

- prompt interface and placeholders
- real task boundary and evaluation target
- expected answer format or scoring rule
- domain, language, and jurisdiction constraints
- licensing or privacy limits
- recency and version expectations

If any of these materially affect source selection and are missing, ask first. Do not guess them from context.

## Output

Return a standalone research brief that includes:

1. `Target layout`: the derived `evals/evals.json` path and any `evals/files/` assets implied by the prompt
2. `Query plan`: a primary-source-first search plan tied to the task and scoring rule
3. `Approved sources`: a ranked shortlist with authority, provenance, licensing, fit, and risk notes
4. `Rejected candidates`: weak or incompatible sources and why they were rejected
5. `Mapping notes`: how approved sources can become prompt rows, expected outputs, optional files, and objective assertions
6. `Unresolved gaps`: anything still blocking safe synthesis, including a recommendation to stop if no source clears the approval bar

If the inputs are already complete, say the plan is satisfied and proceed.

## Research Plan

Before searching, build a short plan with these sections:

1. `Target layout`: derived eval paths, optional files directory, and any workspace directory implied by the prompt file
2. `Observed interface`: prompt placeholders and visible fields that source material must support
3. `Research questions`: what needs to be learned to ground eval authoring for this task
4. `Approval bar`: the evidence each approved source must provide
5. `Missing inputs`: any remaining blockers that need to be elicited

Use the plan to constrain the search. Do not collect sources first and rationalize them later.

## Source approval bar

Approve a source only if it clears the relevant checks for this task:

- accountable maintainer, publisher, or standards body
- traceable data origin, schema, and label definitions
- evaluation rules, annotation guide, or benchmark protocol from the owner when available
- explicit license or reuse terms
- stable version, date, or release identifier
- acceptable contamination, leakage, privacy, and bias risk for authored eval use

If a candidate fails the bar, keep it only as a rejected lead, not an approved recommendation.

## Process

1. Inspect the prompt placeholders and derive the official `evals/evals.json` target path plus any `evals/files/` assets.
2. Build the research plan before searching. Identify the task boundary, required evidence, and any missing constraints.
3. If key constraints are missing, ask for them before continuing.
4. Build research queries that match the task, scoring rule, and prompt-visible fields, starting with official maintainers, benchmark owners, dataset cards, annotation guides, standards bodies, and original papers.
5. Apply academic-style source triage: prefer primary sources first, use credible secondary sources only to discover or verify primary material, and reject derivative mirrors, listicles, or unverifiable blog summaries.
6. Judge each candidate source for authority, provenance, annotation quality, task fit, recency, version stability, licensing, contamination risk, and reuse constraints.
7. Rank the approved sources, record rejection reasons for weak candidates, and summarize the evidence behind each ranking.
8. Map approved source fields into realistic prompt rows, expected outputs, optional input files, and objective assertions, noting constraints or unresolved gaps.
9. If no candidate clears the approval bar, say so explicitly and explain what evidence is missing instead of forcing a recommendation.
10. Deliver the completed research brief as a self-contained artifact that another workflow can hand to `trainer-synthesize` or use directly.

## Source hierarchy

Prefer sources in this order:

1. Official primary sources: benchmark owner sites, maintainer repositories, dataset cards, annotation guidelines, standards bodies, and original papers.
2. High-credibility secondary sources: trusted documentation mirrors, library docs maintained by the source owner, or peer-reviewed comparative surveys that cite the primary source.
3. Tertiary summaries: blog posts, tutorials, scraped mirrors, SEO roundups, or anonymous aggregators. Treat these as discovery hints only and do not rely on them when a primary source is available.

## Research standards

- Prefer official primary sources even when secondary summaries are easier to read.
- Verify that labels, schemas, and evaluation rules come from the source owner whenever possible.
- Record version, publication date, and licensing details before recommending a source.
- Note sampling bias, benchmark contamination risk, train-test leakage risk, and label ambiguity when they could affect eval quality.
- Reject sources that cannot be traced to an accountable maintainer or publication.
- Separate research from synthesis: stop at mapping notes unless the user explicitly asks to author eval rows.

## Elicit If Missing

Ask for missing details that change which public sources are acceptable, such as:

- target domain terminology or user population
- language or locale coverage
- licensing or commercial-use requirements
- privacy or data-handling restrictions
- label taxonomy, class balance needs, or edge-case priorities
- acceptable publication date range or version floor

If none are missing, say so explicitly and continue.

## References and helper

- Read `references/dataset-research.md` when you need a compact triage checklist.
- Use `scripts/run_research.py` to derive eval targets, placeholders, and a research-brief scaffold when deterministic setup will save time.

## Naming rationale

`research` is explicit, standard, and narrow enough to separate source discovery from later synthesis and conversion.