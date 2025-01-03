import sqlite3

conn_to_db = sqlite3.connect('server/accounts.db')
c = conn_to_db.cursor()

c.execute('''CREATE TABLE accounts (username text, password text, token text, 
current_ip text)''')
conn_to_db.commit()

c.execute("INSERT  INTO accounts VALUES ('TheOperator', 'd404559f602eab6fd602ac7680dacbfaadd13630335e951f097af3900e9de176b6db28512f2e000b9d04fba5133e8b1c6e8df59db3a8ab9d60be4b97cc9e81db', '33813646572154400286170798894071', '192.168.178.144')")
conn_to_db.commit()
c.execute("INSERT  INTO accounts VALUES ('test', 'd404559f602eab6fd602ac7680dacbfaadd13630335e951f097af3900e9de176b6db28512f2e000b9d04fba5133e8b1c6e8df59db3a8ab9d60be4b97cc9e81db', '33813646572154400286170798894072', '192.168.178.144')")
conn_to_db.commit()

conn_to_db.close()