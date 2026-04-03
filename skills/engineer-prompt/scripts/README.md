# Scripts

- `export_skill_prompt.py`: DSPy-backed helper that compiles an optimized instruction body for the engineer-prompt skill and renders a stable Markdown artifact.

Use `python skills/engineer-prompt/scripts/export_skill_prompt.py --validate-only` for deterministic validation of the current engineer-prompt markdown contract.
Use `python skills/engineer-prompt/scripts/export_skill_prompt.py --optimize --output-file /tmp/engineer-prompt.md` to run the DSPy optimizer and write a generated artifact when a compatible DSPy model is configured.
