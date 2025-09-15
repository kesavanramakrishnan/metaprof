from typing import Dict, Any, List, Tuple
import csv
from metaprof_nv.core.catalog import metrics as cat_metrics


def parse_ncu_csv(csv_path: str) -> List[Tuple[str, Dict[str, Any]]]:
    """Return list of (kernel_name, counters) from ncu CSV export."""
    rows: List[Tuple[str, Dict[str, Any]]] = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            kernel = row.get("Kernel Name") or row.get("KernelName") or row.get("Name")
            counters = {k: _maybe_float(v) for k, v in row.items()}
            if kernel:
                rows.append((kernel, counters))
    return rows


def compute_metrics_for_kernel(counters: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for name, md in cat_metrics.REGISTRY.items():
        if md.source != "ncu":
            continue
        out[name] = md.formula(counters)
    return out


def _maybe_float(v: Any):
    try:
        return float(str(v).replace(",", ""))
    except Exception:
        return v
