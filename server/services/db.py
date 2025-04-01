import psycopg2
from psycopg2 import sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

env = {
    "user":  "postgres",
    "password": "1234",
    "dbname": "postgres",
    "host": "localhost",
    "port": "5432"
}

url = "postgresql://" + env["user"] + ':' + env["password"] + "@" + env["host"] + "/" + env["dbname"]
engine = create_engine(url)
Session = sessionmaker(bind=engine)

def connect(config: dict = {}):
    conf = env.copy()
    conf.update(config)
    
    conn = psycopg2.connect(**conf)
    return conn

def session(config: dict = {}):
    conf = env.copy()
    conf.update(config)
    
    session = Session()
    return session
def add_model(model, dbsession = session()):
    try:
        dbsession.add(model)
        dbsession.commit()
    except Exception as e:
        print(e)
        if dbsession: dbsession.rollback()
    finally:
        if dbsession: dbsession.close()
    
    
def get_aparts(ids: list, table_name = "apartments"):
    translations = {
        "description": "описание",
        "price": "цена",
        "rooms": "комнаты",
        "area": "площадь",
        "floor": "этаж",
        "location": "местоположение"
    }

    conn = connect()
    cursor = conn.cursor()

    result = []
        
    query = sql.SQL("SELECT * FROM {} WHERE id = ANY(%s)").format(
        sql.Identifier(table_name)
    )
    
    cursor.execute(query, (ids,))
    
    column_names = [desc[0] for desc in cursor.description]
    
    for row in cursor.fetchall():
        row_dict = dict(zip(column_names, row))
        result.append(row_dict)

    conn.close()


    translated_rows = []
    
    for row in result:
        filtered_row = {
            russian_key: row[english_key]
            for english_key, russian_key in translations.items()
            if english_key in row
        }
        translated_rows.append(filtered_row)
    
    return result, translated_rows


