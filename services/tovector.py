from server.services.db import connect, toDict
from server.services.db import add_vector, encode

conn = connect()
cur = conn.cursor()

last_id = 0
while True:
    cur.execute("SELECT * FROM apartments WHERE id > %s ORDER BY id LIMIT 100", (last_id,))
    rows = cur.fetchall()
    
    if not rows:
        break

    try:
        for row in rows:
            data = toDict(row, cur)
            
            id = data["id"]
            
            desc = data["description"]
            location = data["location"]
            
            
        
            last_id = data["id"]
    except Exception as e:
        print("ПОСЛЕДНИЙ id: ", last_id)
    finally:
        print("ПОСЛЕДНИЙ id: ", last_id)

conn.close()
cur.close()