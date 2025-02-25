import sys
from pathlib import Path

# Doda starševsko mapo kot začetek poti
sys.path.append(str(Path(__file__).resolve().parent.parent))

import socket
import hashlib
import sys
import threading
import Encryption.AsymmetricEncryption as ae
from Encryption.Encryption import Encryption
from pathlib import Path
from cryptography.hazmat.primitives import serialization
import time

FORMAT = 'utf-8'
HEADER = 64
DISCONNECT_MESSAGE = "!DISCONNECT_FROM_SERVER"

# Zahteva geslo in dekodira privaten ključ
password = input("Vnesi geslo: ")
se = Encryption(password) # Naredi obejkt za simetrično enkripcijo
messages = []


# Funkcija za registracijo uporabnika
def register():
    try:
        username = input("Ime: ")
        password = input("Geslo: ")
        send_register(username, password)
    except KeyboardInterrupt:
        send(DISCONNECT_MESSAGE, False)
        quit()


# Funkcija za prijavo uporabnika
def login():
    # 3 poskusi za prijavo
    for _ in range(3):
        try:
            account = input("Ali imate račun (n za ustvaritev novega računa)? (y/n): ")
            if account.lower() == "y":
                username = input("Ime: ")
                password = input("Geslo: ")
                send_login(username, password) # Pošlje ime in geslo
            elif account.lower() == "n":
                register()
            else:
                print("Neveljaven vnos!")
                login()
        except KeyboardInterrupt: # V primeru ctrl-c program pošlje DISCONNECT_MESSAGE in se konča
            send(DISCONNECT_MESSAGE, False)
            quit()


# Pošlje uporabniške podatke in prejme nov token
def send_login(username, psw):
    # Preveri da ni presledkov v imenu ali geslu
    if " " in username or " " in psw:
        print("Ne uporabljaj presledkov!")
        return
    
    password = hashlib.sha512(bytes(psw, FORMAT)).hexdigest() # Vrne hash gesla

    # Preveri, če je prijava uspela
    new_token = send(f"{username} {password} 1", True)
    if new_token != "!INCORRECT_PASSWORD" and new_token != "!FALSE_TOKEN":
        file = open("client2/token/token.txt", "w")
        file.write(se.encryption(new_token.encode(FORMAT)).decode(FORMAT))
        file.close()
    else: # Če ne uspe izpiše zakaj ne
        print(new_token)
        return
    
    # Nadaljuje z glavnim delom programa
    send(DISCONNECT_MESSAGE, False)
    main()
    quit()


# Pošlje uporabniške podatke in prejme token pri registraciji
def send_register(username, psw):
     # Preveri da ni presledkov v imenu ali geslu
    if " " in username or " " in psw:
        print("Ne uporabljaj presledkov!")
        return
    
    password = hashlib.sha512(bytes(psw, FORMAT)).hexdigest()

    # Preveri, če je registracija uspela
    new_token = send(f"{username} {password} 0", True)
    if new_token != "Uporabniško ime že obstaja!" and new_token != "Uporabniško ime je prekratko! (vsaj 4 znaki brez presledkov)":
        file = open("client2/token/token.txt", "w")
        file.write(se.encryption(new_token.encode(FORMAT)).decode(FORMAT))
        file.close()
    else: # Če ni izpiše rezultat in se vrne nazaj
        print(new_token)
        return

    # Če proces uspe se odjavi in se ponolno prijavi
    send(DISCONNECT_MESSAGE, False)
    main()
    quit()


# Funkcija za izpis sporočil
def print_messages():
    global messages
    if len(messages) != 0:
        print("\nPrejeta sporočila:")
        for message in messages:
            print("-->", message)
        messages = []
        return
    print("Ni sporočil :(")


#Funkcija za pošiljanje sporočil
def send_msg():
    # Ločen proces za prejemanje
    thread = threading.Thread(target=rec, args=(True,))  # Ustvarimo ločen proces, da lahko sprejmemo več povezav hkrati
    thread.start()

    print("Za osvežitev pritisnite ENTER!")
    try:
        while True:
            user = input("\nNaslovnik:\n--> ")
            if user == "":
                print_messages()
            else:
                msg = input("Sporočilo:\n==> ")
                send(f"{user} !==> {msg}", False)
                time.sleep(0.5) # Da nekaj časa da se sporočilo obdela na strežniku
                print_messages()
    except KeyboardInterrupt:
        send(DISCONNECT_MESSAGE, False)
        quit()


# Funkcija za pošiljanje sporočil
def send(msg, ret):
    # Odpre datoteko
    server_public_pem_path = Path("client2/keys/server_public_key.pem")
    server_public_pem_bytes= server_public_pem_path.read_bytes()

    # Ustvari objekt ključa
    try:
        server_public_key = serialization.load_pem_public_key(server_public_pem_bytes)
    except Exception:
        return

    # Program ne more poslati enkriptiranih sporočil daljših od dolžine javnega ključ
    if len(msg) > 256:
        message = msg.encode(FORMAT)
    else:
        message = ae.encrypt(msg, server_public_key).encode(FORMAT)
    
    # Ta del pošlje dolžino sporočila in sporočilo
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT) # Dobimo dolžino sporočila, ki ga želimo
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

    # Če se odjavlja ne čaka na povratno sporočilo
    if msg == DISCONNECT_MESSAGE:
        return
    
    # Prejme in vrne sporočilo
    if ret:
        return rec(False)


# FUnkcija, ki prejme sporočila
def rec(loop):
    global messages

    ret = True
    if loop:
        ret = False

    try:
        while True:
            recv_msg = client.recv(1024).decode(FORMAT)
            try:
                text = ae.decrypt(recv_msg, rprivate_key())

                # Če hočemo vrniti vrednost
                if ret:
                    return ae.decrypt(recv_msg, rprivate_key())
                messages.append(text)
            except Exception as exec:
                if ret:
                    return recv_msg
                messages.append(recv_msg)
    except KeyboardInterrupt:
        quit()


# Funkcija, ki pošlje javni ključ na strežnik
def send_public_key():
    public_pem_bytes = Path("client2/keys/public_key.pem").read_bytes()
    return send(public_pem_bytes.decode(FORMAT), True)


# Funkcija za branje privatnega ključa
def rprivate_key():
    private_pem_bytes = se.decryption(Path("client2/keys/privat_key.pem").read_bytes().decode(FORMAT))
    return serialization.load_pem_private_key(
        private_pem_bytes,
        password=None,
    )


# Funkcija za branje javnega ključa
def server_public_key():
    public_key_pem_bytes = client.recv(1024)
    server_public_pem_path = Path("client2/keys/server_public_key.pem")
    server_public_pem_path.write_bytes(public_key_pem_bytes)


# Glavni del programa
def main():
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER = "127.0.0.1" # Specifičen glede na to kje testiraš program
    
    # Poskusi se povezati na večih vhodih
    for port in range(10):
        PORT = 5050 + port
        ADDR = (SERVER, PORT)
        try:
            client.connect(ADDR)
            break
        except OSError:
            continue
    else:
        print("Strežnik ni na voljo!")
        return
    
    # Prejme javni ključ strežnika
    server_public_key()
    check_key = send_public_key()
    
    # Preveri, če je ključ bil sprejet na strežniku
    if check_key != "!VALID_KEY":
        print(check_key)
        send(DISCONNECT_MESSAGE, False)
        return

    # Zanka skrbi za bolj povezano uporabo programa
    while True:
        try:
            # Branje datoteke token.txt
            file = open("client2/token/token.txt", "r+")
            token = se.decryption(file.readline()).decode(FORMAT)
            file.close()

            confirm = send(token, True) # Vrne !FALSE_TOKEN ali pa uporabniško ime

            # Preveri če je uspela povezava z danim tokenom
            if confirm == "!FALSE_TOKEN":
                login()
                return
            
            # Če povezava uspe potem gre v glavni del programa
            print(f"Tvoje uporabniško ime: {confirm}\n")
            send_msg()
            return
        
        # Če datoteke token.txt ni jo ustvari
        except OSError:
            file = open("client2/token/token.txt", "x")
            file.close()

if __name__ == '__main__':
    main()
