# Ta datoteka je bila narejena s pomočjo naslednje strani: <https://elc.github.io/python-security/chapters/07_Asymmetric_Encryption.html#rsa-encryption>

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from pathlib import Path
from cryptography.hazmat.primitives import serialization
import Encryption as e
import base64


# Enkripcija
def encrypt(message, public_key):
    data_base64 = base64.standard_b64encode(public_key.encrypt(message.encode('utf-8'), padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)))
    data_base64_string = data_base64.decode("UTF-8")
    return data_base64_string


# Dekripcija
def decrypt(message_encrypted, private_key):
    decoded_data_standard = base64.standard_b64decode(message_encrypted)
    try:
        message_decrypted = private_key.decrypt(bytes.fromhex(decoded_data_standard.hex()), padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        return message_decrypted.decode('utf-8')
    except ValueError:
        return "Failed to Decrypt"


# Namenjeno samo za testiranje
def main():
    es = e.Encryption("123456")

    private_pem_bytes = es.decryption(Path("server/keys/privat_key.pem").read_bytes())
    public_pem_bytes = Path("server/keys/public_key.pem").read_bytes()

    private_key_from_pem = serialization.load_pem_private_key(
        private_pem_bytes,
        password=None,
    )
    public_key_from_pem = serialization.load_pem_public_key(public_pem_bytes)

    print(private_key_from_pem, public_key_from_pem)
    et = encrypt("Samo", public_key_from_pem)
    dt = decrypt(et, private_key_from_pem)
    print(et, "\n", dt)


if __name__ == '__main__':
    main()
