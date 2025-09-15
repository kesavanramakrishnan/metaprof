from typing import Dict, Any, Callable, List

# Canonical metric registry and mapping to tool-specific counters

class MetricDef:
    def __init__(self, description: str, source: str, formula: Callable[[Dict[str, Any]], Any]):
        self.description = description
        self.source = source  # "ncu" | "nsys" | "cupti"
        self.formula = formula

REGISTRY: Dict[str, MetricDef] = {}


def register(name: str, description: str, source: str):
    def deco(fn: Callable[[Dict[str, Any]], Any]):
        REGISTRY[name] = MetricDef(description, source, fn)
        return fn
    return deco

# Initial metrics (v0)

@register(
    "l2_hit_rate",
    "L2 cache hit rate",
    "ncu",
)
def l2_hit_rate(c: Dict[str, Any]):
    hits = c.get("lts__t_sectors_hit.sum", 0)
    total = c.get("lts__t_sectors.sum", 0)
    return (hits / total) if total else None

@register(
    "dram_bw_util_pct",
    "DRAM bandwidth utilization percent",
    "ncu",
)
def dram_bw_util_pct(c: Dict[str, Any]):
    bytes_sum = c.get("dram__bytes.sum", 0)
    theoretical = c.get("theoretical_dram_bw_bytes", 0)
    duration_s = c.get("duration_seconds", 0)
    return (bytes_sum / (theoretical * duration_s) * 100.0) if theoretical and duration_s else None

@register(
    "reg_spills_per_thread",
    "Estimated register spills per thread",
    "ncu",
)
def reg_spills_per_thread(c: Dict[str, Any]):
    return c.get("reg_spills_per_thread", None)

@register(
    "sm_occupancy_pct",
    "SM occupancy percent of peak",
    "ncu",
)
def sm_occupancy_pct(c: Dict[str, Any]):
    return c.get("sm__warps_active.avg.pct_of_peak_sustained_active", None)

@register(
    "warp_execution_efficiency_pct",
    "Warp execution efficiency percent",
    "ncu",
)
def warp_execution_efficiency_pct(c: Dict[str, Any]):
    return c.get("warp__exec_efficiency", None)

@register(
    "smem_bank_conflict_factor",
    "Shared memory bank conflict factor",
    "ncu",
)
def smem_bank_conflict_factor(c: Dict[str, Any]):
    return c.get("smem_bank_conflict_factor", None)

@register(
    "kernel_time_ms",
    "Kernel execution time in milliseconds",
    "nsys",
)
def kernel_time_ms(c: Dict[str, Any]):
    return c.get("time_ms", None)

@register(
    "cpu_gpu_overlap_pct",
    "Percent of CPU/GPU overlap",
    "nsys",
)
def cpu_gpu_overlap_pct(c: Dict[str, Any]):
    return c.get("cpu_gpu_overlap_pct", None)

# Tool counter requirements for Nsight Compute per canonical metric (best-effort v0)
REQUIRED_COUNTERS_NCU: Dict[str, List[str]] = {
    "l2_hit_rate": ["lts__t_sectors_hit.sum", "lts__t_sectors.sum"],
    "dram_bw_util_pct": ["dram__bytes.sum"],
    "warp_execution_efficiency_pct": ["warp__exec_efficiency"],
}


def required_counters_for(metrics: List[str]) -> List[str]:
    counters: List[str] = []
    for m in metrics:
        counters += REQUIRED_COUNTERS_NCU.get(m, [])
    # de-duplicate preserving order
    seen = set()
    out: List[str] = []
    for c in counters:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out
