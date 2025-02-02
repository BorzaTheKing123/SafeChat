import sqlite3

# Izberemo stvari iz baze
def select(query, typ):
    conn_to_db = sqlite3.connect('server/Database/accounts.db')
    c = conn_to_db.cursor()
    c.execute(query)
    if typ == 1:
        result = c.fetchone()
    else:
        result = c.fetchall()
    conn_to_db.close()
    return result


# Posodobimo stvari v bazi
def update(query) -> None:
    conn_to_db = sqlite3.connect('server/Database/accounts.db')
    c = conn_to_db.cursor()
    c.execute(query)
    conn_to_db.commit()
    conn_to_db.close()


# Vstavimo stvari v bazo
def insert(query) -> None:
    conn_to_db = sqlite3.connect('server/Database/accounts.db')
    c = conn_to_db.cursor()
    c.execute(query)
    conn_to_db.commit()
    conn_to_db.close()