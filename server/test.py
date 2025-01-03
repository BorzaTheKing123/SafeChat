import sqlite3

def select(command, typ):
    conn_to_db = sqlite3.connect('server/accounts.db')
    c = conn_to_db.cursor()
    c.execute(command)
    if typ == 1:
        result = c.fetchone()
    else:
        result = c.fetchall()
    conn_to_db.close()
    return result


res = select("SELECT * FROM accounts WHERE username='{}'".format("TheOperator"), 1)
print(res)