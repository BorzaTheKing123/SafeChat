def screen():
    #friends = open("client/friends.txt", "r+")
    print("Katerega prijatelja bi rad kontaktiral:")
    for i in friends.readlines():
        print(i.strip("'"))
    contact = input("--> ")
    c = 0

    if contact.lower() != "q":
        for user in friends.readlines():
            if user == contact:
                friends.close()
                print("Quit with Ctrl + c")
                thread_send = threading.Thread(target=send_msg) # We create a thread for a client that is trying to connect
                thread_send.start()
                listening.listen()
                # This part recieves messages
                while True:
                    conn, addr = listening.accept()
                    thread = threading.Thread(target=get_msg, args=(conn, addr))
                    thread.start()

        if c == len(friends.readlines):
            search = input(f"User {contact} is not your friend!\nDo you want to become friends with {contact}? (y/n)\n--> ")
            if search.lower() == "y":
                confirm = send(contact)
                if confirm != "!NO_USER":
                    friends.writelines(f"'{contact}'")
                else:
                    print(f"User {contact} doesen't exist!")
