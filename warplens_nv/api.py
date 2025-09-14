from typing import Dict, Any, Optional
from warplens_nv.core.spec import ProfilingSpec
from warplens_nv.core.runner import Runner
from warplens_nv.core.results import ProfilingResult
from warplens_nv.core.catalog.recipes import Recipes, resolve_recipe

__all__ = ["profile", "Recipes", "ProfilingResult", "ProfilingSpec"]


def profile(
    target: Dict[str, Any],
    recipe: str,
    kernel_selector: Optional[Dict[str, Any]] = None,
) -> ProfilingResult:
    spec = ProfilingSpec(
        target=target,
        profile={"recipe": recipe, "kernel_selector": kernel_selector or {}},
    )
    runner = Runner()
    return runner.run(spec)
