import os
import time
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad

KLUCZ = os.urandom(16)
ROZMIARY_PLIKOW = [1, 10, 100]
TRYBY = {
    'ECB': AES.MODE_ECB,
    'CBC': AES.MODE_CBC,
    'OFB': AES.MODE_OFB,
    'CFB': AES.MODE_CFB,
    'CTR': AES.MODE_CTR
}

def tworzenie_plikow(nazwa_pliku: str, rozmiar_mb: int):
    print(f"Generowanie pliku {nazwa_pliku} {rozmiar_mb} MB....")
    with open(nazwa_pliku, 'wb') as f:
        f.write(os.urandom(rozmiar_mb * 1024 * 1024))

def wydajnosc():
    testowe_pliki = {}
    for rozmiar in ROZMIARY_PLIKOW:
        nazwa_pliku = f"plik_testowy_{rozmiar}MB.bin"
        if not os.path.exists(nazwa_pliku):
            tworzenie_plikow(nazwa_pliku, rozmiar)
        testowe_pliki[rozmiar] = nazwa_pliku

    print(f"Test w sekundach:\n")
    print(f"{'Rozmiar':<10} | {'Tryb':<5} | {'Czas szyfrowania':<18} | {'Czas odszyfrowania':<18}")
    print("-" * 60)

    for rozmiar, nazwa_pliku in testowe_pliki.items():
        with open(nazwa_pliku, 'rb') as f:
            jawnyTekst = f.read()

        for mode_name, mode_const in TRYBY.items():
            start_szyfr = time.perf_counter()

            if mode_name == 'ECB':
                cipher_enc = AES.new(KLUCZ, mode_const)
                szyfrowanyTekst = cipher_enc.encrypt(pad(jawnyTekst, AES.block_size))
                iv = None
            elif mode_name == 'CTR':
                cipher_enc = AES.new(KLUCZ, mode_const)
                szyfrowanyTekst = cipher_enc.encrypt(jawnyTekst)
                iv = cipher_enc.nonce
            else:
                cipher_enc = AES.new(KLUCZ, mode_const)
                if mode_name == 'CBC':
                    dane_do_szyfr = pad(jawnyTekst, AES.block_size)  # Poprawiono z mode_const
                else:
                    dane_do_szyfr = jawnyTekst

                szyfrowanyTekst = cipher_enc.encrypt(dane_do_szyfr)
                iv = cipher_enc.iv

            koniec_szyfr = time.perf_counter()
            czas_szyfr = koniec_szyfr - start_szyfr

            start_deszyfr = time.perf_counter()

            if mode_name == 'ECB':
                cipher_dec = AES.new(KLUCZ, mode_const)
                deszyfrowany_pad = cipher_dec.decrypt(szyfrowanyTekst)
                deszyfrowany = unpad(deszyfrowany_pad, AES.block_size)
            elif mode_name == 'CTR':
                cipher_dec = AES.new(KLUCZ, mode_const, nonce=iv)
                deszyfrowany = cipher_dec.decrypt(szyfrowanyTekst)  # Dodano .decrypt()
            else:
                cipher_dec = AES.new(KLUCZ, mode_const, iv=iv)
                deszyfrowane_dane = cipher_dec.decrypt(szyfrowanyTekst)

                if mode_name == 'CBC':
                    deszyfrowany = unpad(deszyfrowane_dane, AES.block_size)
                else:
                    deszyfrowany = deszyfrowane_dane

            koniec_deszyfr = time.perf_counter()
            czas_deszyfr = koniec_deszyfr - start_deszyfr

            assert jawnyTekst == deszyfrowany, f"Błąd w trybie {mode_name}"

            print(f"{rozmiar} MB{'':<5} | {mode_name:<5} | {czas_szyfr:<18.5f} | {czas_deszyfr:<18.5f}")

        print("-" * 60)  # Przeniesiono z pętli wewnętrznej i poprawiono składnię

# Przesunięto do lewej krawędzi (bez wcięć)
if __name__ == "__main__":
    wydajnosc()