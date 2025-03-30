import uvicorn
import asyncio
from fastapi import FastAPI
from routes import task_route

app = FastAPI()
app.include_router(task_route.router, prefix="/task")

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)

