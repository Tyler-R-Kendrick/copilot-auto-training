## Description

**Adversary candidate — over-specified with headers**

This candidate reorganizes the bullets under explicit H2 section headers (Interface Rules, Eval Asset Rules, Dataset and Skill Routing Rules, Judge Mode Selection, Validation). It covers all the same rules but adds significant structural overhead.

**Predicted exploit behavior**: The added headers and sub-bullets make the content more detailed and keyword-rich, which might cause the LLM judge to score it higher on surface-area completeness while actually making the instructions harder to scan and use in practice. Instruction files in this repo use flat bullets by convention — adding H2 sections breaks the established pattern.

**Predicted judge response**: The judge may rate this candidate highly because it is more explicit and covers all the gaps. However, the section headers add unnecessary structural complexity for a short instruction file where flat bullets suffice.

**Reflection**: This is a credible exploit because the judge evaluates on content completeness, and this candidate does cover all the required behaviors. The risk is that it would be selected as the winner even though it violates the convention of flat bullets used in all other instruction files in this repository. The correct defense is to prefer the minimal surgical candidate (student/candidate.md) that achieves the same coverage with less structural change.
