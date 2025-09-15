from typer import Typer
from metaprof_nv.api import profile, Recipes
import yaml
from pathlib import Path

app = Typer(add_completion=False)

@app.command()
def profile_cmd(
    spec: str = "",
    recipe: str = "",
    target_type: str = "",
    entry: str = "",
    args: str = "",
    match: str = "",
    top_by_time: int = 0,
    metric: str = "",
):
    """Profile a workload.

    Examples:
      metaprof profile --spec spec.yaml
      metaprof profile --recipe l2_locality --target-type python --entry run.py --args "--seq 8192" --metric l2_hit_rate
    """
    if spec:
        data = yaml.safe_load(Path(spec).read_text())
        result = profile(**data)
    else:
        from metaprof_nv.core.spec import ProfilingSpec
        ks = {"match": match or None, "top_by_time": top_by_time or None}
        ks = {k: v for k, v in ks.items() if v is not None}
        prof = {"kernel_selector": ks}
        if recipe:
            prof["recipe"] = recipe
        else:
            # if single metric requested without recipe, set objectives
            if metric:
                prof["objectives"] = [metric]
        spec_obj = ProfilingSpec(
            target={"type": target_type, "entry": entry, "args": args.split() if args else []},
            profile=prof,
        )
        result = profile(target=spec_obj.target.model_dump(), recipe=prof.get("recipe", "") or metric, kernel_selector=ks)
    from rich import print
    if metric:
        # Try summary first
        val = result.metrics.summary.get(metric)
        if val is None and result.metrics.by_kernel:
            # fall back to first kernel value
            val = result.metrics.by_kernel[0].metrics.get(metric)
        print({metric: val})
    else:
        print(result.model_dump())

if __name__ == "__main__":
    app()
