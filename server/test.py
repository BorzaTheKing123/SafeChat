import sqlite3
conn_to_db = sqlite3.connect('server/accounts.db')
c = conn_to_db.cursor()
c.execute("SELECT password FROM accounts WHERE username='{}'".format("TheOperator"))
psw = c.fetchone()
password = "d404559f602eab6fd602ac7680dacbfaadd13630335e951f097af3900e9de176b6db28512f2e000b9d04fba5133e8b1c6e8df59db3a8ab9d60be4b97cc9e81db"
password = f"('{password}',)"
print("TheOperator", type(password), type(psw))