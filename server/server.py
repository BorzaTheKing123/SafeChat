# Socket = is one endpoint of a two way communication link between two programs running on the network
# Don't use encryption beacuse it has eternqal error.

import socket
import threading
import sqlite3
import hashlib
import random

#print(hashlib.sha512(b"1234").hexdigest())

HEADER = 64 # Size of a message that will tell us how long will the acctual message be
PORT = 5070
FORMAT = 'utf-8'

SERVER = socket.gethostbyname(socket.gethostname()) # Gets ip automaticaly. Also here enter your public ip address to make it work outside home network
ADDR = (SERVER, PORT)
DISCONNECT_MESSAGE = "DISCONNECT_FROM_SERVER"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # We create a socket object --> .AF_INET is one of many different types
server.bind(ADDR)


def handle_client(conn, addr):
    print(f"New Connection --> {addr}") 

    conn_to_db = sqlite3.connect('server/accounts.db')
    c = conn_to_db.cursor()

    msg_length = conn.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        token = conn.recv(msg_length).decode(FORMAT) # Recieve data from client
        c.execute("SELECT token FROM accounts WHERE token='{}'".format(token))
        token_search = c.fetchone()
        print(token_search)
        if token_search == None:
            conn.send("!FALSE_TOKEN".encode(FORMAT))
            login = True
            while login:
                msg_length = conn.recv(HEADER).decode(FORMAT)
                if msg_length:
                    msg_length = int(msg_length)
                    try:
                        username, password = conn.recv(msg_length).decode(FORMAT).split(" ")
                        c.execute("SELECT password FROM accounts WHERE username='{}'".format(username))
                        psw = c.fetchone()
                        password = f"('{password}',)"
                        print(username, password, psw)
                        if password == str(psw):
                            print(True)
                            while True:
                                new_token = random.randrange(10000000000000000000000000000000, 99999999999999999999999999999999)
                                c.execute("SELECT * FROM accounts WHERE token='{}'".format(new_token))
                                check_token = c.fetchone()
                                if check_token == None:
                                    c.execute("UPDATE accounts SET token = '{}' WHERE username='{}'".format(new_token, username))
                                    conn_to_db.commit()
                                    conn.send(f"{new_token}".encode(FORMAT))
                                    break
                        else:
                            print(password)
                            conn.send("!INCORRECT_PASSWORD".encode(FORMAT))
                            break
                    except ValueError:
                        continue

#dodajanje povezav v bazo? ali sprotno povezovanje?
        else:
            conn.send("Connection accepted!".encode(FORMAT))
            connected = True
            while connected:
                msg_length = conn.recv(HEADER).decode(FORMAT) # Recieve how much data will we recieve from client (.decode(FORMAT) --> turns bits into string format)
                if msg_length:
                    msg_length = int(msg_length)
                    msg = conn.recv(msg_length).decode(FORMAT) # Recieve data from client
                    print(f"[{addr}] --> {msg}")
                    if msg == DISCONNECT_MESSAGE:
                        connected = False
                        print(f"Active Connectins --> {threading.active_count() - 1}")
                    conn.send("Message received!".encode(FORMAT))
    
    conn.close() # Closes connection


# Listens to devices that try to connect
def start():
    '''
    conn_to_db = sqlite3.connect('server/accounts.db')
    c = conn_to_db.cursor()

    c.execute("""CREATE TABLE accounts (username text, password text, token text)""")
    conn_to_db.commit()
    
    c.execute("INSERT  INTO accounts VALUES ('TheOperator', 'd404559f602eab6fd602ac7680dacbfaadd13630335e951f097af3900e9de176b6db28512f2e000b9d04fba5133e8b1c6e8df59db3a8ab9d60be4b97cc9e81db', '33813646572154400286170798894071')")
    conn_to_db.commit()
    conn_to_db.close()
    '''

    server.listen()
    print(f"Server is listening on {SERVER}")

    while True:
        conn, addr = server.accept() # Accepting devices that try to connect and getting info about it (addr --> ip adress, conn --> )
        thread = threading.Thread(target=handle_client, args=(conn, addr)) # We create a thread for a client that is trying to connect
        thread.start()
        print(f"Active Connectins --> {threading.active_count() - 1}") # How many clients are connected

print("Starting server!")
start()
