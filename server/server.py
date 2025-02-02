# Zaženi strežnik znotraj mape server drugače bodo poti do datotek malce uničene

# Naredi da bo delala asimetrična enkripcija

import Database.DatabaseRequests as db
import socket
import threading
import random
import Encryption.AsymmetricEncryption as ae # Asimetrična enkripcija
from cryptography.hazmat.primitives import serialization
from pathlib import Path
from Encryption.Encryption import Encryption

HEADER = 64  # Velikost sporočila, ki pove kako veliko bo sporočilo
FORMAT = 'utf-8'

SERVER = socket.gethostbyname(socket.gethostname())  # Pridobi ip naslov avtomatično
DISCONNECT_MESSAGE = "!DISCONNECT_FROM_SERVER"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Ustvarimo socket objekt
active_connections = {} # Shrani aktivne povezave -> username: [conn, public_key]


# Ustvari nov token
def create_token():
    char = "ABCDEFGHIJKLMNOPRSTUVZXYWQqwertyuiopasdfghjklzxcvbnm!#$%&()=?/+*-_{}[]|1234567890<>"
    while True:
        new_token = ""
        for _ in range(30):
            new_token += random.choice(char)
        check_token = db.select("SELECT * FROM accounts WHERE token='{}'".format(new_token), 1)
        if check_token is None:
            return new_token


# Pridobi informacije o uporabniku
def get_target_info(user):
    if user in active_connections:
        return active_connections[user]
    else:
        return


# Funkcija za pošiljanje sporočil
def send(message, conn, public_key):
     conn.send(ae.encrypt(message, public_key).encode(FORMAT))


# Prijava uporabnika
def login(username, password):
    psw = db.select("SELECT password FROM accounts WHERE username='{}'".format(username), 1)
    password = f"('{password}',)"
    print(username, password, psw)
    if password == str(psw):
        return create_token()
    else:
        return "!INCORRECT_PASSWORD"


# Registracija uporabnika
def register(username, password):
    usr = db.select("SELECT username FROM accounts WHERE username='{}'".format(username), 1)
    if usr is not None:
        return False, "Username already exists!"
    elif len(username) < 1:
        return False, "Username is too short!"
    else:
        new_token = create_token()
        db.insert("INSERT INTO accounts VALUES ('{}', '{}', '{}')".format(username, password, new_token))
        return True, new_token


# Funkcija za branje privatnega ključa
def r_private_key():
    private_pem_bytes = se.decryption(Path("server/keys/privat_key.pem").read_bytes())
    return serialization.load_pem_private_key(
        private_pem_bytes,
        password=None,
    )


# Sprejme sporočilo
def receive(conn) -> str:
    msg_length = conn.recv(HEADER).decode(FORMAT)  # Pridobi dolžino sporočila
    if msg_length:
        msg_length = int(msg_length)
        rec = conn.recv(msg_length).decode(FORMAT)  # Pridobi sporočilo
        private_key = r_private_key()


        if msg_length > 450:
            return rec
        else:
            return ae.decrypt(rec, private_key)


# Ko je uporabnik povezan mu omogoča pošiljanje sporočil
def send_msg(sender_conn, sender_username, public_key):
    while True:
        rec = receive(sender_conn)
        print(f"{sender_username}: {rec}")

        if rec is None or rec == DISCONNECT_MESSAGE:
            active_connections.pop(sender_username)
            return
        
        try:
            user, msg = rec.split(" !==> ")
        except ValueError:
            send("->", sender_conn, public_key)
            continue

        if msg == DISCONNECT_MESSAGE:
            active_connections.pop(sender_username)
            return
        
        if " " in user:
            send("Incorrect username!", sender_conn, public_key)
            continue
        
        conn, conn_public_key = get_target_info(user)
        ms = f"{sender_username} !==> {msg}"
        
        if conn is None:
            send("User is unavaliable!", sender_conn, public_key)
            continue
        
        try:
            send(ms, conn, conn_public_key)
            send("Message sent!", sender_conn, public_key)
        except OSError:
            send("User is unavaliable!", sender_conn, public_key)
            active_connections.pop(user)


# Funkcija, ki pošlje javni ključ na strežnik
def send_public_key(conn):
    public_pem_bytes = Path("server/keys/public_key.pem").read_bytes()
    conn.send(public_pem_bytes)


# Obdelava povezave
def handle_client(conn, addr) -> None:
    print(f"Trying to connect from: {addr}")

    send_public_key(conn)

    # Preveri če je format javnega ključa pravilen
    public_pem_bytes = receive(conn).encode('utf-8')
    
    try:
        public_key = serialization.load_pem_public_key(public_pem_bytes)
    except Exception:
        return
    
    send("!VALID_KEY", conn, public_key)

    # Prejme token in preveri če je pravilen
    token = receive(conn)
    rec = db.select("SELECT username FROM accounts WHERE token='{}'".format(token), 1)
    if rec is not None:
        active_connections[rec[0]] = [conn, public_key] # Doda novo povezavo
        send(rec[0], conn, public_key)
        send_msg(conn, rec[0], public_key)
        conn.close()
        return

    # V primeru da token ni pravilen
    send("!FALSE_TOKEN", conn, public_key)
    count = 0

    # Skrbi za prijavo in registracijo
    while count < 3:
        try:
            username, password, log_or_reg = receive(conn).split(" ")
        except Exception:
            break

        # Prijava uporabnika
        if log_or_reg == "1":
            login_attempt = login(username, password)
            if login_attempt == "!INCORRECT_PASSWORD":
                count += 1
            conn.send(f"{login_attempt}".encode(FORMAT))
        
        # Registracija uporabnika
        else:
            status, register_attempt = register(username, password)
            if not status:
                count += 1
            conn.send(f"{register_attempt}".encode(FORMAT))
    else:
        conn.send(DISCONNECT_MESSAGE.format(FORMAT))
    
    print(f"Connection from: {addr} FAILED")
    conn.close()  # Zapre povezavo


# Posluša, če se hoče kdo povezati
def start() -> None:
    password = "123456" # !!!!NAredi input
    global se
    se = Encryption(password)

    server.listen()
    print(f"Server is listening on {SERVER}")

    while True:
        conn, addr = server.accept()  # Sprejme povezave, ki se hočejo povezati (addr --> ip adress, conn --> objekt)
        thread = threading.Thread(target=handle_client, args=(conn, addr))  # Ustvarimo thread, da lahko sprejmemo več povezav hkrati
        thread.start()
        print(f"\nActive Connectins --> {threading.active_count() - 1}")  # Napiše koliko povezav je povezanih na naenkrat


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