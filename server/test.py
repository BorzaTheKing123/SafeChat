# Datoteka za testiranje funkcij

def main(x):
    print(x, "Mamma")
    if x < 3:
        x+= 1
        main(x)
        #return
    print("After")

main(0)