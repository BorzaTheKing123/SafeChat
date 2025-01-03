# Socket = is one endpoint of a two-way communication link between two programs running on the network

import socket
import threading
import sqlite3
import random
# import hashlib

# print(hashlib.sha512(b"1234").hexdigest())

HEADER = 64  # Size of a message that will tell us how long will the actual message be
CLIENT_PORT = 5072
FORMAT = 'utf-8'

SERVER = socket.gethostbyname(socket.gethostname())  # Gets ip automatically.
DISCONNECT_MESSAGE = "!DISCONNECT_FROM_SERVER"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # We create a socket object --> .AF_INET is one of many different types
active_connections = {} # Shrani aktivne povezave


# Izberemo stvari iz baze
def select(query, typ):
    conn_to_db = sqlite3.connect('server/accounts.db')
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
    conn_to_db = sqlite3.connect('server/accounts.db')
    c = conn_to_db.cursor()
    c.execute(query)
    conn_to_db.commit()
    conn_to_db.close()


# Vstavimo stvari v bazo
def insert(query) -> None:
    conn_to_db = sqlite3.connect('server/accounts.db')
    c = conn_to_db.cursor()
    c.execute(query)
    conn_to_db.commit()
    conn_to_db.close()


# Pridobi informacije o uporabniku
def get_target_info(user):
    if user in active_connections:
        return active_connections[user]
    else:
        return 0


# Pošlje sporočilo
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


# Prijava uporabnika
def login(username, password):
    psw = select("SELECT password FROM accounts WHERE username='{}'".format(username), 1)
    password = f"('{password}',)"
    print(username, password, psw)
    if password == str(psw):
        while True:
            new_token = random.randrange(10000000000000000000000000000000, 99999999999999999999999999999999)
            check_token = select("SELECT * FROM accounts WHERE token='{}'".format(new_token), 1)
            if check_token is None:
                update("UPDATE accounts SET token = '{}' WHERE username='{}'".format(new_token, username))
                return new_token
    else:
        return "!INCORRECT_PASSWORD"


# Registracija uporabnika
def register(username, password):
    usr = select("SELECT username FROM accounts WHERE username='{}'".format(username), 1)
    if usr is not None:
        return "Username already exists!"
        count += 1
    elif len(username) == 0:
        return "Username is too short!"
        count += 1
    else:
        while True:
            new_token = random.randrange(10000000000000000000000000000000, 99999999999999999999999999999999)
            check_token = select("SELECT * FROM accounts WHERE token='{}'".format(new_token), 1)
            if check_token is None:
                insert("INSERT INTO accounts VALUES ('{}', '{}', '{}')".format(username, password, new_token))
                return new_token


# Sprejme sporočilo
def receive(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)  # Pridobi dolžino sporočila
    if msg_length:
        msg_length = int(msg_length)
        rec = conn.recv(msg_length).decode(FORMAT)  # Prido sporočilo
        return rec


# Ko je uporabnik povezan mu omogoča pošiljanje sporočil
def send_msg(sender_conn, sender_username):
    while True:
        rec = receive(sender_conn)
        if rec is None:
            active_connections.pop(sender_username)
            break
        else:
            try:
                user, msg = rec.split(" !==> ")

                if msg == DISCONNECT_MESSAGE:
                    return
                
                if " " not in user:
                    conn = get_target_info(user)
                    ms = f"{sender_username} !==> {msg}"
                    if conn != 0:
                        try:
                            conn.send(ms.encode(FORMAT))
                            sender_conn.send("Message sent!".encode(FORMAT))
                        except OSError:
                            sender_conn.send("User is unavaliable!".encode(FORMAT))
                            active_connections.pop(user)
                    else:
                        sender_conn.send("User is unavaliable!".encode(FORMAT))
                else:
                    sender_conn.send("Incorrect username!".encode(FORMAT))

            except ValueError:
                sender_conn.send("->".encode(FORMAT))


# Obdelava povezave
def handle_client(conn, addr):
    print(f"New Connection --> {addr}")
    
    token = receive(conn) # Pridobi token od uporabnika
    rec = select("SELECT username FROM accounts WHERE token='{}'".format(token), 1)

    if rec is None:
        conn.send("!FALSE_TOKEN".encode(FORMAT))
        count = 0

        # Skrbi za prijavo in registracijo
        while count < 3:
            try:
                username, password, log_or_reg = receive(conn).split(" ")

                # Prijava uporabnika
                if log_or_reg == "1":
                    login_attempt = login(username, password)
                    if login_attempt == "!INCORRECT_PASSWORD":
                        count += 1
                    conn.send(f"{login_attempt}".encode(FORMAT))
                
                # Registracija uporabnika
                else:
                    register_attempt = register(username, password)
                    if not register_attempt.isnumeric():
                        count += 1
                    conn.send(f"{register_attempt}".encode(FORMAT))

            except ValueError:
                break
        else:
            conn.send(DISCONNECT_MESSAGE.format(FORMAT))

    # Če je token pravilen
    else:
        active_connections[rec[0]] = conn # Doda novo povezavo
        conn.send("Connected!".encode(FORMAT))
        send_msg(conn, rec[0])
    conn.close()  # Closes connection


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
def start() -> None:
    server.listen()
    print(f"Server is listening on {SERVER}")

    while True:
        conn, addr = server.accept()  # Accepting devices that try to connect and getting info about it (addr --> ip adress, conn --> )
        thread = threading.Thread(target=handle_client, args=(conn, addr))  # We create a thread for a client that is trying to connect
        thread.start()
        print(f"\nActive Connectins --> {threading.active_count() - 1}")  # How many clients are connected


if __name__ == "__main__":
    # Poskusi več portov v primeru če je kakšen zaseden
    for port in range(10):
        PORT = 5050 + port
        ADDR = (SERVER, PORT)
        try:
            server.bind(ADDR)
            break
        except OSError:
            continue


    print("Starting server!")
    start()