import os
import subprocess
from typing import List, Dict

def launch(entry: str, args: List[str], env: Dict[str, str]) -> subprocess.CompletedProcess:
    cmd = ["pytest", entry, *args]
    merged_env = os.environ.copy()
    merged_env.update(env or {})
    return subprocess.run(cmd, env=merged_env, capture_output=True, text=True, check=False)
