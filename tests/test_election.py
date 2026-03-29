"""Tests for the self-contained leader-election runtime in election/scripts/run_election.py."""
from __future__ import annotations

import json
from pathlib import Path
import runpy

import pytest

from run_election import _coerce_float, _coerce_int, _load_runs_from_benchmark, _manifest_eval_count, _mean, _read_prompt_artifact, _read_run_record, _sort_key, build_selection_pool, main as run_election_main, resolve_iteration_dir, resolve_manifest_file, run_election_search


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_workspace_run(
    eval_dir: Path,
    config_name: str,
    pass_rate: float,
    total_duration_seconds: float,
    total_tokens: int,
    *,
    run_number: int | None = None,
    prompt_text: str | None = None,
) -> None:
    run_root = eval_dir / config_name
    if run_number is not None:
        run_root = run_root / f"run-{run_number}"

    write_json(
        run_root / "grading.json",
        {
            "summary": {
                "passed": int(round(pass_rate * 10)),
                "failed": int(round((1.0 - pass_rate) * 10)),
                "total": 10,
                "pass_rate": pass_rate,
            },
            "execution_metrics": {
                "errors_encountered": 0,
                "output_chars": total_tokens,
                "total_tool_calls": 4,
            },
            "timing": {
                "total_duration_seconds": total_duration_seconds,
            },
            "expectations": [],
            "user_notes_summary": {
                "uncertainties": [],
                "needs_review": [],
                "workarounds": [],
            },
        },
    )
    write_json(
        run_root / "timing.json",
        {
            "total_duration_seconds": total_duration_seconds,
            "total_tokens": total_tokens,
        },
    )
    if prompt_text is not None:
        prompt_file = run_root / "outputs" / "prompt.md"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text(prompt_text, encoding="utf-8")


class TestBuildSelectionPool:
    def test_private_helpers_cover_sort_and_coercion_fallbacks(self):
        assert _sort_key(Path("iteration-latest")) == (10**9, "iteration-latest")
        assert _coerce_float("not-a-number") == 0.0
        assert _coerce_int(True) == 1
        assert _coerce_int(7) == 7
        assert _coerce_int("not-an-int") == 0

    def test_resolve_iteration_dir_rejects_missing_workspace(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError, match="Workspace directory not found"):
            resolve_iteration_dir(tmp_path / "missing")

    def test_resolve_iteration_dir_rejects_workspace_without_iterations_or_evals(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()

        with pytest.raises(FileNotFoundError, match="No iteration directories or eval directories found"):
            resolve_iteration_dir(workspace_dir)

    def test_resolve_iteration_dir_accepts_eval_dir_and_latest_iteration(self, tmp_path: Path):
        eval_dir = tmp_path / "eval-billing"
        write_json(eval_dir / "eval_metadata.json", {"eval_id": 1})
        write_workspace_run(eval_dir, "with_skill", 0.8, 10.0, 100)

        workspace_dir = tmp_path / "workspace"
        iteration_one = workspace_dir / "iteration-1"
        iteration_two = workspace_dir / "iteration-2"
        write_json(iteration_one / "eval-a" / "eval_metadata.json", {"eval_id": 1})
        write_workspace_run(iteration_one / "eval-a", "with_skill", 0.1, 5.0, 50)
        write_json(iteration_two / "eval-b" / "eval_metadata.json", {"eval_id": 2})
        write_workspace_run(iteration_two / "eval-b", "with_skill", 0.2, 5.0, 50)

        assert resolve_iteration_dir(eval_dir) == eval_dir
        assert resolve_iteration_dir(workspace_dir) == iteration_two
        assert resolve_iteration_dir(workspace_dir, 1) == iteration_one
        assert resolve_iteration_dir(workspace_dir, str(iteration_two)) == iteration_two

    def test_resolve_iteration_dir_supports_relative_iteration_name(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        custom_iteration = workspace_dir / "candidate-pass"
        write_json(custom_iteration / "eval-a" / "eval_metadata.json", {"eval_id": 1})
        write_workspace_run(custom_iteration / "eval-a", "with_skill", 0.3, 4.0, 40)

        assert resolve_iteration_dir(workspace_dir, "candidate-pass") == custom_iteration

    def test_resolve_iteration_dir_rejects_missing_iteration(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()

        with pytest.raises(FileNotFoundError, match="Iteration directory not found"):
            resolve_iteration_dir(workspace_dir, 7)

    def test_resolve_manifest_file_prefers_explicit_path_and_parent_fallbacks(self, tmp_path: Path):
        iteration_dir = tmp_path / "workspace" / "iteration-1"
        iteration_dir.mkdir(parents=True)
        explicit_manifest = tmp_path / "explicit-evals.json"
        parent_manifest = iteration_dir.parent / "evals" / "evals.json"
        grandparent_manifest = iteration_dir.parent.parent / "evals" / "evals.json"

        write_json(explicit_manifest, {"evals": []})
        write_json(parent_manifest, {"evals": [{"id": 1}]})
        write_json(grandparent_manifest, {"evals": [{"id": 2}]})

        assert resolve_manifest_file(iteration_dir, str(explicit_manifest)) == explicit_manifest
        assert resolve_manifest_file(iteration_dir) == parent_manifest

        parent_manifest.unlink()
        assert resolve_manifest_file(iteration_dir) == grandparent_manifest

        grandparent_manifest.unlink()
        assert resolve_manifest_file(iteration_dir) is None

        with pytest.raises(FileNotFoundError, match="Eval manifest not found"):
            resolve_manifest_file(iteration_dir, str(tmp_path / "missing.json"))

    def test_read_run_record_returns_none_without_grading_and_defaults_run_number(self, tmp_path: Path):
        eval_dir = tmp_path / "eval-a"
        config_dir = eval_dir / "with_skill"
        config_dir.mkdir(parents=True)
        write_json(eval_dir / "eval_metadata.json", {"eval_id": 1, "eval_name": "billing"})

        assert _read_run_record(eval_dir, config_dir, config_dir, 0) is None

        write_json(
            config_dir / "grading.json",
            {
                "summary": {"pass_rate": "0.75", "passed": True, "failed": "2", "total": "3"},
                "execution_metrics": {"errors_encountered": "bad", "output_chars": 55},
                "timing": {"total_duration_seconds": "7.5"},
            },
        )
        write_json(config_dir / "timing.json", {"total_duration_seconds": 8.0, "total_tokens": 123})

        record = _read_run_record(eval_dir, config_dir, config_dir, 0)

        assert record is not None
        assert record["run_number"] == 1
        assert record["pass_rate"] == 0.75
        assert record["passed"] == 1
        assert record["failed"] == 2
        assert record["total"] == 3
        assert record["time_seconds"] == 7.5
        assert record["tokens"] == 123
        assert record["errors"] == 0

    def test_prompt_artifact_and_benchmark_helpers_handle_missing_inputs(self, tmp_path: Path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        empty_manifest = tmp_path / "empty-evals.json"
        write_json(empty_manifest, {"evals": []})
        (empty_dir / "not-a-file.prompt.md").mkdir()

        assert _read_prompt_artifact([empty_dir]) == (None, None)
        assert _manifest_eval_count(None) is None
        assert _manifest_eval_count(empty_manifest) is None
        assert _load_runs_from_benchmark(empty_dir) == []
        assert _mean([]) == 0.0

    def test_prefers_full_eval_coverage_and_reads_prompt_artifacts(self, tmp_path: Path):
        prompt_root = tmp_path / "support"
        workspace_dir = prompt_root / "support-workspace"
        iteration_dir = workspace_dir / "iteration-2"
        manifest_file = prompt_root / "evals" / "evals.json"

        write_json(
            manifest_file,
            {
                "skill_name": "support-skill",
                "evals": [
                    {"id": 1, "prompt": "First eval", "expected_output": "A"},
                    {"id": 2, "prompt": "Second eval", "expected_output": "B"},
                ],
            },
        )

        billing_eval = iteration_dir / "billing-intake"
        write_json(billing_eval / "eval_metadata.json", {"eval_id": 1, "eval_name": "billing-intake"})
        write_workspace_run(
            billing_eval,
            "candidate_alpha",
            0.9,
            31.0,
            1100,
            run_number=1,
            prompt_text="Alpha prompt",
        )
        write_workspace_run(billing_eval, "without_skill", 0.6, 22.0, 800)
        write_workspace_run(
            billing_eval,
            "candidate_bravo",
            1.0,
            25.0,
            900,
            prompt_text="Bravo prompt",
        )

        refund_eval = iteration_dir / "refund-follow-up"
        write_json(refund_eval / "eval_metadata.json", {"eval_id": 2, "eval_name": "refund-follow-up"})
        write_workspace_run(refund_eval, "candidate_alpha", 0.8, 29.0, 1050, run_number=1)
        write_workspace_run(refund_eval, "without_skill", 0.7, 20.0, 780)

        selection_pool, context = build_selection_pool(
            workspace_dir=str(workspace_dir),
            iteration="iteration-2",
            manifest_file=str(manifest_file),
        )

        assert [candidate["source"] for candidate in selection_pool] == [
            "candidate_alpha",
            "without_skill",
            "candidate_bravo",
        ]
        assert selection_pool[0]["coverage_ratio"] == 1.0
        assert selection_pool[0]["prompt_text"] == "Alpha prompt"
        assert selection_pool[1]["is_baseline"] is True
        assert selection_pool[2]["coverage_ratio"] == 0.5
        assert selection_pool[2]["penalty"] == 0.5
        assert context["selection_source"] == "workspace"
        assert context["expected_eval_count"] == 2

    def test_supports_runs_subdirectory_and_manifest_free_eval_count(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        iteration_dir = workspace_dir / "iteration-1" / "runs"
        eval_dir = iteration_dir / "eval-billing"

        write_json(eval_dir / "eval_metadata.json", {"eval_id": 1, "eval_name": "billing"})
        write_workspace_run(eval_dir, "with_skill", 0.8, 10.0, 100, run_number=2)
        write_workspace_run(eval_dir, "old_skill", 0.7, 9.0, 90, run_number=1)

        selection_pool, context = build_selection_pool(workspace_dir=str(workspace_dir), iteration=1)

        assert [candidate["source"] for candidate in selection_pool] == ["with_skill", "old_skill"]
        assert all(candidate["coverage_ratio"] == 1.0 for candidate in selection_pool)
        assert context["expected_eval_count"] == 1
        assert context["manifest_file"] is None

    def test_recognizes_suffix_baselines_and_candidate_prompt_artifacts(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        eval_dir = workspace_dir / "iteration-1" / "eval-billing"

        write_json(eval_dir / "eval_metadata.json", {"eval_id": 1, "eval_name": "billing"})
        write_workspace_run(eval_dir, "candidate_new", 0.82, 10.0, 100, run_number=2)
        write_workspace_run(eval_dir, "control_baseline", 0.75, 9.0, 90, run_number=1)

        candidate_artifact = eval_dir / "candidate_new" / "run-2" / "outputs" / "final-candidate.md"
        candidate_artifact.parent.mkdir(parents=True, exist_ok=True)
        candidate_artifact.write_text("Candidate prompt body", encoding="utf-8")

        selection_pool, _ = build_selection_pool(workspace_dir=str(workspace_dir), iteration=1)
        by_name = {candidate["source"]: candidate for candidate in selection_pool}

        assert by_name["control_baseline"]["is_baseline"] is True
        assert by_name["candidate_new"]["prompt_text"] == "Candidate prompt body"
        assert by_name["candidate_new"]["prompt_file"].endswith("final-candidate.md")

    def test_direct_eval_dir_supports_manifest_fallback_and_selection(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        eval_dir = workspace_dir / "iteration-3" / "eval-billing"
        manifest_path = workspace_dir / "evals" / "evals.json"

        write_json(
            manifest_path,
            {
                "skill_name": "trainer-election",
                "evals": [
                    {"id": 1, "prompt": "billing", "expected_output": "A"},
                    {"id": 2, "prompt": "refund", "expected_output": "B"},
                ],
            },
        )
        write_json(eval_dir / "eval_metadata.json", {"eval_id": 1, "eval_name": "billing"})
        write_workspace_run(eval_dir, "with_skill", 0.85, 11.0, 120)
        write_workspace_run(eval_dir, "without_skill", 0.8, 8.0, 90)

        selection_pool, context = build_selection_pool(workspace_dir=str(eval_dir))

        assert [candidate["source"] for candidate in selection_pool] == ["with_skill", "without_skill"]
        assert selection_pool[0]["coverage_ratio"] == 0.5
        assert selection_pool[0]["penalty"] == 0.5
        assert context["manifest_file"] == str(manifest_path)
        assert context["expected_eval_count"] == 2

    def test_raises_when_no_scored_candidate_runs_exist(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        iteration_dir = workspace_dir / "iteration-1" / "eval-empty"
        iteration_dir.mkdir(parents=True)
        write_json(iteration_dir / "eval_metadata.json", {"eval_id": 1})

        with pytest.raises(RuntimeError, match="No scored candidate runs were found"):
            build_selection_pool(workspace_dir=str(workspace_dir), iteration=1)


class TestRunElectionSearch:
    @pytest.mark.asyncio
    async def test_workspace_result_sets_prompt_fields_and_single_winner(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        eval_dir = workspace_dir / "iteration-1" / "eval-billing"
        write_json(eval_dir / "eval_metadata.json", {"eval_id": 1, "eval_name": "billing"})
        write_workspace_run(eval_dir, "with_skill", 0.9, 12.0, 100, prompt_text="Winning prompt")
        write_workspace_run(eval_dir, "without_skill", 0.4, 8.0, 50)

        result = await run_election_search(workspace_dir=str(workspace_dir), iteration=1)

        assert result["winner"] == "with_skill"
        assert result["best_prompt"] == "Winning prompt"
        assert result["best_prompt_file"].endswith("prompt.md")
        assert sum(1 for candidate in result["persisted_candidates"] if candidate["is_winner"]) == 1

    @pytest.mark.asyncio
    async def test_uses_benchmark_fallback_when_workspace_runs_are_missing(self, tmp_path: Path):
        workspace_dir = tmp_path / "candidate-workspace"
        iteration_dir = workspace_dir / "iteration-1"
        write_json(
            iteration_dir / "benchmark.json",
            {
                "metadata": {
                    "skill_name": "candidate-skill",
                    "evals_run": [1, 2],
                    "runs_per_configuration": 1,
                },
                "runs": [
                    {
                        "eval_id": 1,
                        "eval_name": "billing-intake",
                        "configuration": "with_skill",
                        "run_number": 1,
                        "result": {
                            "pass_rate": 0.9,
                            "passed": 9,
                            "failed": 1,
                            "total": 10,
                            "time_seconds": 34.0,
                            "tokens": 1200,
                            "errors": 0,
                        },
                        "expectations": [],
                        "notes": [],
                    },
                    {
                        "eval_id": 2,
                        "eval_name": "refund-follow-up",
                        "configuration": "with_skill",
                        "run_number": 1,
                        "result": {
                            "pass_rate": 0.8,
                            "passed": 8,
                            "failed": 2,
                            "total": 10,
                            "time_seconds": 36.0,
                            "tokens": 1210,
                            "errors": 0,
                        },
                        "expectations": [],
                        "notes": [],
                    },
                    {
                        "eval_id": 1,
                        "eval_name": "billing-intake",
                        "configuration": "without_skill",
                        "run_number": 1,
                        "result": {
                            "pass_rate": 0.5,
                            "passed": 5,
                            "failed": 5,
                            "total": 10,
                            "time_seconds": 21.0,
                            "tokens": 700,
                            "errors": 0,
                        },
                        "expectations": [],
                        "notes": [],
                    },
                    {
                        "eval_id": 2,
                        "eval_name": "refund-follow-up",
                        "configuration": "without_skill",
                        "run_number": 1,
                        "result": {
                            "pass_rate": 0.6,
                            "passed": 6,
                            "failed": 4,
                            "total": 10,
                            "time_seconds": 20.0,
                            "tokens": 680,
                            "errors": 0,
                        },
                        "expectations": [],
                        "notes": [],
                    },
                ],
            },
        )

        result = await run_election_search(workspace_dir=str(workspace_dir), iteration=1)

        assert result["winner"] == "with_skill"
        assert result["selection_source"] == "benchmark"
        assert result["best_prompt"] is None
        assert result["best_candidate"]["is_winner"] is True
        assert any(candidate["is_baseline"] for candidate in result["persisted_candidates"])


class TestElectionCli:
    def test_main_writes_output_file(self, tmp_path: Path):
        workspace_dir = tmp_path / "workspace"
        eval_dir = workspace_dir / "iteration-1" / "eval-billing"
        output_path = tmp_path / "election-result.json"
        write_json(eval_dir / "eval_metadata.json", {"eval_id": 1, "eval_name": "billing"})
        write_workspace_run(eval_dir, "with_skill", 0.9, 12.0, 100, prompt_text="Winning prompt")
        write_workspace_run(eval_dir, "without_skill", 0.4, 8.0, 50)

        exit_code = run_election_main([str(workspace_dir), "--iteration", "1", "--output-file", str(output_path)])

        assert exit_code == 0
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        assert payload["winner"] == "with_skill"

    def test_main_prints_stdout_when_no_output_file(self, tmp_path: Path, capsys):
        workspace_dir = tmp_path / "workspace"
        eval_dir = workspace_dir / "iteration-1" / "eval-billing"
        write_json(eval_dir / "eval_metadata.json", {"eval_id": 1, "eval_name": "billing"})
        write_workspace_run(eval_dir, "with_skill", 0.9, 12.0, 100, prompt_text="Winning prompt")
        write_workspace_run(eval_dir, "without_skill", 0.4, 8.0, 50)

        exit_code = run_election_main([str(workspace_dir), "--iteration", "1"])

        assert exit_code == 0
        assert '"winner": "with_skill"' in capsys.readouterr().out

    def test_module_entrypoint_executes_main(self, tmp_path: Path, monkeypatch, capsys):
        workspace_dir = tmp_path / "workspace"
        eval_dir = workspace_dir / "iteration-1" / "eval-billing"
        write_json(eval_dir / "eval_metadata.json", {"eval_id": 1, "eval_name": "billing"})
        write_workspace_run(eval_dir, "with_skill", 0.9, 12.0, 100, prompt_text="Winning prompt")
        write_workspace_run(eval_dir, "without_skill", 0.4, 8.0, 50)

        script_path = Path(__file__).resolve().parent.parent / "skills" / "trainer-election" / "scripts" / "run_election.py"
        monkeypatch.setattr("sys.argv", [str(script_path), str(workspace_dir), "--iteration", "1"])

        with pytest.raises(SystemExit) as exc_info:
            runpy.run_path(str(script_path), run_name="__main__")

        assert exc_info.value.code == 0
        assert '"winner": "with_skill"' in capsys.readouterr().out