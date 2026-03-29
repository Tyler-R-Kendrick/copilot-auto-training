---
name: trainer-research
description: Research public datasets, benchmarks, documentation, and source material for official skill eval cases. Use this skill whenever the user asks to find public examples, benchmark tasks, dataset sources, or grounded references for a prompt or skill, especially before generating or converting `evals/evals.json`.
license: MIT
compatibility: Requires Python 3.11+. Produces standalone research briefs, ranked source shortlists, and eval-authoring notes for this repository.
metadata:
  author: Tyler Kendrick
  version: "0.1.0"

---

# Research

Use this skill to research source material and produce a standalone research dossier before generating official skill eval cases.

## When to use this skill

- The optimizer or evaluation workflow needs grounded eval cases, but no suitable local source material exists yet.
- The user wants grounded public examples instead of purely simulated rows.
- The agent needs a ranked shortlist of public datasets, benchmarks, or documentation sources that match a prompt task.
- The user needs explicit judgment about source quality, data reliability, annotation quality, licensing, or provenance before authoring eval data.

## Inputs

- `prompt_file`: target markdown prompt
- `task_description`: short description of the real task the prompt should solve
- `scoring_rule`: expected answer format or evaluation rule

## Output

Return a standalone research brief that includes:

- the derived `evals/evals.json` target path and any `evals/files/` assets implied by the prompt
- a primary-source-first query plan
- a ranked source shortlist with authority, provenance, licensing, and fit notes
- rejected candidates and the reason they were rejected
- mapping notes from approved sources into prompt rows, expected outputs, optional files, and objective assertions

## Process

1. Inspect the prompt placeholders and derive the official `evals/evals.json` target path plus any `evals/files/` assets.
2. Build research queries that match the task, answer format, and prompt-visible fields, starting with official maintainers, benchmark owners, dataset cards, annotation guides, standards bodies, and original papers.
3. Apply academic-style source triage: prefer primary sources first, use credible secondary sources only to discover or verify primary material, and reject derivative mirrors, listicles, or unverifiable blog summaries.
4. Judge each candidate source for authority, provenance, annotation quality, task fit, recency, version stability, licensing, and leakage risk.
5. Rank the approved sources, record the rejection reasons for weak candidates, and summarize the evidence behind each ranking.
6. Map the approved source fields into realistic prompt rows, expected outputs, optional input files, and objective assertions, noting any constraints or unresolved gaps.
7. Deliver the completed research brief as a self-contained artifact that another workflow could use without requiring this skill to call any other skill.

## Source hierarchy

Prefer sources in this order:

1. Official primary sources: benchmark owner sites, maintainer repositories, dataset cards, annotation guidelines, standards bodies, and original papers.
2. High-credibility secondary sources: trusted documentation mirrors, library docs maintained by the source owner, or peer-reviewed comparative surveys that cite the primary source.
3. Tertiary summaries: blog posts, tutorials, scraped mirrors, SEO roundups, or anonymous aggregators. Treat these as discovery hints only and do not rely on them when a primary source is available.

## Research standards

- Prefer official primary sources even when secondary summaries are easier to read.
- Verify that labels, schemas, and evaluation rules come from the source owner whenever possible.
- Record version, publication date, and licensing details before recommending a source.
- Note sampling bias, benchmark contamination risk, and label ambiguity when they could affect eval quality.
- Reject sources that cannot be traced to an accountable maintainer or publication.

## Naming rationale

`research` is explicit, standard, and narrow enough to separate source discovery from later synthesis and conversion.