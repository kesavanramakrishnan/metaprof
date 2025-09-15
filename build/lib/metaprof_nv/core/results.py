from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class SystemInfo(BaseModel):
    gpu: Dict[str, Any] = Field(default_factory=dict)
    nvml: Dict[str, Any] = Field(default_factory=dict)

class ArtifactPaths(BaseModel):
    ncu: Optional[str] = None
    nsys: Optional[str] = None

class KernelMetrics(BaseModel):
    name: str
    time_ms: Optional[float] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)

class Metrics(BaseModel):
    summary: Dict[str, Any] = Field(default_factory=dict)
    by_kernel: List[KernelMetrics] = Field(default_factory=list)

class ProfilingResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    run_id: str
    system: SystemInfo = Field(default_factory=SystemInfo)
    workload: Dict[str, Any] = Field(default_factory=dict)
    artifacts: ArtifactPaths = Field(default_factory=ArtifactPaths)
    metrics: Metrics = Field(default_factory=Metrics)
