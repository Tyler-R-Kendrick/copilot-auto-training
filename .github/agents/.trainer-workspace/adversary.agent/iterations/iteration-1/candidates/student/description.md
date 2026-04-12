## Student Candidate Description

The student candidate applies two targeted improvements to the optimized prompt:

1. **Score format alignment**: `predicted-judge-response.md` now requires scores in `{"score": <float>}` format, matching the judge's actual output format and enabling machine-comparable diff between predicted and actual judge scores.
2. **Numeric comparison in step 4**: Approach step 4 now requires stating predicted judge scores for both the exploit candidate and the student candidate using `{"score": <float>}` format, replacing vague ranking language with anchored numeric comparison.

All other sections (constraints, evidence order, focus areas, other approach steps, output format, frontmatter) are unchanged from the trainer-produced optimized candidate.
