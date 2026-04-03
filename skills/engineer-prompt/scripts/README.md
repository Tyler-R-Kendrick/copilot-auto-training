# Scripts

- `optimize_prompt.py`: DSPy-backed helper for general markdown prompt optimization with DSPy.

Use `python skills/engineer-prompt/scripts/optimize_prompt.py --validate-only --prompt-file <path-to-prompt.md>` for deterministic prompt validation.
Use `python skills/engineer-prompt/scripts/optimize_prompt.py --optimize --prompt-file <path-to-prompt.md> --output-file /tmp/optimized-prompt.md` to run the DSPy optimizer and write the optimized prompt when a compatible DSPy model is configured.
