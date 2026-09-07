# Aegis AI Agent Orchestrator

A distributed multi-agent task execution engine with dynamic DAGs and self-healing capabilities, designed to showcase advanced engineering skills for technical interviews.

## 🌐 Live Interactive Demo
👉 **[Try the Live Web Dashboard Demo](https://devrot-ai.github.io/aegis-ai-agent-orchestrator/)**

## Overview
Aegis is a production-grade distributed system that demonstrates mastery of:
- Distributed systems engineering
- Real-time monitoring and visualization  
- Fault tolerance and self-healing capabilities
- Complex workflow orchestration
- Modern web technologies integration

## Key Features

- **Dynamic DAG Execution**: Build and execute complex workflows with dynamic task dependencies
- **Self-Healing Capabilities**: Automatic fault detection and recovery with transactional rollback
- **Real-time Monitoring**: WebSocket-based live telemetry with interactive Vis.js dashboard
- **Multi-Agent Support**: Register and execute custom agent handlers with retry mechanisms
- **Production-Grade Architecture**: Designed for scalability and reliability

## Usage

### Submit a Workflow (Local Backend)

```bash
curl -X POST http://localhost:8000/workflows/submit \
  -H "Content-Type: application/json" \
  -d '{"id": "sample-workflow", "nodes": [
    {"id": "task1", "agent": "researcher", "dependencies": []},
    {"id": "task2", "agent": "analyst", "dependencies": ["task1"]},
    {"id": "task3", "agent": "writer", "dependencies": ["task2"]}
  ]}'
```

## Technical Architecture

```
Frontend (React + Vis.js) ← WebSocket → Backend (FastAPI)
                                        ↓
                                    Agent Workers
```

## Repository Information

**GitHub**: [kanishkthakur24/aegis-ai-agent-orchestrator](https://github.com/devrot-ai/aegis-ai-agent-orchestrator)
**Live Dashboard Demo**: [https://devrot-ai.github.io/aegis-ai-agent-orchestrator/](https://devrot-ai.github.io/aegis-ai-agent-orchestrator/)

## Getting Started

### Prerequisites

```bash
python 3.11+
pip install fastapi uvicorn pydantic networkx websockets
```

### Run the Backend Server

```bash
python -m uvicorn projects.aegis.core.main:app --host 127.0.0.1 --port 8000
```
