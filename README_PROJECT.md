# Aegis AI Agent Orchestrator

## Project Overview

A distributed multi-agent task execution engine with dynamic DAGs and self-healing capabilities, designed to showcase advanced engineering skills for technical interviews.

## Key Features

- **Dynamic DAG Execution**: Build and execute complex workflows with dynamic task dependencies
- **Self-Healing Capabilities**: Automatic fault detection and recovery with transactional rollback
- **Real-time Monitoring**: WebSocket-based live telemetry with interactive Vis.js dashboard
- **Multi-Agent Support**: Register and execute custom agent handlers with retry mechanisms
- **Production-Grade Architecture**: Designed for scalability and reliability

## Technical Stack

- **Backend**: FastAPI, Python 3.11
- **Concurrency**: asyncio, NetworkX, Pydantic
- **Real-time**: WebSocket, Vis.js
- **Storage**: In-memory execution planning
- **Monitoring**: Custom telemetry events

## Live Demo

The core Aegis server is running at: `http://localhost:8000`

**Dashboard**: `http://localhost:8000/dashboard/index.html`

**Health Check**: `http://localhost:8000/health`

**API Endpoint**: `http://localhost:8000/workflows/submit`

## Example Usage

Submit a multi-node workflow:

```bash
curl -X POST http://localhost:8000/workflows/submit \
  -H "Content-Type: application/json" \
  -d '{"id": "batman-investigation", "nodes": [
    {"id": "fetch-news", "agent": "researcher", "dependencies": []},
    {"id": "analyze-patterns", "agent": "analyst", "dependencies": ["fetch-news"]},
    {"id": "generate-report", "agent": "writer", "dependencies": ["analyze-patterns"]}
  ]}'
```

## Interview Impact

This project demonstrates:

- ✅ Distributed systems expertise (DAG execution)
- ✅ Production fault tolerance (self-healing)
- ✅ Real-time monitoring capabilities
- ✅ Modern web technologies integration
- ✅ Comprehensive error handling and recovery
- ✅ Advanced Python engineering practices

## Repository Links

- **GitHub Repository**: [Aegis AI Agent Orchestrator](https://github.com/KanishkThakur24/aegis-ai-agent-orchestrator)
- **Live Demo**: http://localhost:8000/dashboard/index.html
- **API Documentation**: Available via `/docs` endpoint

## Development Status

- ✅ **Phase 1-4 Completed**: Core implementation
- ✅ **Live Server Running**: Verification successful
- ✅ **Interactive Dashboard**: Ready for demonstration
- ✅ **Testing Verified**: Workflow submission and execution

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install fastapi uvicorn pydantic networkx websockets`
3. Run the server: `python -m uvicorn projects.aegis.core.main:app --host 127.0.0.1 --port 8000`
4. Access dashboard: Open `http://localhost:8000/dashboard/index.html` in your browser

## Future Enhancements

- [ ] Redis/NATS integration for distributed scaling
- [ ] Kubernetes deployment scripts
- [ ] Advanced agent lifecycle management
- [ ] Cloud provider integration
- [ ] Comprehensive benchmarking suite

## Contact

For questions or collaboration, reach out via GitHub repository or LinkedIn.