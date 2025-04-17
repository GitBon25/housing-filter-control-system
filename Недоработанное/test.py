import httpx
import asyncio

userMessage = "Ищу 2-комнатную квартиру во Владивостоке до 10 млн рублей площадью 60 м²"
res = httpx.post('http://127.0.0.1:8000/set-task', params={"data": userMessage})

data = res.json()
id = data["id"]

while True:
    #жду 5 секунд тк запрос обрабатывается не сразу и зачем лишняя нагрузка на сервер
    #await asyncio.sleep(5)
    task = httpx.get("http://127.0.0.1:8000/task/" + id)
    print(task)
    
    if not task: continue
    task = task.json()
    print(task)
    if task['status'] != "done": continue
    
    res = task['result']
    print(res)
    break