import uvicorn
import asyncio
from services.db import connect, create_table
from fastapi import FastAPI
#from routes import task_route

app = FastAPI()

#app.include_router(task_route.router, prefix="/task")

async def p():
    conn = await connect()
    print(conn)
    await create_table()
if __name__ == "__main__":
    #uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

    asyncio.run(p())

