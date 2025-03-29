import asyncio
from server.services.taskQueue import get_last_task, update_task
import logging, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bot.nlp_processor import HousingCriteriaExtractor
from services.url import find_flats

nlp_processor = HousingCriteriaExtractor()

def _format_response(criteria: dict) -> list[dict]:
    """Форматирование ответа"""
    global rooms, location, price, area
    rooms = criteria['rooms']
    location = criteria['location']
    price = criteria['price']
    area = criteria['area']
    return find_flats(rooms, price, area, location)


async def handle_message(msm):
    try:
        criteria = nlp_processor.extract_criteria(msm)
        flats = _format_response(criteria)

        return flats

    except Exception as e:
        logging.error(f"Ошибка обработки сообщения: {e}")
        return { "error": "error" }

async def worker():
    try:
        task = await get_last_task()
        if not task: return

        message = task['data']
        res = await handle_message(message)

        task['result'] = res
        task['status'] = 'done'
        await update_task(task['id'], task)
        print(f"Задача {task['id']} выполнена, статус обновлён.")
    except Exception as e:
        print(f"Oшибка: {e}")

async def main():
    print("Воркер запущен")
    while True:
        await worker()
        await asyncio.sleep(3)

asyncio.run(main())
