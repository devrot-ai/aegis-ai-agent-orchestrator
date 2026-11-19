# Aegis AI Agent Orchestrator

A tool that lets you chain together different AI agents so they work on tasks in order, like an assembly line. If one agent fails, the system tries again on its own.

## Try It Live

You can see it working right now in your browser: [Live Dashboard Demo](https://devrot-ai.github.io/aegis-ai-agent-orchestrator/)

## What It Does

Imagine you have a big task that needs several steps. Maybe step one is research, step two is analysis, and step three is writing a report. Aegis takes care of running each step in the right order. It watches everything happen in real time on a dashboard. And if something breaks, it tries to fix itself.

Built with FastAPI on the backend and a React dashboard on the frontend, connected through WebSockets so you see updates as they happen.

## How to Use

Start the server first:

```bash
python -m uvicorn projects.aegis.core.main:app --host 127.0.0.1 --port 8000
```

Then send it a workflow. For example, a three-step task where each step depends on the one before:

```bash
curl -X POST http://localhost:8000/workflows/submit \
  -H "Content-Type: application/json" \
  -d '{"id": "sample-workflow", "nodes": [
    {"id": "task1", "agent": "researcher", "dependencies": []},
    {"id": "task2", "agent": "analyst", "dependencies": ["task1"]},
    {"id": "task3", "agent": "writer", "dependencies": ["task2"]}
  ]}'
```

The researcher runs first. Once it finishes, the analyst picks up. Then the writer creates the final output.

## Getting Started

You need Python 3.11 or newer. Install the dependencies:

```bash
pip install fastapi uvicorn pydantic networkx websockets
```

Then run the server command shown above and open the dashboard in your browser.

## How It Works

```
Dashboard (React) ← live updates → Server (FastAPI)
                                    ↓
                              Agent Workers
```

The dashboard talks to the server through WebSockets. The server hands off work to different agents. Each agent does its job and reports back.

## Links

- [GitHub Repository](https://github.com/devrot-ai/aegis-ai-agent-orchestrator)
- [Live Dashboard](https://devrot-ai.github.io/aegis-ai-agent-orchestrator/)
