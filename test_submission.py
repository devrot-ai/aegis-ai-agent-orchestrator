import httpx
import asyncio
import json

async def run_test():
    async with httpx.AsyncClient() as client:
        # 1. Check Health
        health = await client.get("http://127.0.0.1:8000/health")
        print(f"Health Check: {health.json()}")

        # 2. Submit Sample Workflow
        sample_dag = {
            "id": "test-dag-batman-1",
            "nodes": [
                { "id": "task-1", "agent": "researcher", "dependencies": [] },
                { "id": "task-2", "agent": "analyst", "dependencies": ["task-1"] },
                { "id": "task-3", "agent": "writer", "dependencies": ["task-2"] }
            ]
        }
        
        response = await client.post("http://127.0.0.1:8000/workflows/submit", json=sample_dag)
        print(f"Workflow Submission Response: {response.status_code}")
        print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    asyncio.run(run_test())
