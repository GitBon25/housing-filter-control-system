from fastapi import APIRouter
from fastapi import Request
from server.controllers import task_controller
router = APIRouter()

@router.post("/")
async def stask(req: Request):
    data = await req.json()
    from server.controllers.task_controller import set_task
    return set_task(data["text"])

@router.get("/{task_id}")
async def gtask(task_id):
    from server.controllers.task_controller import get_task
    return task_controller.get_task(task_id)