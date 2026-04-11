# Collaboration contract

## Ownership

- The trainer orchestrator owns workspace coordination, iteration planning, stage sequencing, and candidate application.
- Research specialists own public-source discovery, source triage, and blocker reporting.
- Review specialists own critique of supplied artifacts and next-step steering.
- Revision specialists own bounded candidate updates and their reasoning.
- Evaluation specialists own scoring of outputs or trajectories from the supplied evidence.
- Stress-test specialists own exploit attempts and robustness probes before finalization.

## Steering artifacts

Publish iteration-scoped steering under:

`iterations/iteration-N/steering/<agent>/turn-N/STEERING.md`

Keep rolling per-agent summaries under:

`iterations/iteration-N/steering/<agent>/summary.md`

Treat `required_artifacts.latest_iteration_dir` plus the active iteration's `steering/`, `optimize/`, `election/`, and `validation/` outputs as the iteration steering bundle.

Treat workspace-root `decision.md`, optional `benchmark.json`, optional `benchmark.md`, and optional `review.html` as the cross-run rollup steering bundle.

## Candidate bundles

Before review or selection, stage candidate bundles under:

- `candidates/original/`
- `candidates/student/`
- `candidates/adversary/`

Prefer a `candidates.json` manifest that maps each candidate source to:

- the candidate artifact
- the description artifact
- the predicted judge response artifact
- the reflection artifact
- any selection notes

If an adversarial candidate exposes a credible exploit, add follow-up steering that blocks the pattern in later turns.
If the old candidate wins, add follow-up steering that explains the regression before another revision round.
