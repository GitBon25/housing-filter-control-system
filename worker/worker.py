import asyncio
from taskQueue import get_task, update_task

async def worker():
    while True:
        task = await get_task()
        if task:
            # парсинг и прочая долгая работа
            res = ""

async def main():
    await worker()

if __name__ == "__main__":
    asyncio.run(main())