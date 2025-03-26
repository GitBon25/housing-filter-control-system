import uvicorn
from taskQueue import add_task, get_res
from fastapi import FastAPI


app = FastAPI()

@app.post("/get-housing")
async def housing(data: str):
    id = add_task(data)
    return {
        "id": id
    }

@app.get("/task/{id}")
async def task(id):
    task = get_res(id)
    return task

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)