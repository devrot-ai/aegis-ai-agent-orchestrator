# Aegis AI Agent Orchestrator - Technical Design Document

## 1. System Architecture

```
                          +-------------------+
                          |  Aegis Dashboard  | (React / D3.js)
                          +---------+---------+
                                    | WebSockets
                          +---------v---------+
                          |   Aegis Gateway   | (REST/WS Server)
                          +---------+---------+
                                    |
            +-----------------------+-----------------------+
            | NATS / Redis PubSub                           | NATS / Redis PubSub
  +---------v---------+                           +---------v---------+
  |   Aegis Worker    |                           |   Aegis Worker    |
  |  (Node / Agent 1) |                           |  (Node / Agent 2) |
  +---------+---------+                           +---------+---------+
            |                                               |
  +---------v---------+                           +---------v---------+
  |   Local Engine    |                           |   Local Engine    |
  |   (Go / Rust)     |                           |   (Go / Rust)     |
  +-------------------+                           +-------------------+
```

The system is split into three main components:
1. **The Orchestrator Core (Go/Rust)**: Manages state, DAG topology, scheduling, rollback logs, and heartbeats.
2. **The Worker Daemon (Python/Node)**: Executes individual task nodes (e.g., calling an LLM, searching a vector DB, running shell commands, parsing files).
3. **The Web Console (React/D3)**: Real-time graphical visualization of task dependencies, execution state, performance metrics, and log streams.

---

## 2. Dynamic DAG Topology

In Aegis, a workflow is defined as a Directed Acyclic Graph (DAG) using a JSON definition:

```json
{
  "workflow_id": "batman-investigation-101",
  "nodes": [
    {
      "id": "fetch-news",
      "type": "agent-task",
      "agent": "researcher",
      "params": { "query": "Gotham cyber attacks" }
    },
    {
      "id": "analyze-patterns",
      "type": "agent-task",
      "agent": "analyst",
      "dependencies": ["fetch-news"],
      "params": { "depth": "high" }
    },
    {
      "id": "generate-report",
      "type": "agent-task",
      "agent": "writer",
      "dependencies": ["analyze-patterns"],
      "params": { "format": "markdown" }
    }
  ]
}
```

### Self-Healing & Transactional Rollback
If a node fails (e.g., `analyze-patterns` fails due to an LLM timeout or unexpected input):
1. **Retry Policies**: Execute progressive backoff-and-retry.
2. **Self-Healing Route**: Spawn a sub-agent to fix the issue (e.g., a "Format Fixer" or "API Router Selection" agent).
3. **Compensation & Rollback**: If the task cannot be completed, execute compensation tasks in reverse order of DAG execution (like Saga Pattern in Microservices) to ensure data/state integrity.

---

## 3. High-Performance Orchestrator Implementation Strategy (Go)

We will implement the Core Orchestrator in **Go** due to its outstanding concurrency support (goroutines/channels) and standard-library networking features, ensuring maximum performance and execution speed.

### Core Structure Outline

- `main.go`: Gateway entrypoint.
- `pkg/dag/dag.go`: Validates DAG cycles (Tarjan's/Kahn's algorithm), tracks task statuses (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `COMPENSATING`).
- `pkg/scheduler/scheduler.go`: Distributes ready tasks to worker nodes via channels/Redis PubSub.
- `pkg/recovery/recovery.go`: Tracks compensating tasks, state snapshots, and rollback transactions.
