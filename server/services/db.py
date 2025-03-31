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
    print("подключилось")
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
    
    
