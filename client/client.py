import socket
from tkinter import *
import hashlib

WIDTH = 1920 #window.winfo_screenwidth()
HEIGHT = 1080 #window.winfo_screenmmheight()s
CENTER_WIDTH = WIDTH / 2
CENTER_HEIGHT = HEIGHT / 2

FORMAT = 'utf-8'
HEADER = 64
PORT = 5061
DISCONNECT_MESSAGE = "DISCONNECT_FROM_SERVER"
SERVER = "192.168.178.144"
ADDR = (SERVER, PORT)


def register():
    global window
    window = Tk()
    window.title("SafeChat")
    window.geometry('960x540')
    window.resizable(False, False)
    # Destroys all widgets
    for widgets in window.winfo_children():
        widgets.destroy()

    title_label = Label(window, text="Register", font=("Arial", 30)).place(x = CENTER_WIDTH-500, y = CENTER_HEIGHT-400)
    username_label = Label(window, text="Username", font=("Arial", 20)).place(x = CENTER_WIDTH-750, y = CENTER_HEIGHT-300)
    user_password = Label(window, text = "Password", font=("Arial", 20)).place(x = CENTER_WIDTH-750, y = CENTER_HEIGHT-250)
    register_label = Label(window, text = "Already have an account?", font=("Arial", 16)).place(x = CENTER_WIDTH-600, y = CENTER_HEIGHT-200)

    username_input_area = Entry(window, width = 30, font=("Arial", 20))
    username_input_area.pack()
    username_input_area.place(x = CENTER_WIDTH-630, y = CENTER_HEIGHT-300)
    password_input_area = Entry(window, width = 30, font=("Arial", 20))
    password_input_area.pack()
    password_input_area.place(x = CENTER_WIDTH-630, y = CENTER_HEIGHT-250)

    login_button = Button(window, text = "Login", font=("Arial", 16), command=login)
    login_button.pack()
    login_button.place(x = CENTER_WIDTH-400, y = CENTER_HEIGHT-200)
    register_button = Button(window, text = "Register", font=("Arial", 16), command=lambda : send_register(username_input_area.get(), password_input_area.get()))
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

    title_label = Label(window, text="Login", font=("Arial", 30)).place(x = CENTER_WIDTH-500, y = CENTER_HEIGHT-400)
    username_label = Label(window, text="Username", font=("Arial", 20)).place(x = CENTER_WIDTH-750, y = CENTER_HEIGHT-300)
    user_password = Label(window, text = "Password", font=("Arial", 20)).place(x = CENTER_WIDTH-750, y = CENTER_HEIGHT-250)
    register_label = Label(window, text = "Don't have an account yet?", font=("Arial", 16)).place(x = CENTER_WIDTH-600, y = CENTER_HEIGHT-200)

    username_input_area = Entry(window, width = 30, font=("Arial", 20))
    username_input_area.pack()
    username_input_area.place(x = CENTER_WIDTH-630, y = CENTER_HEIGHT-300)
    password_input_area = Entry(window, width = 30, font=("Arial", 20))
    password_input_area.pack()
    password_input_area.place(x = CENTER_WIDTH-630, y = CENTER_HEIGHT-250)

    login_button = Button(window, text = "Login", font=("Arial", 16), command=lambda : send_login(username_input_area.get(),  password_input_area.get()))
    login_button.pack()
    login_button.place(x = CENTER_WIDTH-750, y = CENTER_HEIGHT-200)
    register_button = Button(window, text = "Register", font=("Arial", 16), command = register)
    register_button.pack()
    register_button.place(x = CENTER_WIDTH-400, y = CENTER_HEIGHT-200)

    window.mainloop()

# Sends user info and recieves new token
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
                window.destroy()
                break
            elif new_token == "!FALSE_TOKEN":
                window.destroy()
                break
            else: 
                print(new_token)
                window.destroy()
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
                window.destroy()
                main()
                break
            else:
                print(new_token)
                break


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT) # We get length of the message we want to send
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    return client.recv(64).decode(FORMAT)


def main():
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    while True:
        try:
            file = open("token.txt", "r+")
            token = file.readline()
            confirm = send(token)
            print(confirm)
            if confirm == "!FALSE_TOKEN":
                file.close()
                login()
                break
            else:
                file.close()
                while True:
                    msg = input("Vnesi sporočilo ==> ")
                    if msg == "q":
                        send(DISCONNECT_MESSAGE)
                        print("!DISCONNECTED")
                        break
                    else:
                        send(msg)
                break
        except OSError:
            file = open("token.txt", "x")
            file.close()
            login()
            break

if __name__ == '__main__':
    main()
