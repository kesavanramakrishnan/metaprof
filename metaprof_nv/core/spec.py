from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

class Target(BaseModel):
    type: Literal["python", "pytest", "binary"]
    entry: str
    args: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)

class KernelSelector(BaseModel):
    match: Optional[str] = None
    top_by_time: Optional[int] = None
    index: Optional[List[str]] = None

class Profile(BaseModel):
    tools: Optional[List[Literal["ncu", "nsys"]]] = None
    objectives: Optional[List[str]] = None
    recipe: Optional[str] = None
    kernel_selector: KernelSelector = Field(default_factory=KernelSelector)
    duration: Optional[Dict[str, int]] = None

class ProfilingSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target: Target
    profile: Profile
