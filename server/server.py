# Socket = is one endpoint of a two-way communication link between two programs running on the network
# Don't use encryption because it has eternal error.

import socket
import threading
import sqlite3
import random

# import hashlib

# print(hashlib.sha512(b"1234").hexdigest())

HEADER = 64  # Size of a message that will tell us how long will the actual message be
PORT = 5068
CLIENT_PORT = 5072
FORMAT = 'utf-8'

SERVER = socket.gethostbyname(socket.gethostname())  # Gets ip automatically.
ADDR = (SERVER, PORT)
DISCONNECT_MESSAGE = "DISCONNECT_FROM_SERVER"

server = socket.socket(socket.AF_INET,
                       socket.SOCK_STREAM)  # We create a socket object --> .AF_INET is one of many different types
server.bind(ADDR)


def connection_token(token, addr):
    c_token = random.randrange(10000000000000000000000000000000, 99999999999999999999999999999999)
    conn_to_db = sqlite3.connect('accounts.db')
    c = conn_to_db.cursor()
    # Poskusi spremeniti ena po eno
    c.execute("UPDATE accounts SET connection_token = '{}', current_ip = '{}' WHERE token='{}'".format(c_token,
                                                                                                       f"{addr[0]}", token))
    conn_to_db.commit()
    c.close()
    return f'{c_token}'


def get_target_info(user):
    conn_to_db = sqlite3.connect('accounts.db')
    c = conn_to_db.cursor()
    c.execute("SELECT connection_token, current_ip FROM accounts WHERE username='{}'".format(user))
    res = c.fetchone()
    if res is not None:
        ct, current_ip = res[0], res[1]
        return ct ,current_ip
    else:
        return 0, 0 # Spomni se česa boljšga


def send(msg ,C_ADDR):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(C_ADDR)

    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT) # We get length of the message we want to send
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    return client.recv(1024).decode(FORMAT)


def handle_client(conn, addr):
    print(f"New Connection --> {addr}")

    conn_to_db = sqlite3.connect('accounts.db')
    c = conn_to_db.cursor()

    msg_length = conn.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        token = conn.recv(msg_length).decode(FORMAT)  # Recieve data from client
        print(token)
        c.execute("SELECT username FROM accounts WHERE token='{}'".format(token))
        rec = c.fetchone()
        print(rec)
        if rec is None:
            conn.send("!FALSE_TOKEN".encode(FORMAT))
            count = 0
            while count < 3:
                msg_length = conn.recv(HEADER).decode(FORMAT)
                if msg_length:
                    msg_length = int(msg_length)
                    try:
                        username, password, log_or_reg = conn.recv(msg_length).decode(FORMAT).split(" ")
                        if log_or_reg == "1":
                            c.execute("SELECT password FROM accounts WHERE username='{}'".format(username))
                            psw = c.fetchone()
                            password = f"('{password}',)"
                            print(username, password, psw)
                            if password == str(psw):
                                while True:
                                    new_token = random.randrange(10000000000000000000000000000000,
                                                                 99999999999999999999999999999999)
                                    c.execute("SELECT * FROM accounts WHERE token='{}'".format(new_token))
                                    check_token = c.fetchone()
                                    if check_token is None:
                                        c.execute(
                                            "UPDATE accounts SET token = '{}' WHERE username='{}'".format(new_token,
                                                                                                          username))
                                        conn_to_db.commit()
                                        conn.send(f"{new_token}".encode(FORMAT))
                                        break
                                break
                            else:
                                print(password)
                                conn.send("!INCORRECT_PASSWORD".encode(FORMAT))
                                count += 1
                        else:
                            c.execute("SELECT username FROM accounts WHERE username='{}'".format(username))
                            usr = c.fetchone()
                            if usr is not None:
                                conn.send("Username already exists!".encode(FORMAT))
                                count += 1
                            elif len(username) == 0:
                                conn.send("Username is too short!".encode(FORMAT))
                                count += 1
                            else:
                                while True:
                                    new_token = random.randrange(10000000000000000000000000000000,
                                                                 99999999999999999999999999999999)
                                    c.execute("SELECT * FROM accounts WHERE token='{}'".format(new_token))
                                    check_token = c.fetchone()
                                    if check_token is None:
                                        c.execute(
                                            "INSERT INTO accounts VALUES ('{}', '{}', '{}')".format(username, password,
                                                                                                    new_token))
                                        conn_to_db.commit()
                                        conn.send(f"{new_token}".encode(FORMAT))
                                        break
                                break
                    except ValueError:
                        break
            else:
                conn.send(DISCONNECT_MESSAGE.format(FORMAT))

        else:
            username = rec[0]
            conn.send(connection_token(token, addr).encode(FORMAT))
            while True:
                msg_length = conn.recv(HEADER).decode(FORMAT)  # Receive how much data will we recieve from client
                if msg_length:
                    msg_length = int(msg_length)
                    rec = conn.recv(msg_length).decode(FORMAT)  # Receive data from client
                    print(rec)
                    user, msg = rec.split(" !==> ")
                    if msg == DISCONNECT_MESSAGE:
                        break
                    else:
                        if user != "" or " " not in user:
                            con_token, ip = get_target_info(user)
                            C_ADDR = (ip, CLIENT_PORT)
                            ms = f"{con_token} !==> {username} !==> {msg}"
                            conn.send(send(ms, C_ADDR).encode(FORMAT))
                        else:
                            conn.send("Incorrect username!")
    conn.close()  # Closes connection
    conn_to_db.close()  # Closes database
"""
Some code, if I am going to make a better experience with saved friends an like
                    if msg == DISCONNECT_MESSAGE:
                        connected = False
                        print(f"Active Connectins --> {threading.active_count() - 2}")
                    elif msg == "!NEW_FRIEND":
                        msg_length = conn.recv(HEADER).decode(FORMAT)
                        if msg_length:
                            msg_length = int(msg_length)
                            msg = conn.recv(msg_length).decode(FORMAT)
                            c.execute("SELECT * FROM accounts WHERE username='{}'".format(msg))
                            check_token = c.fetchone()
                            if check_token is None:
                                conn.send("!NO_USER".format(FORMAT))
                            else:
                                pass
                    else:
                        break
                    conn.send("Message received!".encode(FORMAT))
"""


# Listens to devices that try to connect
def start():
    """
    conn_to_db = sqlite3.connect('accounts.db')
    c = conn_to_db.cursor()

    c.execute('''CREATE TABLE accounts (username text, password text, token text, connection_token text, 
    current_ip text)''')
    conn_to_db.commit()

    c.execute("INSERT  INTO accounts VALUES ('TheOperator', 'd404559f602eab6fd602ac7680dacbfaadd13630335e951f097af3900e9de176b6db28512f2e000b9d04fba5133e8b1c6e8df59db3a8ab9d60be4b97cc9e81db', '33813646572154400286170798894071', '0', '192.168.178.144')")
    conn_to_db.commit()
    conn_to_db.close()
    """

    server.listen()
    print(f"Server is listening on {SERVER}")

    while True:
        conn, addr = server.accept()  # Accepting devices that try to connect and getting info about it (addr --> ip adress, conn --> )
        thread = threading.Thread(target=handle_client,
                                  args=(conn, addr))  # We create a thread for a client that is trying to connect
        thread.start()
        print(f"\nActive Connectins --> {threading.active_count() - 1}")  # How many clients are connected


print("Starting server!")
start()
