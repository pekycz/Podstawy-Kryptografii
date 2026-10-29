import hashlib
import math
import secrets


ROZMIAR_BITOW_LICZBY_PIERWSZEJ = 1024
LICZBA_RUND_MILLERA_RABINA = 40
WYKLADNIK_PUBLICZNY = 65537


def czy_prawdopodobnie_pierwsza(liczba: int) -> bool:
    """Sprawdza pierwszość liczby testem Millera-Rabina."""
    male_liczby_pierwsze = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    if liczba < 2:
        return False
    if liczba in male_liczby_pierwsze:
        return True
    if any(liczba % dzielnik == 0 for dzielnik in male_liczby_pierwsze):
        return False

    # Rozkładamy liczba - 1 na 2^s * d, gdzie d jest nieparzyste.
    d = liczba - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    # Losowe podstawy ograniczają prawdopodobieństwo błędnego wyniku testu.
    for _ in range(LICZBA_RUND_MILLERA_RABINA):
        podstawa = secrets.randbelow(liczba - 3) + 2
        wynik = pow(podstawa, d, liczba)
        if wynik in (1, liczba - 1):
            continue

        for _ in range(s - 1):
            wynik = pow(wynik, 2, liczba)
            if wynik == liczba - 1:
                break
        else:
            return False

    return True


def generuj_liczbe_pierwsza(liczba_bitow: int) -> int:
    """Generuje nieparzystą liczbę pierwszą o zadanej długości bitowej."""
    if liczba_bitow < 2:
        raise ValueError("Liczba bitów musi wynosić co najmniej 2.")

    while True:
        kandydat = secrets.randbits(liczba_bitow)
        kandydat |= (1 << (liczba_bitow - 1)) | 1
        if czy_prawdopodobnie_pierwsza(kandydat):
            return kandydat


def generuj_klucze() -> tuple[tuple[int, int], tuple[int, int]]:
    """Zwraca klucz publiczny (N, e) i prywatny (N, d)."""
    while True:
        p = generuj_liczbe_pierwsza(ROZMIAR_BITOW_LICZBY_PIERWSZEJ)
        q = generuj_liczbe_pierwsza(ROZMIAR_BITOW_LICZBY_PIERWSZEJ)
        if p == q:
            continue

        n = p * q
        if n.bit_length() != 2 * ROZMIAR_BITOW_LICZBY_PIERWSZEJ:
            continue

        funkcja_eulera = (p - 1) * (q - 1)
        e = WYKLADNIK_PUBLICZNY
        if math.gcd(e, funkcja_eulera) == 1:
            d = pow(e, -1, funkcja_eulera)
            return (n, e), (n, d)


def podpisz_wiadomosc(
    wiadomosc: int, klucz_prywatny: tuple[int, int]
) -> int:
    """Tworzy naiwny podpis RSA dla liczby z zakresu od 0 do N - 1."""
    n, d = klucz_prywatny
    if not 0 <= wiadomosc < n:
        raise ValueError("Wiadomość musi spełniać warunek 0 <= M < N.")
    return pow(wiadomosc, d, n)


def weryfikuj_podpis(
    podpis: int, wiadomosc: int, klucz_publiczny: tuple[int, int]
) -> bool:
    """Sprawdza, czy podpis RSA odpowiada podanej wiadomości."""
    n, e = klucz_publiczny
    if not 0 <= podpis < n or not 0 <= wiadomosc < n:
        return False
    return pow(podpis, e, n) == wiadomosc


def oblicz_skrot(wiadomosc: bytes) -> int:
    """Zamienia skrót SHA-256 wiadomości na liczbę całkowitą."""
    return int.from_bytes(hashlib.sha256(wiadomosc).digest(), "big")


def podpisz_skrot(
    wiadomosc: bytes, klucz_prywatny: tuple[int, int]
) -> int:
    """Podpisuje skrót SHA-256 wiadomości zamiast jej surowej wartości."""
    return podpisz_wiadomosc(oblicz_skrot(wiadomosc), klucz_prywatny)


def weryfikuj_skrot(
    podpis: int, wiadomosc: bytes, klucz_publiczny: tuple[int, int]
) -> bool:
    """Porównuje skrót wiadomości ze skrótem odzyskanym z podpisu."""
    return weryfikuj_podpis(podpis, oblicz_skrot(wiadomosc), klucz_publiczny)


def pokaz_naiwny_podpis(
    klucz_publiczny: tuple[int, int], klucz_prywatny: tuple[int, int]
) -> None:
    """Pokazuje podpis i weryfikację zwykłej wiadomości."""
    wiadomosc = "Ala ma kota".encode("utf-8")
    liczba_wiadomosci = int.from_bytes(wiadomosc, "big")
    podpis = podpisz_wiadomosc(liczba_wiadomosci, klucz_prywatny)

    print("1. Naiwny podpis cyfrowy RSA")
    print(f"Wiadomość: {wiadomosc.decode('utf-8')}")
    print(f"Podpis: {podpis:x}")
    print(
        "Podpis jest poprawny: "
        f"{weryfikuj_podpis(podpis, liczba_wiadomosci, klucz_publiczny)}"
    )


def pokaz_falszerstwo_egzystencjalne(
    klucz_publiczny: tuple[int, int],
) -> None:
    """Tworzy poprawną parę wiadomość-podpis bez klucza prywatnego."""
    n, e = klucz_publiczny
    falszywy_podpis = secrets.randbelow(n - 1) + 1

    # Wybieramy podpis, a odpowiadającą mu wiadomość wyliczamy kluczem publicznym.
    falszywa_wiadomosc = pow(falszywy_podpis, e, n)
    poprawny = weryfikuj_podpis(
        falszywy_podpis, falszywa_wiadomosc, klucz_publiczny
    )

    print("\n2. Fałszerstwo egzystencjalne")
    print(f"Wybrany podpis: {falszywy_podpis:x}")
    print(f"Pasująca wiadomość (liczba): {falszywa_wiadomosc}")
    print(f"Para przechodzi weryfikację: {poprawny}")


def pokaz_podatnosc_homomorficzna(
    klucz_publiczny: tuple[int, int], klucz_prywatny: tuple[int, int]
) -> None:
    """Pokazuje, że iloczyn podpisów naiwnych jest podpisem iloczynu."""
    n, _ = klucz_publiczny
    wiadomosc_1 = 2
    wiadomosc_2 = 3
    podpis_1 = podpisz_wiadomosc(wiadomosc_1, klucz_prywatny)
    podpis_2 = podpisz_wiadomosc(wiadomosc_2, klucz_prywatny)

    # Mnożymy podpisy i wiadomości modulo N, nie używając klucza prywatnego.
    falszywy_podpis = (podpis_1 * podpis_2) % n
    falszywa_wiadomosc = (wiadomosc_1 * wiadomosc_2) % n
    poprawny = weryfikuj_podpis(
        falszywy_podpis, falszywa_wiadomosc, klucz_publiczny
    )

    print("\n3. Podatność homomorficzna")
    print(f"Wiadomości: {wiadomosc_1} i {wiadomosc_2}")
    print(f"Iloczyn wiadomości modulo N: {falszywa_wiadomosc}")
    print(f"Podpis iloczynu przechodzi weryfikację: {poprawny}")


def pokaz_podpisywanie_skrotu(
    klucz_publiczny: tuple[int, int], klucz_prywatny: tuple[int, int]
) -> None:
    """Pokazuje podpisywanie skrótu i ponawia próbę ataku homomorficznego."""
    wiadomosc_1 = b"Pierwsza wiadomosc"
    wiadomosc_2 = b"Druga wiadomosc"
    wiadomosc_3 = b"Iloczyn pierwszej i drugiej wiadomosci"

    podpis_1 = podpisz_skrot(wiadomosc_1, klucz_prywatny)
    podpis_2 = podpisz_skrot(wiadomosc_2, klucz_prywatny)
    n, _ = klucz_publiczny

    # Próba łączenia podpisów nie daje podpisu skrótu wiadomości wynikowej.
    falszywy_podpis = (podpis_1 * podpis_2) % n
    poprawny = weryfikuj_skrot(
        falszywy_podpis, wiadomosc_3, klucz_publiczny
    )
    podpis_prawidlowy = podpisz_skrot(wiadomosc_3, klucz_prywatny)

    print("\n4. Podpisywanie skrótu SHA-256")
    print(
        "Podpis wiadomości przechodzi weryfikację: "
        f"{weryfikuj_skrot(podpis_prawidlowy, wiadomosc_3, klucz_publiczny)}"
    )
    print(
        "Połączony podpis przechodzi weryfikację dla nowej wiadomości: "
        f"{poprawny}"
    )


def main() -> None:
    klucz_publiczny, klucz_prywatny = generuj_klucze()
    n, e = klucz_publiczny

    print("Laboratorium 7 — podpisy cyfrowe RSA")
    print(f"Długość modułu N: {n.bit_length()} bitów")
    print(f"Wykładnik publiczny e: {e}")
    pokaz_naiwny_podpis(klucz_publiczny, klucz_prywatny)
    pokaz_falszerstwo_egzystencjalne(klucz_publiczny)
    pokaz_podatnosc_homomorficzna(klucz_publiczny, klucz_prywatny)
    pokaz_podpisywanie_skrotu(klucz_publiczny, klucz_prywatny)

    print(
        "\nUwaga: to edukacyjna demonstracja surowego RSA, "
        "a nie implementacja do zastosowań produkcyjnych."
    )


if __name__ == "__main__":
    main()
