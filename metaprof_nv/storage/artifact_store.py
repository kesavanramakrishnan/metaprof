from pathlib import Path
from typing import Dict
import json
from datetime import datetime

class ArtifactStore:
    def __init__(self, root: str = "artifacts"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def start_run(self, hint: str = "") -> str:
        ts = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
        run_id = f"{ts}{('_' + hint) if hint else ''}"
        (self.root / run_id).mkdir(parents=True, exist_ok=True)
        return run_id

    def path(self, run_id: str, filename: str) -> str:
        p = self.root / run_id / filename
        p.parent.mkdir(parents=True, exist_ok=True)
        return str(p)

    def write_json(self, run_id: str, filename: str, data: Dict):
        p = Path(self.path(run_id, filename))
        p.write_text(json.dumps(data, indent=2))
        return str(p)
