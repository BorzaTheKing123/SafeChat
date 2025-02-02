# Program simetrično enkriptira besedilo
# !!! Minimalna dolžina ključa je 6 in maksimalna 30

class Encryption:

    def __init__(self, key):
        self.key_in_binary = Encryption.toBits(key)


    # Funkcija pretovri besedilo v binarno obliko
    def toBits(text) -> list[str]:
        text_in_binary: list[str] = []

        for symbol in text:
            binary: str = bin(ord(symbol))[2:]
            text_in_binary.append((8-len(binary))*"0" + binary) # Naredi vse binarne vrednosti dolge 8 bitov
        
        return text_in_binary


    # Funkcija za enkripcijo besedila
    def encryption(self, text) -> bytes:
        symbol_count = 0
        len_of_key = len(self.key_in_binary)
        encrypted_text: str = ""
        text = text.decode('utf-8')
        text_in_binary = Encryption.toBits(text)

        value: int = 0
        for symbol in self.key_in_binary:
            value = value + int(symbol, 2)

        for symbol in text_in_binary:
            encrypted_text += hex(int(symbol, 2) + int(self.key_in_binary[symbol_count], 2) + value )[2:]

            symbol_count += 1
            if symbol_count == len_of_key:
                symbol_count = 0
            
        return encrypted_text.encode('utf-8') # Vrne bajtni zapis -> b'ključ'


    # Funkcija za dekripcijo besedila
    def decryption(self, encrypted_text) -> str:
        decrypted_text: str = ""
        symbol_count = 0
        len_of_key = len(self.key_in_binary)
        index = 0

        value: int = 0
        for symbol in self.key_in_binary:
            value = value + int(symbol, 2)
        
        for _ in range(int(len(encrypted_text)/3)):
            decrypted_text += str(chr(int(encrypted_text[index: index+3], 16) - value - int(self.key_in_binary[symbol_count], 2)))
            index += 3

            symbol_count += 1
            if symbol_count == len_of_key:
                symbol_count = 0
            
        return decrypted_text.encode('utf-8')


# Funkcija za testiranje programa
def main() -> None:
    key = "123456" # MIN 6, MAX is 30
    e = Encryption(key)
    encrypted_text = e.encryption("Fe#_i&FOP!s8VM8es2L<NTuAwMPs9j".encode('utf-8'))
    decrypted_text = e.decryption(encrypted_text.decode('utf-8'))
    print(encrypted_text)
    print(decrypted_text)


if __name__ == "__main__":
    main()
