import uvicorn
from taskQueue import add_task, get_task_by_id
from fastapi import FastAPI


app = FastAPI()

@app.post("/set-task")
async def housing(data: str):
    res = add_task(data)
    return res

@app.get("/task/{id}")
async def task(id):
    task = get_task_by_id(id)
    return task

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)