import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routes import task_route

app = FastAPI()
app.include_router(task_route.router, prefix="/task")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def start_server():
    uvicorn.run("server.server:app", host="127.0.0.1", port=8000, reload=True)

