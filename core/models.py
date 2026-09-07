from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TaskNode(BaseModel):
    id: str
    type: str = "agent-task"
    agent: str
    dependencies: List[str] = Field(default_factory=list)
    params: Dict[str, Any] = Field(default_factory=dict)
    retry_policy: Dict[str, Any] = Field(default_factory=lambda: {"max_retries": 3, "backoff": "exponential"})

class Workflow(BaseModel):
    id: str
    nodes: List[TaskNode]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TaskStatus(BaseModel):
    task_id: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED, COMPENSATING
    worker_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
