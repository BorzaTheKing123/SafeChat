from tkinter import *

def screen():
    window = Tk()
    window.title("SafeChat")
    #window.geometry('960x540')
    #window.resizable(False, False)
    # Destroys all widgets
    for widgets in window.winfo_children():
        widgets.destroy()
    
    # Texting part
    msg_box = Text(window)
    msg_box.grid(row=0, column=1)
    msg_box.pack()
    if Event == "Enter":
        print("Enter")
    #thread = threading.Thread(target=send, args=(msg_box.get())) # We create a thread for a client that is trying to connect
    #thread.start()
    window.mainloop()

screen()