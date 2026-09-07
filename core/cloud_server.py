import os
import json
import asyncio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import networkx as nx

app = FastAPI(title="Aegis AI Agent Orchestrator - Live Cloud Node")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for active workflows
workflows_db = {}

class TaskNode(BaseModel):
    id: str
    type: str = "agent-task"
    agent: str
    dependencies: List[str] = Field(default_factory=list)
    params: Dict[str, Any] = Field(default_factory=dict)

class Workflow(BaseModel):
    id: str
    nodes: List[TaskNode]

class TelemetryManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.connections.remove(ws)

    async def broadcast(self, event: str, data: dict):
        message = json.dumps({"event": event, "data": data})
        dead = []
        for conn in self.connections:
            try:
                await conn.send_text(message)
            except:
                dead.append(conn)
        for d in dead:
            self.disconnect(d)

telemetry = TelemetryManager()

def validate_dag(workflow: Workflow):
    G = nx.DiGraph()
    for node in workflow.nodes:
        G.add_node(node.id)
        for dep in node.dependencies:
            G.add_edge(dep, node.id)
    if not nx.is_directed_acyclic_graph(G):
        raise ValueError("Workflow contains cycles and is not a valid DAG.")
    return list(nx.topological_sort(G))

@app.post("/api/workflows/submit")
async def submit_workflow(workflow: Workflow):
    try:
        plan = validate_dag(workflow)
        workflows_db[workflow.id] = {"workflow": workflow, "plan": plan}
        
        await telemetry.broadcast("WORKFLOW_SUBMITTED", {
            "workflow_id": workflow.id,
            "plan": plan
        })

        # Run workflow execution in background
        asyncio.create_task(execute_cloud_workflow(workflow, plan))

        return {"status": "accepted", "workflow_id": workflow.id, "execution_plan": plan}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

async def execute_cloud_workflow(workflow: Workflow, plan: List[str]):
    node_map = {n.id: n for n in workflow.nodes}
    
    for task_id in plan:
        task = node_map[task_id]
        
        # 1. RUNNING
        await telemetry.broadcast("TASK_STATUS", {
            "workflow_id": workflow.id,
            "task_id": task_id,
            "status": "RUNNING"
        })
        await asyncio.sleep(1.2)

        # Simulate agent execution & self-healing resilience
        if task.agent == "analyst" and workflow.id.endswith("fail"):
            # Trigger self-healing / retry
            await telemetry.broadcast("TASK_STATUS", {
                "workflow_id": workflow.id,
                "task_id": task_id,
                "status": "FAILED",
                "error": "LLM rate limit encountered. Initiating fallback agent..."
            })
            await asyncio.sleep(1.0)
            # Recovered
            await telemetry.broadcast("TASK_STATUS", {
                "workflow_id": workflow.id,
                "task_id": task_id,
                "status": "COMPLETED",
                "result": {"output": "Self-heal fallback succeeded: backup model routed."}
            })
        else:
            await telemetry.broadcast("TASK_STATUS", {
                "workflow_id": workflow.id,
                "task_id": task_id,
                "status": "COMPLETED",
                "result": {"output": f"Agent {task.agent} executed successfully."}
            })
        await asyncio.sleep(0.5)

    await telemetry.broadcast("WORKFLOW_COMPLETED", {"workflow_id": workflow.id})

@app.websocket("/ws/telemetry")
async def websocket_endpoint(ws: WebSocket):
    await telemetry.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        telemetry.disconnect(ws)

@app.get("/health")
async def health():
    return {"status": "healthy", "engine": "Aegis Cloud Orchestrator"}

# Mount static files for dashboard if present
if os.path.exists("dashboard"):
    app.mount("/", StaticFiles(directory="dashboard", html=True), name="dashboard")
