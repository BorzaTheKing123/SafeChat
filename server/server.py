# Zaženi strežnik znotraj mape server drugače bodo poti do datotek malce uničene

import Database.DatabaseRequests as db
import socket
import threading
import random
import Encryption.AsymmetricEncryption as ae # Asimetrična enkripcija
from cryptography.hazmat.primitives import serialization
from pathlib import Path
from Encryption.Encryption import Encryption
import hashlib

password = input("Vnesi geslo (Testno geslo je: 123456): ")
se = Encryption(password)

HEADER = 64  # Velikost sporočila, ki pove kako veliko bo sporočilo
FORMAT = 'utf-8'

# Trenutno delal lokalno, vendar to ne spremeni delovanja
SERVER = "127.0.0.1" # Uporabi to funkcijo, da dobiš ip avtomatsko -> socket.gethostbyname(socket.gethostname())
DISCONNECT_MESSAGE = "!DISCONNECT_FROM_SERVER"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Ustvarimo socket objekt
active_connections = {} # Shrani aktivne povezave -> username: [conn, public_key]


# Ustvari nov token
def create_token():
    char = "ABCDEFGHIJKLMNOPRSTUVZXYWQqwertyuiopasdfghjklzxcvbnm!#$%&()=?/+*-_{}[]|1234567890<>"
    while True:
        new_token = ""

        # Ustvari token dolžine 64
        for _ in range(64):
            new_token += random.choice(char)
        
        # Preveri da tokena ni že v bazi
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

    # Če se geslo ujema ustavri nov token za povezavo
    if password == str(psw):
        token = create_token()
        db.update("UPDATE accounts SET token='{}' WHERE username='{}'".format(hashlib.sha512(bytes(token, FORMAT)).hexdigest(), username))
        return token
    
    return "!INCORRECT_PASSWORD"


# Registracija uporabnika
def register(username, password, addr):
    usr = db.select("SELECT username FROM accounts WHERE username='{}'".format(username), 1)

    # Preveri da uporbaniško ime ne obstaja že in da ustreza zahtevam
    if usr is not None:
        return False, "Uporabniško ime že obstaja!"
    elif len(username) < 4:
        return False, "Uporabniško ime je prekratko! (vsaj 4 znaki brez presledkov)"
    
    # Ustvari nov uporabiški račun
    new_token = create_token()
    db.update("INSERT INTO accounts VALUES ('{}', '{}', '{}', '{}')".format(username, password, hashlib.sha512(bytes(new_token, FORMAT)).hexdigest(), addr[0]))
    return True, new_token


# Funkcija za branje privatnega ključa
def r_private_key():
    private_pem_bytes = se.decryption(Path("server/keys/privat_key.pem").read_bytes())
    return serialization.load_pem_private_key(
        private_pem_bytes,
        password=None,
    )


# Sprejme sporočilo
def recv(conn) -> str:
    msg_length = conn.recv(HEADER).decode(FORMAT)  # Pridobi dolžino sporočila
    if msg_length:
        msg_length = int(msg_length)
        rec = conn.recv(msg_length).decode(FORMAT)  # Pridobi sporočilo
        private_key = r_private_key()

        # Poskuša dekripirati sporočilo razen če je predolgo
        try:
            return ae.decrypt(rec, private_key)
        except Exception:
            return rec


# Ko je uporabnik povezan mu omogoča pošiljanje sporočil
def send_msg(sender_conn, sender_username, public_key):
    while True:
        rec = recv(sender_conn)
        print(f"{sender_username}: {rec}")

        # Če prejme sporočilo za prekinjanje povezave konča povezavo
        if rec is None or DISCONNECT_MESSAGE in rec:
            active_connections.pop(sender_username)
            return

        # Ujame napake
        try:
            user, msg = rec.split(" !==> ")
        except ValueError:
            send(rec, sender_conn, public_key)
            continue
        
        # Če poskuša uporabnik poslati sporočilo samemu sebi
        if user == sender_username:
            send("Ej, ne pošiljaj sporočil samemu sebi!", sender_conn, public_key)
            continue
        
        # Preveri če je vneseno pravilno uporabniško ime
        if " " in user:
            send("Napačno uporabniško ime!", sender_conn, public_key)
            continue
        
        # Pridobi informacije o naslovniku
        get_target = get_target_info(user)
        if type(get_target) != list:
            send("Uporabnik ne obstaja ali pa ni povezan!", sender_conn, public_key)
            continue
        
        # Ta del sestavi sporočilo
        conn, conn_public_key = get_target
        ms = f"{sender_username} !==> {msg}"
        
        # Dodatno preveri, povezava obstaja
        if conn is None:
            send("Uporabnik ni na voljo!", sender_conn, public_key)
            continue
        
        # Pošlje sporočilo razen če je uporabnik nedostopen
        try:
            send(ms, conn, conn_public_key)
            send("Poslano!", sender_conn, public_key)
        except OSError:
            send("Uporabnik ni na voljo!", sender_conn, public_key)
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
    public_pem_bytes = recv(conn).encode(FORMAT)
    
    # naloži javni ključ uporabnika
    try:
        public_key = serialization.load_pem_public_key(public_pem_bytes)
    except Exception:
        return
    
    send("!VALID_KEY", conn, public_key)

    # Prejme token in preveri če je pravilen
    token = hashlib.sha512(bytes(recv(conn), FORMAT)).hexdigest()
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
            username, password, log_or_reg = recv(conn).split(" ")
        except Exception:
            break

        # Prijava uporabnika
        if log_or_reg == "1":
            login_attempt = login(username, password)
            if login_attempt == "!INCORRECT_PASSWORD":
                count += 1
            send(f"{login_attempt}", conn, public_key)
        
        # Registracija uporabnika
        else:
            status, register_attempt = register(username, password, addr)
            if not status:
                count += 1
            send(f"{register_attempt}", conn, public_key)
    else:
        send(DISCONNECT_MESSAGE, conn, public_key)
    
    print(f"Connection from: {addr} FAILED")
    conn.close()  # Zapre povezavo


# Posluša, če se hoče kdo povezati
def start() -> None:
    # Zažene strežnik
    server.listen()
    print(f"Server is listening on {SERVER}")

    # Sprejema povezave in jih daje v podprocese
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