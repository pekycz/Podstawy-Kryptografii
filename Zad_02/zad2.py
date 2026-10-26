from Cryptodome.Cipher import AES, DES
import binascii
#pip install pycryptodomex
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

    aes_ciphertext = szyfrowanie_aes(b'SekretnyKluczAES', b'ToJest16Bajtow!!')
    print(f"AES-128 (ECB) Raw: {aes_ciphertext} Szyfrogram (HEX): {binascii.hexlify(aes_ciphertext).decode('utf-8')}")

    des_ciphertext = szyfrowanie_des(b'KluczDES', b'Tajne123')
    print(f"DES (ECB) Szyfrogram (HEX):    {binascii.hexlify(des_ciphertext).decode('utf-8')}")

    x = b'\x0F' # 00001111
    y = b'\xFF' # 11111111
    print(f"Odległość (hamming): {hamming(x, y)}")

    aes_klucz = b'SekretnyKluczAES'
    aes_tekst = b'\x00' * 16
    aes_zaszyfrowanyTekst = szyfrowanie_aes(aes_klucz, aes_tekst)
    des_zad1_klucz = b'00000000'
    des_zad1_tekst = b'00000000'

    odleglosci_aes = []

    # Zmiana tekstu jawnego

    for i in range(128):
        zmienionyTekst = bytearray(aes_tekst)
        byte_index = i // 8
        bit_index = i % 8

        zmienionyTekst[byte_index] ^= (1 << bit_index) #XOR naklada przesuniety bit na tekst
        nowyTekst = bytes(zmienionyTekst)
        nowyZaszyfrowany = szyfrowanie_aes(aes_klucz, nowyTekst)

        dist = hamming(aes_zaszyfrowanyTekst, nowyZaszyfrowany)
        odleglosci_aes.append(dist)

    srednia_aes = sum(odleglosci_aes) / len(odleglosci_aes)
    min_aes = min(odleglosci_aes)
    max_aes = max(odleglosci_aes)

    des_klucz = b'KluczDES'
    des_tekst = b'\x00' * 8
    des_zaszyfrowanyTekst = szyfrowanie_des(des_klucz,des_tekst)
    odleglosci_des = []
    for i in range(64):
        zmienionyTekst = bytearray(des_tekst)
        byte_index = i // 8
        bit_index = i % 8

        zmienionyTekst[byte_index] ^= (1 << bit_index) #XOR naklada przesuniety bit na tekst
        nowyTekst = bytes(zmienionyTekst)
        nowyZaszyfrowany = szyfrowanie_des(des_klucz, nowyTekst)

        dist = hamming(des_zaszyfrowanyTekst, nowyZaszyfrowany)
        odleglosci_des.append(dist)

    srednia_des = sum(odleglosci_des) / len(odleglosci_des)
    min_des = min(odleglosci_des)
    max_des = max(odleglosci_des)

    print("Zmienianie tekstu jawnego: ")
    print(f"AES: Średnia: {srednia_aes}, Minimalna: {min_aes}, Maksymalna: {max_aes}")
    print(f"DES: Średnia: {srednia_des}, Minimalna: {min_des}, Maksymalna: {max_des}\n")

    # Zmiana klucza
    odleglosci_aes1 = []
    for i in range(128):
        zmienionyKlucz = bytearray(aes_klucz)
        byte_index = i // 8
        bit_index = i % 8

        zmienionyKlucz[byte_index] ^= (1 << bit_index)
        nowyZaszyfrowany = szyfrowanie_aes(zmienionyKlucz, aes_tekst)

        dist = hamming(aes_zaszyfrowanyTekst, nowyZaszyfrowany)
        odleglosci_aes1.append(dist)

    srednia_aes1 = sum(odleglosci_aes1) / len(odleglosci_aes1)
    min_aes1 = min(odleglosci_aes1)
    max_aes1 = max(odleglosci_aes1)

    odleglosci_des1 = []
    for i in range(64):
        zmienionyKlucz = bytearray(des_klucz)
        byte_index = i // 8
        bit_index = i % 8

        zmienionyKlucz[byte_index] ^= (1 << bit_index)
        nowyZaszyfrowany = szyfrowanie_des(zmienionyKlucz, des_tekst)

        dist = hamming(des_zaszyfrowanyTekst, nowyZaszyfrowany)
        odleglosci_des1.append(dist)

    srednia_des1 = sum(odleglosci_des1) / len(odleglosci_des1)
    min_des1 = min(odleglosci_des1)
    max_des1 = max(odleglosci_des1)

    print("Zmienianie Klucza: ")
    print(f"AES: Średnia: {srednia_aes1}, Minimalna: {min_aes1}, Maksymalna: {max_aes1}")
    print(f"DES: Średnia: {srednia_des1}, Minimalna: {min_des1}, Maksymalna: {max_des1}")

# Minimalna w DES == 0, jest spowodowana co 8-mym tzw. bitem parzystości ktory jest całkowicie ignorowany przy szyfrowaniu - (wyjasnienie gemini)
# Wyniki są poprawne ponieważ oczekiwana wartość hamminga to 50% czyli dla AES to 128 x 0.5 = 64 bity, dla DES jest to 32 bity
