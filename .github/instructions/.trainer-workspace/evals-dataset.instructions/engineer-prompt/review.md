# Engineer-Prompt Review: evals-dataset.instructions.md

## Target Goal

Improve `evals-dataset.instructions.md` so it guides correct, consistent authoring of skill eval manifests (`evals/evals.json`). The file should produce eval cases that are realistic, well-structured, correctly scored, and free of common authoring errors.

## Current State Analysis

The current file contains 6 bullet rules covering:
1. Manifest root shape (`skill_name` + `evals` array)
2. Prompt realism guidance
3. `expected_output` usage
4. `files` path conventions
5. `assertions` usage
6. Coverage expansion cadence

**Gaps identified:**
- No worked examples showing a good vs bad eval case
- No guidance on required vs optional fields per eval row
- No definition of what `assertions` look like structurally
- No guidance on `scoring` field values or `judge_mode` selection
- No explicit statement of forbidden patterns (e.g., using shorthand prompts, brittle expected_output matching)
- No guidance on `criteria` field for `llm_judge` rows
- Missing: how to handle file-dependent evals (`files` key usage)

## Likely Failure Modes

1. **Missing field guidance**: Authors omit required fields (`skill_name`, `prompt`, `expected_output`) or use wrong keys
2. **Unclear assertion rules**: Authors write subjective assertions or assertions that can't be verified programmatically
3. **Ambiguous scoring labels**: Authors pick `deterministic` when `llm_judge` is needed, or leave `scoring` out entirely
4. **Poor prompt phrasing**: Prompts read like test labels ("Test case 1: add eval") rather than natural user requests
5. **Brittle expected_output**: Authors write exact match strings that fail on minor variations
6. **Wrong files paths**: Authors use absolute paths or wrong relative roots

## Dataset Gaps

- No worked examples of a complete, correct eval row in the instruction text
- No counter-examples showing what NOT to do
- No example of the full JSON structure with all optional fields populated

## Optimization Hypothesis

The instruction file can be improved by:
1. Adding a concrete minimal example of a correct eval case
2. Clarifying assertion structure and criteria for objective vs subjective checks
3. Specifying required vs optional fields explicitly
4. Adding a note about `scoring` field values and when to use each
5. Tightening the forbidden-pattern list (shorthand prompts, absolute paths, brittle match text)

## Validation Plan

Run `python -m pytest -q` after applying changes to ensure no tests are broken.
The instruction file itself is not directly tested, so validation focuses on ensuring no file syntax errors and no regressions in the broader test suite.

## Recommended Improvement Areas

- Add a minimal JSON example block showing a complete, correct eval case
- Add a note: "Every eval row must include `prompt` and `expected_output`; `assertions`, `files`, and `scoring` are optional but follow specific conventions when present"
- Clarify: assertions must be string predicates that can be checked programmatically or by a judge without ambiguity
- Add: `scoring` supported values are `deterministic`, `custom`, `llm_judge`; default when omitted is implementation-defined
- Add: when `files` is present, paths must be relative to the eval manifest directory
