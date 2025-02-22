import sqlite3

# Poveže se z bazo
conn_to_db = sqlite3.connect('server/Database/accounts.db')
c = conn_to_db.cursor()

# Ustvari tabelo za uporabnike
c.execute('''CREATE TABLE accounts (username text, password text, token text, 
current_ip text)''')
conn_to_db.commit()

# Vstavi testnega uporabnika z geslom 1234
c.execute("INSERT  INTO accounts VALUES ('test', 'd404559f602eab6fd602ac7680dacbfaadd13630335e951f097af3900e9de176b6db28512f2e000b9d04fba5133e8b1c6e8df59db3a8ab9d60be4b97cc9e81db', 'a07c2b89aa67f5c440094278beeb9675f3f847e5335ce5ec856fcf03db545c24aaf67e67dfb212a3c13e45eefcd48291db1adfd8628da2117fa0066852be2f03', '192.168.178.144')")
conn_to_db.commit()

conn_to_db.close()