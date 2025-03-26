import redis
import asyncio
import json
import uuid

r = redis.Redis()
task_queue = asyncio.Queue()

def add_task(data: str):
    id = str(uuid.uuid4())
    task = {
        "id": id,
        "data": data,
        "status": "pending" | "done"
    }

    r.hset("tasks", id, json.dumps(task))

    r.lpush("task_queue", id)
    return task

def get_res(id: str):
    task = r.hget("tasks", id)
    if task:
        return json.loads(task)
    return { "error": "404, task not found" }

async def get_task():
    id = await task_queue.get()
    if id:
        task = json.lods(r.hget("tasks", id))
        return task
    else:
        return None

def update_task(id, res):
    task = json.loads(r.hget("tasks", id))
    task = task | res
    r.hset("tasks", id, json.dumps(task))