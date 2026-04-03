# Scripts

- `export_skill_prompt.py`: DSPy-backed helper that validates or optimizes a general markdown prompt file and renders a stable markdown artifact.

Use `python skills/engineer-prompt/scripts/export_skill_prompt.py --validate-only --prompt-file <path-to-prompt.md>` for deterministic prompt validation.
Use `python skills/engineer-prompt/scripts/export_skill_prompt.py --optimize --prompt-file <path-to-prompt.md> --output-file /tmp/optimized-prompt.md` to run the DSPy optimizer and write a generated artifact when a compatible DSPy model is configured.
