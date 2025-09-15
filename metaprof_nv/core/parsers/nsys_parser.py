from typing import Dict, Any, List
import csv


def parse_nsys_kernel_csv(csv_path: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("Name") or row.get("Kernel Name") or row.get("CUDA Kernel Name")
            time_ms = _to_float(row.get("Time (ms)") or row.get("Duration (ms)") or row.get("time_ms"))
            if name:
                out.append({"name": name, "time_ms": time_ms})
    return out


def _to_float(v: Any):
    try:
        return float(str(v).replace(",", ""))
    except Exception:
        return None
