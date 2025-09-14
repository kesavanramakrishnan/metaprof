import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple

from warplens_nv.core.spec import ProfilingSpec
from warplens_nv.core.results import ProfilingResult, Metrics, KernelMetrics, ArtifactPaths
from warplens_nv.core.parsers.nsys_parser import parse_nsys_kernel_csv
from warplens_nv.core.parsers.ncu_parser import parse_ncu_csv, compute_metrics_for_kernel
from warplens_nv.core.catalog.recipes import resolve_recipe
from warplens_nv.storage.artifact_store import ArtifactStore


class Runner:
    def __init__(self, artifact_root: str = "artifacts"):
        self.store = ArtifactStore(artifact_root)

    def run(self, spec: ProfilingSpec) -> ProfilingResult:
        hint = Path(spec.target.entry).stem
        run_id = self.store.start_run(hint)
        artifacts = ArtifactPaths()

        # Determine tools from recipe if not explicitly provided
        tools = spec.profile.tools
        if not tools and spec.profile.recipe:
            tools = resolve_recipe(spec.profile.recipe)["tools"]

        # Prepass to pick kernels if needed
        kernel_names: List[str] = []
        if spec.profile.kernel_selector.top_by_time:
            kernel_names = self.nsys_prepass(spec, run_id)
            if spec.profile.kernel_selector.match:
                pattern = re.compile(spec.profile.kernel_selector.match)
                kernel_names = [k for k in kernel_names if pattern.search(k)]
            kernel_names = kernel_names[: spec.profile.kernel_selector.top_by_time]
        elif spec.profile.kernel_selector.match:
            pattern = re.compile(spec.profile.kernel_selector.match)
            # Without names, ncu will filter by regex directly

        if tools and "ncu" in tools:
            ncu_csv, ncu_rep = self.ncu_profile(spec, run_id)
            artifacts.ncu = ncu_rep
            kernels = parse_ncu_csv(ncu_csv)
        else:
            kernels = []

        # Aggregate metrics
        by_kernel: List[KernelMetrics] = []
        for name, counters in kernels:
            km = KernelMetrics(name=name, time_ms=counters.get("time_ms"))
            km.metrics = compute_metrics_for_kernel(counters)
            by_kernel.append(km)

        # Summary: simple averages over available metrics
        summary: Dict[str, Any] = {}
        if by_kernel:
            keys = set().union(*[set(km.metrics.keys()) for km in by_kernel])
            for k in keys:
                vals = [km.metrics.get(k) for km in by_kernel if km.metrics.get(k) is not None]
                summary[k] = sum(vals) / len(vals) if vals else None

        result = ProfilingResult(
            run_id=run_id,
            workload={
                "cmd": self._render_cmd(spec),
                "env": spec.target.env,
            },
            artifacts=artifacts,
            metrics=Metrics(summary=summary, by_kernel=by_kernel),
        )

        # Persist normalized result
        self.store.write_json(run_id, "result.json", result.model_dump())
        return result

    def _render_cmd(self, spec: ProfilingSpec) -> str:
        if spec.target.type == "python":
            return "python " + spec.target.entry + (" " + " ".join(spec.target.args) if spec.target.args else "")
        if spec.target.type == "pytest":
            return "pytest " + spec.target.entry + (" " + " ".join(spec.target.args) if spec.target.args else "")
        return spec.target.entry + (" " + " ".join(spec.target.args) if spec.target.args else "")

    def nsys_prepass(self, spec: ProfilingSpec, run_id: str) -> List[str]:
        out_csv = self.store.path(run_id, "nsys_kernels.csv")
        # Run nsys stats directly if a qdrep already existed, else do a quick profile run.
        entry_cmd = self._entry_command(spec)
        qdrep = self.store.path(run_id, "trace.qdrep")
        cmd = [
            "nsys", "profile", "--trace=cuda,nvtx,osrt", "--sample=cpu",
            "-o", qdrep.replace(".qdrep", ""),
            *entry_cmd,
        ]
        subprocess.run(cmd, check=False)
        # Extract kernel summary
        stats_cmd = [
            "nsys", "stats", "--report", "cudaapisum,kernsum", "--format", "csv",
            qdrep,
        ]
        with open(out_csv, "w") as f:
            subprocess.run(stats_cmd, stdout=f, check=False)
        rows = parse_nsys_kernel_csv(out_csv)
        rows = sorted(rows, key=lambda r: (r.get("time_ms") or 0), reverse=True)
        return [r["name"] for r in rows]

    def ncu_profile(self, spec: ProfilingSpec, run_id: str) -> Tuple[str, str]:
        out_csv = self.store.path(run_id, "ncu.csv")
        out_rep_base = self.store.path(run_id, "ncu_report")
        out_rep = out_rep_base + ".ncu-rep"
        entry_cmd = self._entry_command(spec)

        # Sections from recipe
        sections: List[str] = []
        if spec.profile.recipe:
            rec = resolve_recipe(spec.profile.recipe)
            # Minimal sections to begin with
            if "ncu" in rec["tools"]:
                sections = ["LaunchStats", "MemoryWorkloadAnalysis", "WarpStateStats"]

        cmd = ["ncu", "--csv", "--target-processes", "all", "--export", out_rep_base]
        for s in sections:
            cmd += ["--section", s]
        if spec.profile.kernel_selector.match:
            cmd += ["--kernel-name-base", f"regex:{spec.profile.kernel_selector.match}"]
        cmd += ["--", *entry_cmd]

        with open(out_csv, "w") as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, check=False)
        return out_csv, out_rep

    def _entry_command(self, spec: ProfilingSpec) -> List[str]:
        env = os.environ.copy()
        env.update(spec.target.env or {})
        if spec.target.type == "python":
            return ["python", spec.target.entry, *spec.target.args]
        if spec.target.type == "pytest":
            return ["pytest", spec.target.entry, *spec.target.args]
        return [spec.target.entry, *spec.target.args]
