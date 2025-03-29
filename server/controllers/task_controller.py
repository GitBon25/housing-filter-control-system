import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server.services.taskQueue import add_task, get_task_by_id

def set_task(data):
    return add_task(data)
def get_task():
    return get_task_by_id(id)