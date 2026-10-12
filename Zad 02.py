from Cryptodome.Cipher import AES, DES
import binascii

def szyfrowanie_aes(klucz: bytes, jawnyTekst: bytes) -> bytes:
    if len(klucz) != 16:
        raise ValueError("Klucz musi mieć dokładnie 16 bajtów")
    if len(jawnyTekst) != 16:
        raise ValueError("Tekst musi miec dokładnie 16 bajtów dla jednego bloku")

    cipher = AES.new(klucz, AES.MODE_ECB)
    return cipher.encrypt(jawnyTekst)

def szyfrowanie_des(klucz: bytes, jawnyTekst: bytes) -> bytes:
    if len(klucz) != 8:
        raise ValueError("Klucz musi mieć dokładnie 8 bajtów")
    if len(jawnyTekst) != 8:
        raise ValueError("Tekst musi miec dokładnie 8 bajtów dla jednego bloku")

    cipher = DES.new(klucz, DES.MODE_ECB)
    return cipher.encrypt(jawnyTekst)

def hamming(x: bytes, y: bytes) -> int:
    if len(x) != len(y):
        raise ValueError("łańcuchy muszą mieć tą samą długość")
    return sum((b1 ^ b2).bit_count() for b1, b2 in zip(x,y))

if __name__ == "__main__":
    ## Weryfikacja dzialania funkcji pomocniczych
    aes_klucz = b'SekretnyKluczAES'
    aes_jawnyTekst = b'ToJest16Bajtow!!'

    aes_ciphertext = szyfrowanie_aes(aes_klucz, aes_jawnyTekst)
    print(f"AES-128 (ECB) Szyfrogram (HEX): {binascii.hexlify(aes_ciphertext).decode('utf-8')}")

    des_klucz = b'KluczDES'
    des_jawnyTekst = b'Tajne123'

    des_ciphertext = szyfrowanie_des(des_klucz, des_jawnyTekst)
    print(f"DES (ECB) Szyfrogram (HEX):     {binascii.hexlify(des_ciphertext).decode('utf-8')}")

    x = b'\x0F' # 00001111
    y = b'\xFF' # 11111111
    print(f"Odległość (hamming): {hamming(x, y)}")