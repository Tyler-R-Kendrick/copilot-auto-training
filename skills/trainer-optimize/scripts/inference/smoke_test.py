from __future__ import annotations

import argparse
import asyncio

from inference.config import InferenceConfig
from inference.contract import InferenceRequest
from inference.copilot_provider import CopilotInferenceProvider


async def main_async(model: str = "default") -> str:
    provider = CopilotInferenceProvider(InferenceConfig(model=model))
    result = await provider.generate(
        InferenceRequest(
            messages=[{"role": "user", "content": "Say hello in one sentence"}],
            model=model,
            metadata={"episode_id": "smoke-test", "step_id": "hello"},
        )
    )
    return result.text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a Copilot inference smoke test.")
    parser.add_argument("--model", default="default")
    args = parser.parse_args(argv)
    print(asyncio.run(main_async(model=args.model)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
