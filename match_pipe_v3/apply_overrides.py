#!/usr/bin/env python3
"""Apply dashboard-edited parts to a PromptRegistry at runtime.

Usage in runner:
    from match_pipe_v3.registry import PromptRegistry
    from match_pipe_v3.apply_overrides import apply_overrides

    registry = PromptRegistry.from_dir("match_pipe_v3")
    apply_overrides(registry)   # loads match_pipe_v3/overrides.json if present
"""

from pathlib import Path

from match_pipe_v3.registry import PromptRegistry


DEFAULT_OVERRIDES_PATH = Path(__file__).resolve().parent / "overrides.json"


def apply_overrides(registry: PromptRegistry, path: str | Path | None = None) -> None:
    """Load a dashboard export JSON and inject into the registry."""
    p = Path(path) if path else DEFAULT_OVERRIDES_PATH
    if p.exists():
        registry.load_overrides(p)
