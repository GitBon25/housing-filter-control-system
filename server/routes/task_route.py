from fastapi import APIRouter
router = APIRouter()

@router.post("/")
async def set_task(data: str):
    from server.controllers.task_controller import set_task
    return set_task(data)

@router.get("{task_id}")
async def get_task(id):
    from server.controllers.task_controller import get_task
    return task_controller.get_task(id)