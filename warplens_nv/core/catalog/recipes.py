from enum import Enum
from typing import Dict, List

RECIPES: Dict[str, Dict[str, List[str]]] = {
    "l2_locality": {
        "tools": ["ncu"],
        "metrics": ["l2_hit_rate", "dram_bw_util_pct", "kernel_time_ms"],
    },
    "register_spills": {
        "tools": ["ncu"],
        "metrics": ["reg_spills_per_thread", "sm_occupancy_pct", "kernel_time_ms"],
    },
    "bank_conflicts": {
        "tools": ["ncu"],
        "metrics": ["smem_bank_conflict_factor", "warp_execution_efficiency_pct", "kernel_time_ms"],
    },
    "throughput_overview": {
        "tools": ["ncu", "nsys"],
        "metrics": [
            "sm_occupancy_pct",
            "warp_execution_efficiency_pct",
            "kernel_time_ms",
            "cpu_gpu_overlap_pct",
        ],
    },
}

class Recipes(str, Enum):
    L2_LOCALITY = "l2_locality"
    REGISTER_SPILLS = "register_spills"
    BANK_CONFLICTS = "bank_conflicts"
    THROUGHPUT_OVERVIEW = "throughput_overview"


def resolve_recipe(name: str) -> Dict[str, List[str]]:
    key = name.lower()
    if key not in RECIPES:
        raise KeyError(f"Unknown recipe: {name}")
    return RECIPES[key]
