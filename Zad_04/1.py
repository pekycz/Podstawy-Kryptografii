import hashlib
import time

wiadomosci = ["A" * dlugosc for dlugosc in (11, 100, 1000, 10000, 100000)]
metody = [
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
]
wybrana_metoda = "sha256"


def porownaj_czasy():
    for wiadomosc in wiadomosci:
        dane = wiadomosc.encode("utf-8")
        powtorzenia = max(1, 100000 // len(dane))
        print(f"\nDługość wiadomości: {len(dane)} bajtów")
        for metoda in metody:
            poczatek = time.perf_counter()
            for _ in range(powtorzenia):
                skrot = hashlib.new(metoda, dane).hexdigest()
            czas = time.perf_counter() - poczatek
            print(
                f"{metoda:9} {skrot}  "
                f"{czas * 1000:.3f} ms  "
                f"({czas * 1000000 / powtorzenia:.3f} µs na obliczenie)"
            )


def sprawdz_sac():
    liczba_prob = 100
    dlugosc = 32  # 32 bajty = 256 bitów wejścia
    licznik_zmienionych_bitow = [0] * (
        hashlib.new(wybrana_metoda).digest_size * 8
    )

    # Dla każdego bitu wejścia sprawdzamy, jak często zmienia się każdy bit skrótu.
    for numer_proby in range(liczba_prob):
        dane = bytes((indeks + numer_proby) % 256 for indeks in range(dlugosc))
        skrot = hashlib.new(wybrana_metoda, dane).digest()

        for bit_wejscia in range(dlugosc * 8):
            zmienione_dane = bytearray(dane)
            zmienione_dane[bit_wejscia // 8] ^= 1 << (bit_wejscia % 8)
            nowy_skrot = hashlib.new(wybrana_metoda, zmienione_dane).digest()

            for bit_wyjscia in range(len(licznik_zmienionych_bitow)):
                if (skrot[bit_wyjscia // 8] ^ nowy_skrot[bit_wyjscia // 8]) & (
                    1 << (bit_wyjscia % 8)
                ):
                    licznik_zmienionych_bitow[bit_wyjscia] += 1


    # liczba prób oznacza, że wynik jest przybliżeniem, a nie dowodem.
    procenty = [
        licznik / (liczba_prob * dlugosc * 8) * 100
        for licznik in licznik_zmienionych_bitow
    ]
    print(f"\nSAC dla {wybrana_metoda} ({liczba_prob} prób):")
    print(
        f"Średnia zmiana bitów wyjścia: "
        f"{sum(procenty) / len(procenty):.2f}% (oczekiwane - 50%)"
    )
    print(f"Zakres dla bitów wyjścia: {min(procenty):.2f}%–{max(procenty):.2f}%")


def znajdz_kolizje(liczba_bitow):
    znalezione_skroty = {}
    poczatek = time.perf_counter()
    proba = 0

    while True:
        wiadomosc = f"Wiadomosc-{proba}".encode("utf-8")
        pelny_skrot = hashlib.new(wybrana_metoda, wiadomosc).digest()
        skrot_czesciowy = pelny_skrot[:liczba_bitow // 8]

        # Różne wiadomości z takim samym początkiem skrótu tworzą częściową kolizję.
        if skrot_czesciowy in znalezione_skroty:
            czas = time.perf_counter() - poczatek
            print(f"\nKolizja pierwszych {liczba_bitow} bitów ({wybrana_metoda}):")
            print(f"Próby: {proba + 1}, czas: {czas:.3f} s")
            print(f"Wiadomość 1: {znalezione_skroty[skrot_czesciowy].decode('utf-8')}")
            print(f"Wiadomość 2: {wiadomosc.decode('utf-8')}")
            print(f"Wspólny początek skrótu: {skrot_czesciowy.hex()}")
            print(f"Oczekiwana liczba prób (paradoks urodzin): około 2^{liczba_bitow // 2}")
            return

        znalezione_skroty[skrot_czesciowy] = wiadomosc
        proba += 1


if __name__ == "__main__":
    porownaj_czasy()
    sprawdz_sac()
    for liczba_bitow in (8, 16, 32):
        znajdz_kolizje(liczba_bitow)
