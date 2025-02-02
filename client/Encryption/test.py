from Encryption import Encryption
import random

char = "ABCDEFGHIJKLMNOPRSTUVZXYWQqwertyuiopasdfghjklzxcvbnm!#$%&()=?/+*-_{}[]|1234567890<>"
while True:
    key = ""
    s = ""
    t = ""
    
    for i in range (30):
        key += random.choice(char)
    for i in range (30):
        s += random.choice(char)
    e = Encryption(key)
    et = str(e.encryption(s))
    et = et[2:len(et)-1]

    ccount = 1
    prev = et[0]
    change=prev
    for x in range(0, int(len(et)), 3):
        t += et[x+1:x+3]
        if et[x] != prev:
            change += prev + str(ccount)
    print(t)
    print(et)

    break

