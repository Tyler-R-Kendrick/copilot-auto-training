from __future__ import annotations

import asyncio
from typing import Any, Literal


def generate_variants(prompt_text: str, n: int) -> list[str]:
    from run_optimize import generate_variants as _generate_variants

    return _generate_variants(prompt_text, n)


async def topk_select(
    variants: list[str],
    dataset: list[dict[str, Any]],
    judge_mode: str = "deterministic",
    k: int = 1,
    judge_prompt_file: str | None = None,
    llm_client: Any | None = None,
    custom_scorer: Any | None = None,
    steering_text: str = "",
) -> list[str]:
    from run_optimize import topk_select as _topk_select

    kwargs: dict[str, Any] = {
        "judge_mode": judge_mode,
        "k": k,
    }
    if judge_prompt_file is not None:
        kwargs["judge_prompt_file"] = judge_prompt_file
    if llm_client is not None:
        kwargs["llm_client"] = llm_client
    if custom_scorer is not None:
        kwargs["custom_scorer"] = custom_scorer
    if steering_text:
        kwargs["steering_text"] = steering_text

    return await _topk_select(variants, dataset, **kwargs)


def build_selection_pool(
    candidate_templates: list[str],
    baseline_prompt: str,
    algorithm: str = "election",
    n_variants: int = 4,
) -> tuple[list[str], list[str]]:
    if len(candidate_templates) == 1:
        variants = generate_variants(candidate_templates[0], n_variants)
        return variants + [baseline_prompt], [f"variant_{index + 1}" for index in range(len(variants))] + ["baseline"]

    selection_pool = list(candidate_templates) + [baseline_prompt]
    selection_sources = [f"{algorithm}_candidate_{index + 1}" for index in range(len(candidate_templates))] + ["baseline"]
    return selection_pool, selection_sources


async def run_election_search(
    prompt_text: str,
    train_dataset: list[dict[str, Any]],
    val_dataset: list[dict[str, Any]],
    openai_client: Any,
    model_settings: dict[str, Any],
    algorithm: Literal["apo", "verl"] = "apo",
    iterations: int = 3,
    beam_width: int = 4,
    branch_factor: int = 4,
    n_runners: int = 4,
    judge_mode: Literal["deterministic", "custom", "llm_judge"] = "deterministic",
    judge_prompt_file: str | None = None,
    n_variants: int = 4,
    steering_text: str = "",
) -> dict[str, Any]:
    import agentlightning as agl
    from run_optimize import _make_rollout, assess_candidates

    algorithm_registry = {
        "apo": agl.APO,
        "verl": agl.VERL,
    }
    if algorithm not in algorithm_registry:
        raise ValueError(f"Unsupported algorithm: {algorithm!r}")

    algo = algorithm_registry[algorithm](
        openai_client,
        beam_rounds=iterations,
        beam_width=beam_width,
        branch_factor=branch_factor,
        gradient_batch_size=min(4, len(train_dataset)),
        val_batch_size=min(16, len(val_dataset)),
        gradient_model=model_settings["gradient_model"],
        apply_edit_model=model_settings["apply_edit_model"],
    )

    trainer = agl.Trainer(
        algorithm=algo,
        n_runners=n_runners,
        tracer=agl.OtelTracer(),
        initial_resources={
            "main_prompt": agl.PromptTemplate(template=prompt_text, engine="f-string")
        },
        adapter=agl.TraceToMessages(),
    )

    rollout_fn = _make_rollout(judge_mode)
    await asyncio.to_thread(
        trainer.fit,
        agent=rollout_fn,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
    )

    candidates = algo.get_candidates()
    if not candidates:
        raise RuntimeError("Optimization produced no valid prompt candidates.")

    selection_pool, selection_sources = build_selection_pool(
        candidate_templates=[candidate.template for candidate in candidates],
        baseline_prompt=prompt_text,
        algorithm="election",
        n_variants=n_variants,
    )

    topk_kwargs: dict[str, Any] = {
        "judge_mode": judge_mode,
        "k": 1,
    }
    if judge_prompt_file is not None:
        topk_kwargs["judge_prompt_file"] = judge_prompt_file
    if steering_text.strip():
        topk_kwargs["steering_text"] = steering_text

    top = await topk_select(selection_pool, val_dataset, **topk_kwargs)
    if not top:
        raise RuntimeError("Optimization produced no selectable prompt candidates.")
    best_prompt = top[0]

    candidate_assessments = await assess_candidates(
        selection_pool,
        val_dataset,
        judge_mode=judge_mode,
        judge_prompt_file=judge_prompt_file,
        steering_text=steering_text,
    )
    persisted_candidates = [
        {
            "template": candidate["template"],
            "score": candidate["score"],
            "raw_score": candidate["raw_score"],
            "penalty": candidate["penalty"],
            "source": source,
            "is_baseline": source == "baseline",
            "is_winner": candidate["template"] == best_prompt,
            "risks": candidate["risks"],
            "improvements": candidate["improvements"],
            "steering_hits": candidate["steering_hits"],
        }
        for candidate, source in zip(candidate_assessments, selection_sources, strict=True)
    ]

    return {
        "best_prompt": best_prompt,
        "persisted_candidates": persisted_candidates,
        "steering_applied": bool(steering_text.strip()),
    }