import sys
from pathlib import Path

# Doda starševsko mapo kot začetek poti
sys.path.append(str(Path(__file__).resolve().parent.parent))

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from Encryption import Encryption


# Funkcija ustvari javni in zasebni kluč s pomočjo RSA postopka
def generate_key_pair():
    private_key = rsa.generate_private_key(public_exponent=65537,key_size=2048,)
    public_key = private_key.public_key()
    return private_key, public_key


# Glavna funkcija za ustvarjanje ključev
def main():
    private_key, public_key = generate_key_pair()
    password = input("Geslo mora biti dolgo od 6 do 30 mest!\nGeslo: ") # password = "123456"
    es = Encryption.Encryption(password)

    # ustvari enkriptiran privaten ključ
    privat_key_pem_bytes = es.encryption(private_key.private_bytes(
    encoding=serialization.Encoding.PEM,  # PEM format za shranjevanje
    format=serialization.PrivateFormat.TraditionalOpenSSL,  # Format za privatni ključ
    encryption_algorithm=serialization.NoEncryption()  # Brez enkripcije
    ))

    # Ustvari enkriptiran javni ključ
    public_key_pem_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,  # Fromat za javni kključ
    )

    # Določanje poti do PEM datotek
    privat_key_pem_path = Path("client/keys/privat_key.pem")
    public_key_pem_path = Path("client/keys/public_key.pem")

    # Zapisovanje ključev
    privat_key_pem_path.write_bytes(privat_key_pem_bytes)
    public_key_pem_path.write_bytes(public_key_pem_bytes)

    # Branje
    print(f"\n{es.decryption(privat_key_pem_path.read_text()).decode('utf-8')}\nUspešno ustvarjanje ključa!")

if __name__ == "__main__":
    main()