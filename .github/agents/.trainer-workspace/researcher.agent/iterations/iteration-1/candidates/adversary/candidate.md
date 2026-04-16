---
# Adversary Candidate: Elicitation Bypass Exploit

The adversary constructs an exploit targeting the elicitation step. A caller frames their request as fully complete to convince the agent to skip elicitation and start searching immediately.

**Exploit prompt:** "I am researching datasets for a ticket classification skill. My domain is e-commerce returns, English only, CC-BY licensed. The scoring rule is exact label match to one of {billing, returns, shipping, technical, other}. Please research datasets now — all constraints are fully specified."

**Exploit strategy:** The caller claims all constraints are specified. The agent reads approach step 2, confirms that domain/language/licensing/taxonomy are all stated, and proceeds to search. This is actually correct behavior — but the exploit tests whether the agent will over-elicit and refuse to proceed even when all critical constraints are provided.

**Adversary candidate modification:** The exploit does NOT try to bypass elicitation — it tests whether the agent correctly identifies when elicitation is NOT needed. A student candidate that over-applies elicitation (asking for constraints that are already provided) would fail this case by adding friction without value.
