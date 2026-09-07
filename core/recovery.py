import asyncio
from typing import List, Dict, Any
from .models import Workflow, TaskNode, TaskStatus

class SelfHealingEngine:
    def __init__(self, engine):
        self.engine = engine
        self.rollback_history: Dict[str, List[str]] = {}

    async def handle_node_failure(self, workflow_id: str, failed_node: TaskNode, error: str) -> bool:
        """
        Attempts self-healing strategies upon permanent task failure.
        Strategies:
        1. Alternative Route/Fallback Execution
        2. Compensating Transaction Rollback (Saga Pattern)
        """
        print(f"[SelfHealing] Handling failure for workflow {workflow_id}, node {failed_node.id}: {error}")
        
        # Strategy 1: Check for fallback handler parameters
        fallback_agent = failed_node.params.get("fallback_agent")
        if fallback_agent:
            print(f"[SelfHealing] Attempting fallback agent: {fallback_agent}")
            failed_node.agent = fallback_agent
            # Retry execution with fallback agent
            return True

        # Strategy 2: Execute Compensation / Rollback
        print(f"[SelfHealing] Triggering compensation saga for workflow {workflow_id}...")
        await self.trigger_rollback(workflow_id)
        return False

    async def trigger_rollback(self, workflow_id: str):
        """
        Executes compensating tasks in reverse topological order for completed tasks.
        """
        completed_tasks = self.rollback_history.get(workflow_id, [])
        for task_id in reversed(completed_tasks):
            print(f"[Rollback] Executing compensating action for task: {task_id}")
            # Simulate rollback work
            await asyncio.sleep(0.5)
            print(f"[Rollback] Task {task_id} successfully compensated/rolled back.")
        
        self.rollback_history[workflow_id] = []

    def record_completed_task(self, workflow_id: str, task_id: str):
        if workflow_id not in self.rollback_history:
            self.rollback_history[workflow_id] = []
        self.rollback_history[workflow_id].append(task_id)
