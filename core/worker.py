import asyncio
import json
import time
from typing import Dict, Any, Callable
from .models import TaskNode, TaskStatus

class AegisWorker:
    def __init__(self, worker_id: str, redis_client=None):
        self.worker_id = worker_id
        self.redis = redis_client
        self.registered_agents: Dict[str, Callable] = {}
        self.is_running = False

    def register_agent(self, name: str, handler: Callable):
        """Register a handler function for a specific agent type."""
        self.registered_agents[name] = handler
        print(f"[Worker {self.worker_id}] Registered agent: {name}")

    async def execute_task(self, task: TaskNode) -> TaskStatus:
        """Executes a task with retries and reports status."""
        print(f"[Worker {self.worker_id}] Starting task: {task.id} (Agent: {task.agent})")
        
        status = TaskStatus(
            task_id=task.id,
            status="RUNNING",
            worker_id=self.worker_id
        )
        
        if task.agent not in self.registered_agents:
            status.status = "FAILED"
            status.error = f"No handler registered for agent: {task.agent}"
            return status

        max_retries = task.retry_policy.get("max_retries", 3)
        backoff = task.retry_policy.get("backoff", "exponential")
        
        for attempt in range(1, max_retries + 1):
            try:
                handler = self.registered_agents[task.agent]
                # Execute the handler (can be async or sync)
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(task.params)
                else:
                    result = handler(task.params)
                
                status.status = "COMPLETED"
                status.result = result if isinstance(result, dict) else {"output": str(result)}
                print(f"[Worker {self.worker_id}] Task {task.id} COMPLETED successfully.")
                return status
            except Exception as e:
                print(f"[Worker {self.worker_id}] Task {task.id} Attempt {attempt} FAILED: {str(e)}")
                if attempt < max_retries:
                    sleep_time = (2 ** attempt) if backoff == "exponential" else 1
                    await asyncio.sleep(sleep_time)
                else:
                    status.status = "FAILED"
                    status.error = str(e)
                    return status

    async def heartbeat_loop(self):
        """Sends periodic heartbeats to track worker health."""
        while self.is_running:
            if self.redis:
                # Store heartbeat timestamp in Redis
                await self.redis.hset("aegis:workers", self.worker_id, time.time())
            await asyncio.sleep(5)
