import socket
from tkinter import *
import hashlib
import sys

WIDTH = 1920#window.winfo_screenwidth()
HEIGHT = 1080#window.winfo_screenmmheight()
CENTER_WIDTH = WIDTH / 2
CENTER_HEIGHT = HEIGHT / 2

FORMAT = 'utf-8'
HEADER = 64
DISCONNECT_MESSAGE = "!DISCONNECT_FROM_SERVER"

CLIENT = socket.gethostbyname(socket.gethostname()) # Gets ip automaticaly. Also here enter your public ip address to make it work outside home network
listening = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # We create a socket object --> .AF_INET is one of many different types

for port in range(10):
    CLIENT_PORT = 5070 + port
    ADDR_CLIENT = (CLIENT, CLIENT_PORT)
    try:
        listening.bind(ADDR_CLIENT)
        break
    except OSError:
        continue


def register():
    global window
    window = Tk()
    window.title("SafeChat")
    window.geometry('960x540')
    window.resizable(False, False)
    # Destroys all widgets
    for widgets in window.winfo_children():
        widgets.destroy()

    Label(window, text="Register", font=("Arial", 30)).place(x=CENTER_WIDTH - 500, y=CENTER_HEIGHT - 400)
    Label(window, text="Username", font=("Arial", 20)).place(x = CENTER_WIDTH-750, y=CENTER_HEIGHT-300)
    Label(window, text = "Password", font=("Arial", 20)).place(x=CENTER_WIDTH-750, y=CENTER_HEIGHT-250)
    Label(window, text="Already have an account?", font=("Arial", 16)).place(x=CENTER_WIDTH - 600, y=CENTER_HEIGHT - 200)

    username_input_area = Entry(window, width = 30, font=("Arial", 20)).grid(row=0, column=0)
    username_input_area.pack()
    username_input_area.place(x = CENTER_WIDTH-630, y = CENTER_HEIGHT-300)
    password_input_area = Entry(window, width = 30, font=("Arial", 20))
    password_input_area.pack()
    password_input_area.place(x = CENTER_WIDTH-630, y = CENTER_HEIGHT-250)

    login_button = Button(window, text = "Login", font=("Arial", 16), command=login)
    login_button.pack()
    login_button.place(x = CENTER_WIDTH-400, y = CENTER_HEIGHT-200)
    register_button = Button(window, text = "Register", font=("Arial", 16), command=lambda :
    (window.destroy(), send_register(username_input_area.get(), password_input_area.get())))
    register_button.pack()
    register_button.place(x = CENTER_WIDTH-750, y = CENTER_HEIGHT-200)


def login():
    global window
    window = Tk()
    window.title("SafeChat")
    window.geometry('960x540')
    window.resizable(False, False)
    # Destroy all widgets
    for widgets in window.winfo_children():
        widgets.destroy()

    Label(window, text="Login", font=("Arial", 30)).place(x=CENTER_WIDTH-500, y=CENTER_HEIGHT-400)
    Label(window, text="Username", font=("Arial", 20)).place(x=CENTER_WIDTH-750, y=CENTER_HEIGHT-300)
    Label(window, text="Password", font=("Arial", 20)).place(x=CENTER_WIDTH-750, y=CENTER_HEIGHT-250)
    Label(window, text="Don't have an account yet?", font=("Arial", 16)).place(x=CENTER_WIDTH-600, y=CENTER_HEIGHT-2)

    username_input_area = Entry(window, width = 30, font=("Arial", 20))
    username_input_area.pack()
    username_input_area.place(x = CENTER_WIDTH-630, y = CENTER_HEIGHT-300)
    password_input_area = Entry(window, width = 30, font=("Arial", 20))
    password_input_area.pack()
    password_input_area.place(x = CENTER_WIDTH-630, y = CENTER_HEIGHT-250)

    login_button = Button(window, text = "Login", font=("Arial", 16), command=lambda:
    (window.destroy(), send_login(username_input_area.get(), password_input_area.get())))
    login_button.pack()
    login_button.place(x = CENTER_WIDTH-750, y = CENTER_HEIGHT-200)
    register_button = Button(window, text = "Register", font=("Arial", 16), command = register)
    register_button.pack()
    register_button.place(x = CENTER_WIDTH-400, y = CENTER_HEIGHT-200)

    window.mainloop()


# Sends user info and receives new token
def send_login(username, psw):
    if " " in username or " " in psw:
        print("Invalid characters!")
    else:
        password = hashlib.sha512(bytes(psw, "utf-8")).hexdigest()
        while True:
            new_token = send(f"{username} {password} 1")
            if new_token != "!INCORRECT_PASSWORD" and new_token != "!FALSE_TOKEN":
                file = open("token.txt", "w")
                file.write(new_token)
                file.close()
                break
            elif new_token == "!FALSE_TOKEN":
                break
            else: 
                print(new_token)
        print("main")
        main()


def send_register(username, psw):
    if " " in username or " " in psw:
        print("Invalid characters!")
    else:
        password = hashlib.sha512(bytes(psw, "utf-8")).hexdigest()
        while True:
            new_token = send(f"{username} {password} 0")
            if new_token != "Username already exists!" and new_token != "Username is too short!":
                file = open("token.txt", "w")
                file.write(new_token)
                file.close()
                main()
                break
            else:
                print(new_token)
                break


def send_msg():
    print("To REFRESH just press ENTER!")
    try:
        while True:
            user = input("Komu pošiljaš sporočilo\n--> ")
            if user == "":
                print(send(f"{user} !==>"))
            else:
                msg = input("==> ")
                print(send(f"{user} !==> {msg}"))
    except KeyboardInterrupt:
        send(DISCONNECT_MESSAGE)
        sys.exit()


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT) # We get length of the message we want to send
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    return client.recv(1024).decode(FORMAT)


# Main part of the program
def main():
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER = "127.0.0.1" # Specifičen glede na to kje testiraš program

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


    while True:
        try:
            file = open("token.txt", "r+")
            token = file.readline()
            print(token)
            confirm = send(token) # Vrne !FALSE_TOKEN ali pa potrditev
            if confirm == "!FALSE_TOKEN":
                file.close()
                login()
                break
            else:
                file.close()
                send_msg()
                break
        except OSError:
            file = open("token.txt", "x")
            file.close()


if __name__ == '__main__':
    main()
