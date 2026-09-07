import asyncio
import heapq
from typing import Dict, List, Set
from .models import TaskNode, Workflow, TaskStatus

class AegisScheduler:
    def __init__(self):
        self.active_workflows: Dict[str, Workflow] = {}
        self.task_status: Dict[str, TaskStatus] = {}
        self.worker_assignments: Dict[str, str] = {}
        self.priority_queue: List[tuple] = []
        self.running_tasks: Set[str] = set()
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()

    def add_workflow(self, workflow: Workflow):
        """Adds a workflow to the scheduler."""
        self.active_workflows[workflow.id] = workflow
        print(f"[Scheduler] Added workflow: {workflow.id}")

    def calculate_task_priority(self, task: TaskNode, workflow: Workflow) -> float:
        """
        Calculate task priority based on:
        - Number of dependencies (fewer = higher priority)
        - Agent type (system-critical agents first)
        - Estimated complexity (placeholder for actual estimation)
        """
        base_priority = len(task.dependencies)
        
        # Boost priority for critical agents
        critical_agents = {"researcher", "analyst", "writer"}
        if task.agent in critical_agents:
            base_priority -= 2
            
        # Reduce priority for long-running tasks
        if task.agent in {"researcher"}:
            base_priority += 1
            
        return base_priority

    def schedule_workflow(self, workflow: Workflow):
        """Schedules all tasks in a workflow based on dependencies."""
        task_map = {node.id: node for node in workflow.nodes}
        
        # Initialize task status for all tasks
        for task in workflow.nodes:
            self.task_status[task.id] = TaskStatus(
                task_id=task.id,
                status="PENDING",
                worker_id=None
            )
        
        # Build dependency graph
        dependencies = {task.id: set(task.dependencies) for task in workflow.nodes}
        
        # Calculate in-degree (number of dependencies)
        in_degree = {task.id: len(deps) for task, deps in dependencies.items()}
        
        # Initialize priority queue
        self.priority_queue.clear()
        for task_id, degree in in_degree.items():
            if degree == 0:
                priority = self.calculate_task_priority(task_map[task_id], workflow)
                heapq.heappush(self.priority_queue, (priority, task_id))
                self.task_status[task_id].status = "READY"
        
        print(f"[Scheduler] Workflow {workflow.id} scheduled. Ready tasks: {len(self.priority_queue)}")

    async def execute_scheduled(self, worker_handler):
        """Executes ready tasks using the provided worker handler."""
        while self.priority_queue:
            # Get highest priority task (lowest number)
            priority, task_id = heapq.heappop(self.priority_queue)
            
            if task_id in self.running_tasks or task_id in self.completed_tasks:
                continue
                
            task = next((t for t in self.active_workflows.values() 
                        for t in t.nodes if t.id == task_id), None)
            if not task:
                continue
                
            # Assign worker
            self.running_tasks.add(task_id)
            self.task_status[task_id].status = "RUNNING"
            self.worker_assignments[task_id] = f"worker-{len(self.worker_assignments) + 1}"
            self.task_status[task_id].worker_id = self.worker_assignments[task_id]
            
            print(f"[Scheduler] Executing task {task_id} with priority {priority} on worker {self.worker_assignments[task_id]}")
            
            # Execute task using worker
            result = await worker_handler(task)
            
            # Update status
            self.task_status[task_id].status = result.status
            self.task_status[task_id].result = result.result
            self.task_status[task_id].error = result.error
            
            if result.status == "COMPLETED":
                self.completed_tasks.add(task_id)
                print(f"[Scheduler] Task {task_id} completed successfully")
                
                # Check for dependent tasks that can now be scheduled
                for dependent_task in self.active_workflows.values():
                    for node in dependent_task.nodes:
                        if node.id != task_id and task_id in node.dependencies:
                            # Check if all dependencies are completed
                            remaining_deps = [d for d in node.dependencies if d not in self.completed_tasks]
                            if not remaining_deps:
                                # Schedule this dependent task
                                dep_priority = self.calculate_task_priority(node, dependent_task)
                                heapq.heappush(self.priority_queue, (dep_priority, node.id))
                                self.task_status[node.id].status = "READY"
                                print(f"[Scheduler] Dependent task {node.id} is now READY")
            else:
                self.failed_tasks.add(task_id)
                print(f"[Scheduler] Task {task_id} failed: {result.error}")
            
            self.running_tasks.remove(task_id)
            
            # Small delay to simulate processing time
            await asyncio.sleep(0.5)
        
        print(f"[Scheduler] Workflow execution completed. Total completed: {len(self.completed_tasks)}, Total failed: {len(self.failed_tasks)}")

    def get_workflow_status(self, workflow_id: str) -> Dict:
        """Returns detailed status of a workflow."""
        if workflow_id not in self.active_workflows:
            return {"error": "Workflow not found"}
            
        workflow = self.active_workflows[workflow_id]
        
        return {
            "workflow_id": workflow_id,
            "total_tasks": len(workflow.nodes),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "pending_tasks": len(self.priority_queue),
            "running_tasks": len(self.running_tasks),
            "task_statuses": {k: v.dict() for k, v in self.task_status.items()}
        }
