import asyncio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .models import Workflow
from .engine import AegisEngine
from .telemetry import telemetry
from .recovery import SelfHealingEngine
from .worker import AegisWorker

app = FastAPI(title="Aegis AI Orchestrator Core")

# Enable CORS for local Dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = AegisEngine()
recovery_engine = SelfHealingEngine(engine)

# Initialize a default worker instance for local processing
worker = AegisWorker(worker_id="worker-node-1")

# Register dummy handlers
async def researcher_handler(params):
    await asyncio.sleep(1)
    return {"data": "Found 5 threat signals in Gotham digital feeds."}

async def analyst_handler(params):
    await asyncio.sleep(1)
    return {"threat_level": "HIGH", "location": "Narrows"}

async def writer_handler(params):
    await asyncio.sleep(1)
    return {"report": "Gotham Security Advisory: Heightened vigilance recommended."}

worker.register_agent("researcher", researcher_handler)
worker.register_agent("analyst", analyst_handler)
worker.register_agent("writer", writer_handler)


@app.post("/workflows/submit")
async def submit_workflow(workflow: Workflow):
    try:
        execution_plan = engine.validate_dag(workflow)
        
        # Broadcast submission event to connected clients
        await telemetry.broadcast_event("WORKFLOW_SUBMITTED", {
            "workflow_id": workflow.id,
            "plan": execution_plan
        })

        # Run execution asynchronously
        asyncio.create_task(run_workflow_execution(workflow, execution_plan))

        return {
            "status": "accepted",
            "workflow_id": workflow.id,
            "execution_plan": execution_plan
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def run_workflow_execution(workflow: Workflow, execution_plan: list):
    """Executes tasks in topological order and streams real-time status."""
    node_map = {node.id: node for node in workflow.nodes}

    for task_id in execution_plan:
        task_node = node_map[task_id]
        
        # Stream RUNNING status
        await telemetry.broadcast_event("TASK_STATUS", {
            "workflow_id": workflow.id,
            "task_id": task_id,
            "status": "RUNNING"
        })

        status = await worker.execute_task(task_node)

        # Stream Task Result
        await telemetry.broadcast_event("TASK_STATUS", {
            "workflow_id": workflow.id,
            "task_id": task_id,
            "status": status.status,
            "result": status.result,
            "error": status.error
        })

        if status.status == "COMPLETED":
            recovery_engine.record_completed_task(workflow.id, task_id)
        else:
            # Trigger Self-Healing / Rollback
            healed = await recovery_engine.handle_node_failure(
                workflow.id, task_node, status.error or "Unknown error"
            )
            if not healed:
                await telemetry.broadcast_event("WORKFLOW_FAILED", {
                    "workflow_id": workflow.id,
                    "failed_node": task_id
                })
                return

    await telemetry.broadcast_event("WORKFLOW_COMPLETED", {
        "workflow_id": workflow.id
    })


@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await telemetry.connect(websocket)
    try:
        while True:
            # Keep connection open and listen for messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        telemetry.disconnect(websocket)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "aegis-core"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
