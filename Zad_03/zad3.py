import os
import time
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
#pip install pycryptodomex
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
                    dane_do_szyfr = pad(jawnyTekst, AES.block_size)
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
                deszyfrowany = cipher_dec.decrypt(szyfrowanyTekst)
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

        print("-" * 60)

jawnyTekst = b'A' * 16 + b'B' * 16 + b'C' * 16 + b'D' * 16

#2

def analiza_propagacji_bledow():
    for nazwa_trybu, stala_trybu in TRYBY.items():
        if nazwa_trybu == 'ECB':
            szyfrowanie = AES.new(KLUCZ, stala_trybu)
            iv = None
        elif nazwa_trybu == 'CTR':
            szyfrowanie = AES.new(KLUCZ, stala_trybu)
            iv = szyfrowanie.nonce
        else:
            szyfrowanie = AES.new(KLUCZ, stala_trybu)
            iv = szyfrowanie.iv

        szyfrogram = bytearray(szyfrowanie.encrypt(jawnyTekst))

        szyfrogram[0] ^= 1 #Stworzenie błędu - odwrocenie pierwszego bitu

        if nazwa_trybu == 'ECB':
            szyfrowanie = AES.new(KLUCZ, stala_trybu)
        elif nazwa_trybu == 'CTR':
            szyfrowanie = AES.new(KLUCZ, stala_trybu, nonce=iv)
        else:
            szyfrowanie = AES.new(KLUCZ, stala_trybu, iv=iv)

        odszyfrowany = szyfrowanie.decrypt(bytes(szyfrogram))

        print(f"--- Tryb {nazwa_trybu} ---")
        for i in range(4):
            blok_oryginalny = jawnyTekst[i*16:(i+1)*16]
            blok_odszyfrowany = odszyfrowany[i*16:(i+1)*16]

            if blok_oryginalny == blok_odszyfrowany:
                wynik = "Nienaruszony"
            else:
                zmienione_bity = sum((b1 ^ b2).bit_count() for b1, b2 in zip(blok_oryginalny, blok_odszyfrowany))
                wynik = f"Zmienione {zmienione_bity} bity"
            print(f"Blok {i+1}: {wynik}")

#3
def xor_bytes(b1: bytes, b2: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(b1, b2))

def cbc_szyfruj(klucz: bytes, iv: bytes, tekst_jawny: bytes) -> bytes:
    """Szyfruje dane w trybie CBC używając wyłącznie trybu ECB."""
    szyfrator_ecb = AES.new(klucz, AES.MODE_ECB)

    # CBC wymaga pełnych 16-bajtowych bloków
    dane_z_paddingiem = pad(tekst_jawny, 16)
    szyfrogram = b''
    poprzedni_blok_szyfrogramu = iv

    # Szyfrujemy blok po bloku (krok po kroku)
    for i in range(0, len(dane_z_paddingiem), 16):
        blok_jawny = dane_z_paddingiem[i:i + 16]

        # Wzór CBC: C_i = E(P_i XOR C_{i-1})
        blok_po_xor = xor_bytes(blok_jawny, poprzedni_blok_szyfrogramu)
        zaszyfrowany_blok = szyfrator_ecb.encrypt(blok_po_xor)

        szyfrogram += zaszyfrowany_blok
        poprzedni_blok_szyfrogramu = zaszyfrowany_blok

    return szyfrogram


def cbc_odszyfruj(klucz: bytes, iv: bytes, szyfrogram: bytes) -> bytes:
    """Odszyfrowuje dane w trybie CBC używając wyłącznie trybu ECB."""
    deszyfrator_ecb = AES.new(klucz, AES.MODE_ECB)

    odszyfrowane_dane = b''
    poprzedni_blok_szyfrogramu = iv

    for i in range(0, len(szyfrogram), 16):
        blok_szyfrogramu = szyfrogram[i:i + 16]

        # Wzór CBC: P_i = D(C_i) XOR C_{i-1}
        odszyfrowany_ecb = deszyfrator_ecb.decrypt(blok_szyfrogramu)
        blok_jawny = xor_bytes(odszyfrowany_ecb, poprzedni_blok_szyfrogramu)

        odszyfrowane_dane += blok_jawny
        poprzedni_blok_szyfrogramu = blok_szyfrogramu

    return unpad(odszyfrowane_dane, 16)


# 2. IMPLEMENTACJA TRYBU CTR

def ctr_szyfruj_odszyfruj(klucz: bytes, nonce: bytes, dane: bytes) -> bytes:
    """
    Szyfruje i odszyfrowuje dane w trybie CTR używając wyłącznie ECB.
    W trybie CTR szyfrowanie i odszyfrowywanie to ta sama operacja matematyczna
    """
    szyfrator_ecb = AES.new(klucz, AES.MODE_ECB)

    wynik = b''
    licznik = 0

    # CTR nie wymaga paddingu, przetwarza tyle bajtów ile otrzyma
    for i in range(0, len(dane), 16):
        blok_danych = dane[i:i + 16]

        # Budujemy 16-bajtowy wektor: 8 bajtów Nonce + 8 bajtów Licznika
        licznik_bajty = licznik.to_bytes(8, byteorder='big')
        wektor_licznikowy = nonce + licznik_bajty

        # Generujemy fragment strumienia klucza
        strumien_klucza = szyfrator_ecb.encrypt(wektor_licznikowy)

        # XORujemy dane ze strumieniem klucza (tylko tyle bajtów, ile ma obecny blok)
        wynik += xor_bytes(blok_danych, strumien_klucza[:len(blok_danych)])

        licznik += 1

    return wynik
if __name__ == "__main__":
    wydajnosc()
    analiza_propagacji_bledow()

# Wnioski - Najszybsze są ECB i CTR, CBC jest szybsze przy odszyfrowywaniu, najwolniejsze jest CFB,
# Skrypt działa poprawnie ponieważ czas rośnie proporcjonalnie do rozmiaru pliku (x10)

    klucz_testowy = os.urandom(16)
    tekst_testowy = b"Bardzo tajna wiadomosc do zaszyfrowania! 123456"

    # 1. Test CBC
    iv_cbc = os.urandom(16)
    moj_szyfrogram_cbc = cbc_szyfruj(klucz_testowy, iv_cbc, tekst_testowy)
    moj_odszyfrowany_cbc = cbc_odszyfruj(klucz_testowy, iv_cbc, moj_szyfrogram_cbc)
    print("\nCzy własne CBC odszyfrowało poprawnie?:", moj_odszyfrowany_cbc == tekst_testowy)

    # 2. Test CTR
    nonce_ctr = os.urandom(8)  # Używamy 8-bajtowego nonce dla naszego CTR
    moj_szyfrogram_ctr = ctr_szyfruj_odszyfruj(klucz_testowy, nonce_ctr, tekst_testowy)
    moj_odszyfrowany_ctr = ctr_szyfruj_odszyfruj(klucz_testowy, nonce_ctr, moj_szyfrogram_ctr)
    print("Czy własne CTR odszyfrowało poprawnie?:", moj_odszyfrowany_ctr == tekst_testowy)