import sqlite3
import random
c_token = random.randrange(10000000000000000000000000000000, 99999999999999999999999999999999)
conn_to_db = sqlite3.connect('accounts.db')
c = conn_to_db.cursor()
addr = '192.168.178.144'
token = '17199267902585703679444574753483'
# Poskusi spremeniti ena po eno
c.execute("UPDATE accounts SET connection_token = '{}', current_ip = '{}' WHERE token='{}'".format(c_token,
                                                                                                   addr, token))
conn_to_db.commit()
