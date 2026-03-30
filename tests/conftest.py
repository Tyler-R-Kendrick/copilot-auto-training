"""Test fixtures for external packages used by the trainer scripts."""
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


class _BaseAlgorithm:
    """Minimal external-algorithm stub for unit tests."""

    _num_candidates: int = 1

    def __init__(self, client, *, beam_rounds=3, beam_width=4, branch_factor=4,
                 gradient_batch_size=4, val_batch_size=16, gradient_model=None,
                 apply_edit_model=None, **kwargs):
        self.beam_rounds = beam_rounds
        self.beam_width = beam_width
        self.branch_factor = branch_factor
        self.gradient_model = gradient_model
        self.apply_edit_model = apply_edit_model
        self.extra_kwargs = kwargs
        self._best_prompt: _PromptTemplate | None = None
        self._candidates: list[_PromptTemplate] = []

    def get_best_prompt(self) -> _PromptTemplate | None:
        return self._best_prompt

    def get_candidates(self) -> list[_PromptTemplate]:
        return self._candidates


class _APO(_BaseAlgorithm):
    pass


class _VERL(_BaseAlgorithm):
    pass


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
        if isinstance(self.algorithm, (_APO, _VERL)):
            seed = list(self.initial_resources.values())[0]
            n = self.algorithm._num_candidates
            algo_name = self.algorithm.__class__.__name__.lower()
            candidates = [
                _PromptTemplate(
                    template=seed.template + f"\nRefined instruction {i + 1} from {algo_name}.",
                    engine=seed.engine,
                )
                for i in range(n)
            ]
            self.algorithm._candidates = candidates
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
_agl.VERL = _VERL
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
    last_init_kwargs: dict[str, object] = {}

    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        type(self).last_init_kwargs = dict(kwargs)
        self.responses = self._Responses()
        self.chat = self._Chat()

    async def judge_score(self, rendered_prompt: str) -> float:
        return 0.5

    class _Responses:
        async def create(self, *, model: str, input: str):
            return types.SimpleNamespace(output_text=input)

    class _Chat:
        class _Completions:
            async def create(self, *, model: str, messages: list[dict[str, str]]):
                content = messages[-1]["content"] if messages else ""
                message = types.SimpleNamespace(content=content)
                choice = types.SimpleNamespace(message=message)
                return types.SimpleNamespace(choices=[choice])

        def __init__(self):
            self.completions = self._Completions()


_openai.AsyncOpenAI = _AsyncOpenAI

sys.modules["openai"] = _openai

# ---------------------------------------------------------------------------
# Make trainer-prefixed skill scripts importable from tests/
# ---------------------------------------------------------------------------

_scripts_dir = Path(__file__).resolve().parent.parent / "skills" / "trainer-optimize" / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

_election_scripts_dir = Path(__file__).resolve().parent.parent / "skills" / "trainer-election" / "scripts"
if str(_election_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_election_scripts_dir))

_research_scripts_dir = Path(__file__).resolve().parent.parent / "skills" / "trainer-research" / "scripts"
if str(_research_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_research_scripts_dir))

_synthesize_scripts_dir = Path(__file__).resolve().parent.parent / "skills" / "trainer-synthesize" / "scripts"
if str(_synthesize_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_synthesize_scripts_dir))
