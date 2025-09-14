from typer import Typer
from warplens_nv.api import profile, Recipes
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
):
    """Profile a workload.

    Examples:
      warplens profile --spec spec.yaml
      warplens profile --recipe l2_locality --target-type python --entry run.py --args "--seq 8192"
    """
    if spec:
        data = yaml.safe_load(Path(spec).read_text())
        result = profile(**data)
    else:
        from warplens_nv.core.spec import ProfilingSpec
        ks = {"match": match or None, "top_by_time": top_by_time or None}
        ks = {k: v for k, v in ks.items() if v is not None}
        spec_obj = ProfilingSpec(
            target={"type": target_type, "entry": entry, "args": args.split() if args else []},
            profile={"recipe": recipe, "kernel_selector": ks},
        )
        result = profile(target=spec_obj.target.model_dump(), recipe=recipe, kernel_selector=ks)
    from rich import print
    print(result.model_dump())

if __name__ == "__main__":
    app()
