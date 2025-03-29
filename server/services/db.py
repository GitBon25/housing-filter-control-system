import psycopg2
from psycopg2 import sql

async def connect():
    conn = psycopg2.connect(
        user="postgres",
        password="1234",
        dbname="postgres",
        host="localhost",
        port="5432",
    )
    print("подключилось")
    return conn

async def session():
    # создай сессию
    a =1

async def add_model(model):
    conn = await connect()
    cursor = conn.cursor()

    table = model.tableName

    conn.close()
