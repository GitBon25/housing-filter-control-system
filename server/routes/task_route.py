import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import APIRouter
from server.controllers import task_controller


router = APIRouter()

@router.post("/")
async def set_task(data: str):
    return task_controller.set_task(data)

@router.get("{task_id}")
async def get_task(id):
    return task_controller.get_task(id)