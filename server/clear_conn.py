import sqlite3

conn_to_db = sqlite3.connect('server/accounts.db')
c = conn_to_db.cursor()

c.execute('''DROP TABLE connections''')
conn_to_db.commit()

c.execute('''CREATE TABLE connections (conn text, username text)''')
conn_to_db.commit()
conn_to_db.close()