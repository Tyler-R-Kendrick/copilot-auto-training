"""
conftest.py — install lightweight stubs for external packages
(agentlightning, openai) before any test module imports run_optimize.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

# ---------------------------------------------------------------------------
# agentlightning stub
# ---------------------------------------------------------------------------

_agl = types.ModuleType("agentlightning")


class _PromptTemplate:
    def __init__(self, template: str, engine: str = "f-string"):
        self.template = template
        self.engine = engine


class _APO:
    """Minimal APO stub whose behaviour tests can override per-test."""

    # Class-level knob: controls how many candidates _Trainer.fit() produces.
    # Tests that need to exercise the multi-candidate path can monkeypatch this
    # value (e.g. ``monkeypatch.setattr(agl.APO, "_num_candidates", 3)``).
    # Defaults to 1 to exercise the single-candidate → variant fallback path.
    _num_candidates: int = 1

    def __init__(self, client, *, beam_rounds=3, beam_width=4, branch_factor=4,
                 gradient_batch_size=4, val_batch_size=16):
        self.beam_rounds = beam_rounds
        self.beam_width = beam_width
        self.branch_factor = branch_factor
        self._best_prompt: _PromptTemplate | None = None
        self._candidates: list[_PromptTemplate] = []

    def get_best_prompt(self) -> _PromptTemplate | None:
        return self._best_prompt

    def get_candidates(self) -> list[_PromptTemplate]:
        return self._candidates


class _Trainer:
    def __init__(self, *, algorithm, n_runners, tracer, initial_resources, adapter):
        self.algorithm = algorithm
        self.n_runners = n_runners
        self.initial_resources = initial_resources
        self._dev_called = False
        self._fit_called = False

    def dev(self, *, agent, train_dataset, val_dataset):
        self._dev_called = True

    def fit(self, *, agent, train_dataset, val_dataset):
        self._fit_called = True
        # Simulate a successful optimisation: produce _num_candidates candidates.
        # The first/best has the "<!-- optimized -->" marker; additional candidates
        # are labelled so tests can assert which path was taken.
        if isinstance(self.algorithm, _APO):
            seed = list(self.initial_resources.values())[0]
            n = self.algorithm._num_candidates
            candidates = [
                _PromptTemplate(
                    template=seed.template + "\n<!-- optimized -->" + (
                        f"\n<!-- candidate {i} -->" if i > 0 else ""
                    ),
                    engine=seed.engine,
                )
                for i in range(n)
            ]
            self.algorithm._candidates = candidates
            # Simulate a successful optimisation: append a marker so tests can
            # verify the output file contains the "optimized" result.
            self.algorithm._best_prompt = candidates[0]


class _OtelTracer:
    pass


class _TraceToMessages:
    pass


def _rollout(fn):
    """Passthrough decorator — preserve the original async function."""
    return fn


_agl.PromptTemplate = _PromptTemplate
_agl.APO = _APO
_agl.Trainer = _Trainer
_agl.OtelTracer = _OtelTracer
_agl.TraceToMessages = _TraceToMessages
_agl.rollout = _rollout

sys.modules["agentlightning"] = _agl

# ---------------------------------------------------------------------------
# openai stub
# ---------------------------------------------------------------------------

_openai = types.ModuleType("openai")


class _AsyncOpenAI:
    pass


_openai.AsyncOpenAI = _AsyncOpenAI

sys.modules["openai"] = _openai

# ---------------------------------------------------------------------------
# Make skills/optimize/scripts/ importable from tests/
# ---------------------------------------------------------------------------

_scripts_dir = Path(__file__).resolve().parent.parent / "skills" / "optimize" / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))
