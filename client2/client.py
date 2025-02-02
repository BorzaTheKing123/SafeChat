# Geslo: 1234

import socket
import hashlib
import sys
import Encryption.AsymmetricEncryption as ae
from Encryption.Encryption import Encryption
from pathlib import Path
from cryptography.hazmat.primitives import serialization

FORMAT = 'utf-8'
HEADER = 64
DISCONNECT_MESSAGE = "!DISCONNECT_FROM_SERVER"


# Funkcija za registracijo uporabnika
def register():
    try:
        username = input("Username: ")
        password = input("Password: ")
        send_register(username, password)
    except KeyboardInterrupt:
        send(DISCONNECT_MESSAGE)
        sys.exit()


# Funkcija za prijavo uporabnika
def login():
    try:
        account = input("Do you have an account? (y/n): ")
        if account.lower() == "y":
            username = input("Username: ")
            password = input("Password: ")
            send_login(username, password)
        elif account.lower() == "n":
            register()
        else:
            print("Invalid input!")
            login()
    except KeyboardInterrupt:
        send(DISCONNECT_MESSAGE)
        sys.exit()


# Pošlje uporabniške podatke in prejme nov token
def send_login(username, psw):
    if " " in username or " " in psw:
        print("Invalid characters!")
    else:
        password = hashlib.sha512(bytes(psw, "utf-8")).hexdigest()
        while True:
            new_token = send(f"{username} {password} 1")
            if new_token != "!INCORRECT_PASSWORD" and new_token != "!FALSE_TOKEN":
                file = open("token/token.txt", "w")
                file.write(new_token)
                file.close()
                break
            elif new_token == "!FALSE_TOKEN":
                break
            else: 
                print(new_token)
        print("main")
        main()


# Pošlje uporabniške podatke in prejme token pri registraciji
def send_register(username, psw):
    if " " in username or " " in psw:
        print("Invalid characters!")
    else:
        password = hashlib.sha512(bytes(psw, "utf-8")).hexdigest()
        while True:
            new_token = send(f"{username} {password} 0")
            if new_token != "Username already exists!" and new_token != "Username is too short!":
                file = open("token/token.txt", "w")
                file.write(new_token)
                file.close()
                main()
                break
            else:
                print(new_token)
                break


#Funkcija za pošiljanje sporočil
def send_msg():
    print("To REFRESH just press ENTER!")
    try:
        while True:
            user = input("Destination:\n--> ")
            if user == "":
                print(send(f"{user} !==>"))
            else:
                msg = input("Message:\n==> ")
                print(send(f"{user} !==> {msg}"))
    except KeyboardInterrupt:
        send(DISCONNECT_MESSAGE)


# Funkcija za pošiljanje sporočil
def send(msg):
    server_public_pem_path = Path("keys/server_public_key.pem")
    server_public_pem_bytes= server_public_pem_path.read_bytes()
    try:
        server_public_key = serialization.load_pem_public_key(server_public_pem_bytes)
    except Exception:
        return

    if len(msg) > 256:
        message = msg.encode(FORMAT)
    else:
        message = ae.encrypt(msg, server_public_key).encode(FORMAT)
    
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT) # We get length of the message we want to send
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

    if msg == DISCONNECT_MESSAGE:
        return
    
    recv_msg = client.recv(1024).decode(FORMAT)
    if len(recv_msg) > 450:
        return recv_msg
    return ae.decrypt(recv_msg, rprivate_key(se))


# Funkcija, ki pošlje javni ključ na strežnik
def send_public_key():
    public_pem_bytes = Path("keys/public_key.pem").read_bytes()
    return send(public_pem_bytes.decode('utf-8'))


# Funkcija za branje privatnega ključa
def rprivate_key(se):
    private_pem_bytes = se.decryption(Path("keys/privat_key.pem").read_bytes())
    return serialization.load_pem_private_key(
        private_pem_bytes,
        password=None,
    )


# Funkcija za branje javnega ključa
def server_public_key():
    public_key_pem_bytes = client.recv(1024)
    server_public_pem_path = Path("keys/server_public_key.pem")
    server_public_pem_path.write_bytes(public_key_pem_bytes)


# Glavni del programa
def main():
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER = "192.168.178.33" # Specifičen glede na to kje testiraš program

    # Zahteva geslo in dekodira privaten ključ
    password = "123456" # Nastavi kasneje za geslo svojega programa input() !!!!
    global se
    se = Encryption(password)
    private_key = rprivate_key(se)

    for port in range(10):
        PORT = 5050 + port
        ADDR = (SERVER, PORT)

        try:
            client.connect(ADDR)
            break
        except OSError:
            continue
    else:
        print("Server unavailable!")
        return
    
    # Prejme javni ključ strežnika
    server_public_key()
    
    # Preveri, če je ključ bil sprejet na strežniku
    if send_public_key() != "!VALID_KEY":
        send(DISCONNECT_MESSAGE)
        return

    # Zanka skrbi za bolj povezano uporabo programa
    while True:
        try:
            # Branje datoteke token.txt
            file = open("token/token.txt", "r+")
            token = se.decryption(file.readline()).decode('utf-8')
            file.close()

            confirm = send(token) # Vrne !FALSE_TOKEN ali pa uporabniško ime

            # Preveri če je uspela povezava z danim tokenom
            if confirm == "!FALSE_TOKEN":
                login()
                break
            
            # Če povezava uspe potem gre v glavni del programa
            print(f"Logined as user: {confirm}")
            send_msg()
            break
        
        # Če datoteke token.txt ni jo ustvari
        except OSError:
            file = open("token/token.txt", "x")
            file.close()

if __name__ == '__main__':
    main()
