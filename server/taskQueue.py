import redis
import json
import uuid

r = redis.Redis()

def add_task(data: str):
    id = str(uuid.uuid4())
    task = {
        "id": id,
        "data": data,
        "status": "pending"
    }

    r.hset("tasks", id, json.dumps(task))

    r.lpush("task_queue", id)
    return task

def get_task_by_id(id: str):
    task = r.hget("tasks", id)
    if task:
        return json.loads(task)
    return { "error": "404, task not found" }

async def get_last_task():
    id = r.rpop("task_queue")
    if id:
        task = json.loads(r.hget("tasks", id))
        return task
    return None

def update_task(id, res):
    task = json.loads(r.hget("tasks", id))
    task = task | res
    r.hset("tasks", id, json.dumps(task))